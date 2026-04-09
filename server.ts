import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';
import { parse } from 'node-html-parser';

process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0'; // Traefik self-signed chain

// ─── Config ───────────────────────────────────────────────────────────────────
const MINIMAX_API_KEY    = process.env.MINIMAX_API_KEY;
const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;

if (!MINIMAX_API_KEY && !OPENROUTER_API_KEY) {
  console.error('Warning: No AI API key set (MINIMAX_API_KEY or OPENROUTER_API_KEY).');
}

// S3 — always use external Traefik URL (works from any isolated container)
const S3_ENDPOINT   = process.env.S3_ENDPOINT   || 'https://s3-rustfs-6bfb08-82-165-172-78.traefik.me';
const S3_ACCESS_KEY = process.env.S3_ACCESS_KEY  || 'rustfsadmin';
const S3_SECRET_KEY = process.env.S3_SECRET_KEY  || 'ecirjxhvfpuzn3ut';
const S3_BUCKET     = process.env.S3_BUCKET      || 'silviyaaeterna';

const INDEX_FILE = 'index.html';

// ─── Deep reasoning prompts ───────────────────────────────────────────────────
const SYSTEM_FULL_PAGE = `You are a world-class Frontend Web Developer and UI/UX Designer with 15+ years of experience building award-winning, pixel-perfect websites.

THINKING PROCESS — Before writing any code, you must silently reason through:
1. What is the user's INTENT? What visual/functional change are they actually requesting?
2. Which exact HTML sections need to change to satisfy that intent? List them mentally.
3. What should NOT change? Identify structural sections, IDs, class names, and scripts that must be preserved.
4. What design improvements can you make WITHIN the scope — better typography, spacing, micro-animations, color depth?
5. Will your change break any existing JavaScript behaviour? Audit thoroughly.

EXECUTION RULES:
- Return ONLY the complete updated HTML starting with <!DOCTYPE html>. No markdown, no explanation.
- Every section you touch must be MORE detailed, richer, and higher quality than before.
- Use premium design patterns: glassmorphism, layered gradients, smooth transitions (0.3s ease), CSS custom properties.
- Typography: use existing Google Font stacks; never introduce new external dependencies.
- Only generate production-ready HTML — no TODO comments, no placeholder text.
- Preserve ALL existing IDs, data- attributes, and JavaScript hooks exactly.
- DO NOT add or remove any <script> tag that was not in the original unless explicitly asked.`;

const SYSTEM_TARGETED = `You are a world-class Frontend Web Developer performing a precise surgical edit on a single HTML element.

THINKING PROCESS — Before writing anything, reason through:
1. What is the exact change the user is requesting on THIS element?
2. What CSS classes, inline styles, IDs, and event handlers must be preserved exactly?
3. What child elements must stay structurally intact?
4. How can you make this element visually BETTER while satisfying the user request?
5. Does this element have any JavaScript bindings that must be kept?

EXECUTION RULES:
- Return ONLY the modified HTML for this ONE element. No surrounding context, no markdown.
- The output must be a drop-in replacement — same root tag, same ID/class structure.
- Make the element more detailed and visually rich than the original within the user's request scope.
- Premium styling: gradients, shadows, transitions, refined spacing and typography.
- Never remove or rename existing IDs or classes.
- Never add external CSS/JS links.`;

const SYSTEM_CHUNK = `You are a world-class Frontend Web Developer performing a precise targeted edit on one layout section of a webpage.

THINKING PROCESS — Before writing code, reason through:
1. What is the user requesting for THIS specific section?
2. Which child elements need to change, and which must stay identical?
3. What visual improvements can be made WITHIN the requested change scope?
4. Are there any IDs, classes, or JS hooks in this section that must be preserved?

EXECUTION RULES:
- Return ONLY the modified HTML for this exact section block. Drop-in replacement.
- No markdown, no explanation, no surrounding context.
- Richer detail: more semantic HTML, better spacing, premium transitions.
- Preserve all existing IDs, class names, data attributes, and event handler references.
- Use existing styling conventions (TailwindCSS for krusil-webpage).`;

// ─── AI call — OpenRouter first, Minimax fallback ─────────────────────────────
async function callAI(systemPrompt: string, userPrompt: string, maxTokens = 32000): Promise<ReadableStream<Uint8Array>> {
  // Try OpenRouter z-ai/glm-5.1 first
  if (OPENROUTER_API_KEY) {
    console.log('Calling OpenRouter z-ai/glm-5.1...');
    const res = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
        'HTTP-Referer': 'https://silviyaaeterna.com',
        'X-Title': 'AI Web Inspector',
      },
      body: JSON.stringify({
        model: 'z-ai/glm-5.1',
        messages: [{ role: 'system', content: systemPrompt }, { role: 'user', content: userPrompt }],
        stream: true,
        temperature: 0.7,
        max_tokens: maxTokens,
      })
    });
    if (res.ok) return res.body!;
    const err = await res.text();
    console.error(`OpenRouter failed [${res.status}]: ${err} — falling back to Minimax`);
  }

  // Fallback: Minimax M2.7
  if (!MINIMAX_API_KEY) throw new Error('No AI API key available.');
  console.log('Calling Minimax M2.7 (fallback)...');
  const res = await fetch('https://api.minimax.io/v1/chat/completions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${MINIMAX_API_KEY}` },
    body: JSON.stringify({
      model: 'MiniMax-M2.7',
      messages: [{ role: 'system', content: systemPrompt }, { role: 'user', content: userPrompt }],
      stream: true,
    })
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Minimax also failed [${res.status}]: ${err}`);
  }
  return res.body!;
}

// ─── Stream SSE to accumulated string ─────────────────────────────────────────
async function streamToString(stream: ReadableStream<Uint8Array>, onChunk?: (c: string) => void): Promise<string> {
  const reader  = stream.getReader();
  const decoder = new TextDecoder();
  let acc    = '';
  let buffer = '';
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() ?? '';
    for (const line of lines) {
      if (!line.startsWith('data: ') || line.includes('[DONE]')) continue;
      if (line.startsWith(': ')) continue; // OpenRouter keep-alive comment
      try {
        const data = JSON.parse(line.slice(6));
        // Check for mid-stream error (OpenRouter spec)
        if (data.error) { console.error('Mid-stream error:', data.error); continue; }
        const content = data.choices?.[0]?.delta?.content;
        if (content) { acc += content; onChunk?.(content); }
      } catch(_) {}
    }
  }
  return acc;
}

// ─── Clean AI output ──────────────────────────────────────────────────────────
function cleanHtml(raw: string): string {
  let h = raw.trim();
  h = h.replace(/<think>[\s\S]*?<\/think>/gi, '').trim();
  const md = h.match(/```(?:html)?\s*([\s\S]*?)```/);
  if (md) return md[1].trim();
  const ft = h.indexOf('<');
  if (ft !== -1) return h.substring(ft).trim();
  return h;
}

// ─── Selector-based DOM patching ──────────────────────────────────────────────
function patchBySelector(html: string, selector: string, replacement: string): string | null {
  try {
    const root = parse(html, { comment: true, blockTextElements: { script: true, style: true, pre: true } });
    const el = root.querySelector(selector);
    if (!el) { console.warn(`patchBySelector: no element found for "${selector}"`); return null; }
    el.replaceWith(replacement);
    return root.toString();
  } catch (e) {
    console.error('patchBySelector error:', e);
    return null;
  }
}

// ─── AWS Signature v4 (no external deps) ─────────────────────────────────────
async function hmac(key: BufferSource | string, data: string): Promise<ArrayBuffer> {
  const keyData = typeof key === 'string' ? new TextEncoder().encode(key) : key;
  const k = await crypto.subtle.importKey('raw', keyData, { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  return crypto.subtle.sign('HMAC', k, new TextEncoder().encode(data));
}
function toHex(buf: ArrayBuffer) {
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
}
async function sha256Hex(data: string | ArrayBuffer): Promise<string> {
  const buf = typeof data === 'string' ? new TextEncoder().encode(data) : data;
  return toHex(await crypto.subtle.digest('SHA-256', buf));
}

async function s3Fetch(method: string, objectKey: string, body?: Uint8Array | null, contentType?: string): Promise<Response> {
  const endpoint = S3_ENDPOINT.replace(/\/$/, '');
  const urlStr   = `${endpoint}/${S3_BUCKET}/${objectKey}`;
  const urlObj   = new URL(urlStr);
  const now       = new Date();
  const amzDate   = now.toISOString().replace(/[:\-]|\.\d{3}/g, '').slice(0, 15) + 'Z';
  const dateStamp = amzDate.slice(0, 8);
  const payload   = body ?? new Uint8Array(0);
  const payloadHash = await sha256Hex(payload.buffer ?? payload);
  const ct = contentType ?? (body ? 'text/html; charset=utf-8' : 'application/octet-stream');
  const headers: Record<string, string> = {
    'host': urlObj.host, 'x-amz-date': amzDate, 'x-amz-content-sha256': payloadHash,
    ...(body ? { 'content-type': ct } : {}),
  };
  const sl = Object.keys(headers).sort();
  const ch = sl.map(h => `${h}:${headers[h]}`).join('\n') + '\n';
  const ss = sl.join(';');
  const cr = [method, `/${S3_BUCKET}/${objectKey}`, '', ch, ss, payloadHash].join('\n');
  const cs = `${dateStamp}/us-east-1/s3/aws4_request`;
  const sts = ['AWS4-HMAC-SHA256', amzDate, cs, await sha256Hex(cr)].join('\n');
  let sk: ArrayBuffer = await hmac('AWS4' + S3_SECRET_KEY, dateStamp);
  sk = await hmac(sk, 'us-east-1'); sk = await hmac(sk, 's3'); sk = await hmac(sk, 'aws4_request');
  const sig = toHex(await hmac(sk, sts));
  return fetch(urlStr, { method, headers: { ...headers, Authorization: `AWS4-HMAC-SHA256 Credential=${S3_ACCESS_KEY}/${cs}, SignedHeaders=${ss}, Signature=${sig}` }, body: body ?? undefined });
}

async function ensureBucket() {
  try {
    const res = await s3Fetch('HEAD', '');
    if (res.status === 404 || res.status === 403) {
      const endpoint = S3_ENDPOINT.replace(/\/$/, '');
      const urlStr = `${endpoint}/${S3_BUCKET}`; const urlObj = new URL(urlStr);
      const now = new Date();
      const amzDate = now.toISOString().replace(/[:\-]|\.\d{3}/g, '').slice(0, 15) + 'Z';
      const dateStamp = amzDate.slice(0, 8); const ph = await sha256Hex('');
      const headers: Record<string, string> = { 'host': urlObj.host, 'x-amz-date': amzDate, 'x-amz-content-sha256': ph };
      const sl = Object.keys(headers).sort(); const ch = sl.map(h => `${h}:${headers[h]}`).join('\n') + '\n'; const ss = sl.join(';');
      const cr = ['PUT', `/${S3_BUCKET}`, '', ch, ss, ph].join('\n'); const cs = `${dateStamp}/us-east-1/s3/aws4_request`;
      const sts = ['AWS4-HMAC-SHA256', amzDate, cs, await sha256Hex(cr)].join('\n');
      let sk: ArrayBuffer = await hmac('AWS4' + S3_SECRET_KEY, dateStamp);
      sk = await hmac(sk, 'us-east-1'); sk = await hmac(sk, 's3'); sk = await hmac(sk, 'aws4_request');
      const sig = toHex(await hmac(sk, sts));
      await fetch(urlStr, { method: 'PUT', headers: { ...headers, Authorization: `AWS4-HMAC-SHA256 Credential=${S3_ACCESS_KEY}/${cs}, SignedHeaders=${ss}, Signature=${sig}` } });
      console.log(`✅ S3 bucket "${S3_BUCKET}" created.`);
    } else { console.log(`✅ S3 bucket "${S3_BUCKET}" accessible.`); }
  } catch(e) { console.error('S3 bucket check failed:', e); }
}

async function s3SaveSnapshot(html: string): Promise<string> {
  const ts  = Math.floor(Date.now() / 1000);
  const key = `history/${INDEX_FILE.replace('.html', '')}_${ts}.html`;
  const buf = new TextEncoder().encode(html);
  const res = await s3Fetch('PUT', key, buf, 'text/html; charset=utf-8');
  if (!res.ok) throw new Error(`S3 PUT failed [${res.status}]: ${await res.text()}`);
  console.log(`💾 S3 snapshot: ${key}`);
  return key;
}

async function s3ListVersions(): Promise<string[]> {
  const prefix = `history/${INDEX_FILE.replace('.html', '')}_`;
  const query  = `list-type=2&prefix=${encodeURIComponent(prefix)}`;
  const endpoint = S3_ENDPOINT.replace(/\/$/, '');
  const urlObj = new URL(`${endpoint}/${S3_BUCKET}?${query}`);
  const now = new Date();
  const amzDate = now.toISOString().replace(/[:\-]|\.\d{3}/g, '').slice(0, 15) + 'Z';
  const dateStamp = amzDate.slice(0, 8); const ph = await sha256Hex('');
  const headers: Record<string, string> = { 'host': urlObj.host, 'x-amz-date': amzDate, 'x-amz-content-sha256': ph };
  const sl = Object.keys(headers).sort(); const ch = sl.map(h => `${h}:${headers[h]}`).join('\n') + '\n'; const ss = sl.join(';');
  const cr = ['GET', `/${S3_BUCKET}`, query, ch, ss, ph].join('\n'); const cs = `${dateStamp}/us-east-1/s3/aws4_request`;
  const sts = ['AWS4-HMAC-SHA256', amzDate, cs, await sha256Hex(cr)].join('\n');
  let sk: ArrayBuffer = await hmac('AWS4' + S3_SECRET_KEY, dateStamp);
  sk = await hmac(sk, 'us-east-1'); sk = await hmac(sk, 's3'); sk = await hmac(sk, 'aws4_request');
  const sig = toHex(await hmac(sk, sts));
  const res = await fetch(urlObj.toString(), { headers: { ...headers, Authorization: `AWS4-HMAC-SHA256 Credential=${S3_ACCESS_KEY}/${cs}, SignedHeaders=${ss}, Signature=${sig}` } });
  const text = await res.text();
  return [...text.matchAll(/<Key>([^<]+)<\/Key>/g)].map(m => m[1]).sort();
}

async function s3GetVersion(key: string): Promise<string> {
  const res = await s3Fetch('GET', key);
  if (!res.ok) throw new Error(`S3 GET failed [${res.status}]`);
  return res.text();
}

async function s3DeleteVersion(key: string) {
  const res = await s3Fetch('DELETE', key);
  if (!res.ok) console.error(`S3 DELETE failed for ${key}: ${res.status}`);
}

function autoCommit(message: string) {
  exec(`git add ${INDEX_FILE} && git commit -m "${message}"`, { cwd: process.cwd() }, (err, stdout, stderr) => {
    if (err && !stdout.includes('nothing to commit') && !stderr.includes('nothing to commit')) {
      console.error('Git commit error:', stderr || err.message);
    } else { console.log(`✅ Git: "${message}"`); }
  });
}

async function snapshotAndCommit(message: string) {
  const html = fs.readFileSync(path.join(process.cwd(), INDEX_FILE), 'utf-8');
  try { await s3SaveSnapshot(html); } catch(e) { console.error('S3 snapshot error:', e); }
  autoCommit(message);
}

// ─── Bootstrap ────────────────────────────────────────────────────────────────
await ensureBucket();

// ─── Server ───────────────────────────────────────────────────────────────────
Bun.serve({
  port: process.env.PORT || 3000,
  async fetch(req) {
    const url = new URL(req.url);

    // Rollback
    if (url.pathname === '/api/rollback' && req.method === 'POST') {
      try {
        const versions = await s3ListVersions();
        if (versions.length < 2) return new Response(JSON.stringify({ success: false, error: 'Not enough history to rollback' }), { status: 400, headers: { 'Content-Type': 'application/json' } });
        const newest = versions[versions.length - 1];
        const target = versions[versions.length - 2];
        const html   = await s3GetVersion(target);
        fs.writeFileSync(path.join(process.cwd(), INDEX_FILE), html, 'utf-8');
        await s3DeleteVersion(newest);
        autoCommit(`AI Update ⏪ Rollback to ${target}`);
        return new Response(JSON.stringify({ success: true, versionsLeft: versions.length - 2 }), { headers: { 'Content-Type': 'application/json' } });
      } catch(e: any) {
        return new Response(JSON.stringify({ success: false, error: e.message }), { status: 500, headers: { 'Content-Type': 'application/json' } });
      }
    }

    // AI Generate
    if (url.pathname === '/api/generate' && req.method === 'POST') {
      try {
        const body = await req.json();
        const { prompt, targetHtml, chunks, targetSelector } = body;
        if (!prompt) return new Response(JSON.stringify({ error: 'Prompt is required' }), { status: 400 });

        const indexPath  = path.join(process.cwd(), INDEX_FILE);
        let currentHtml  = '';
        try { currentHtml = fs.readFileSync(indexPath, 'utf-8'); }
        catch(e) { return new Response(JSON.stringify({ error: `Could not read ${INDEX_FILE}` }), { status: 500 }); }

        // ── Chunk / cluster mode ───────────────────────────────────────────────
        if (chunks && chunks.length > 0) {
          console.log(`AI cluster mode: ${chunks.length} chunks...`);
          return new Response(new ReadableStream({
            async start(controller) {
              const enc = (s: string) => controller.enqueue(new TextEncoder().encode(s));
              try {
                let totalApplied = 0;
                for (let i = 0; i < chunks.length; i += 3) {
                  const batch = chunks.slice(i, i + 3);
                  const results = await Promise.all(batch.map(async (chunk: string, bi: number) => {
                    const gi = i + bi;
                    const userMsg = `TARGET SECTION (${gi+1}/${chunks.length}):\n${chunk}\n\nUSER REQUEST: ${prompt}`;
                    const stream = await callAI(SYSTEM_CHUNK, userMsg);
                    const acc = await streamToString(stream, c => enc(c));
                    return { chunk, gi, acc };
                  }));

                  let liveHtml = fs.readFileSync(indexPath, 'utf-8'); let changed = false;
                  for (const r of results) {
                    const fh = cleanHtml(r.acc);
                    if (!fh) continue;
                    const nh = liveHtml.replace(r.chunk, fh);
                    if (nh !== liveHtml) { liveHtml = nh; changed = true; totalApplied++; console.log(`Chunk ${r.gi+1} injected.`); }
                    else {
                      // Retry with alternate model
                      console.warn(`Chunk ${r.gi+1} string-replace missed — retrying with alt model...`);
                      try {
                        const altStream = await callAI(SYSTEM_CHUNK + '\n\nIMPORTANT: The previous attempt returned HTML that did not match the original. This time, preserve the EXACT opening and closing tags of the target section so string replacement succeeds.', `TARGET SECTION (retry ${r.gi+1}/${chunks.length}):\n${r.chunk}\n\nUSER REQUEST: ${prompt}`);
                        const altAcc = await streamToString(altStream, c => enc(c));
                        const altFh = cleanHtml(altAcc);
                        const altNh = liveHtml.replace(r.chunk, altFh);
                        if (altNh !== liveHtml) { liveHtml = altNh; changed = true; totalApplied++; console.log(`Chunk ${r.gi+1} injected on retry.`); }
                      } catch(retryErr) { console.error(`Retry chunk ${r.gi+1} failed:`, retryErr); }
                    }
                  }
                  if (changed) { fs.writeFileSync(indexPath, liveHtml, 'utf-8'); await snapshotAndCommit('AI Update: Batch chunk modifications via Inspector'); }
                }
                enc(`\n\x00PATCH_STATUS:${totalApplied > 0 ? 'ok' : 'fail'}\x00`);
                controller.close();
              } catch(e) { controller.error(e); }
            }
          }), { headers: { 'Content-Type': 'text/event-stream' } });
        }

        // ── Single / targeted mode ─────────────────────────────────────────────
        const sysP = targetHtml ? SYSTEM_TARGETED : SYSTEM_FULL_PAGE;
        const usrP = targetHtml
          ? `TARGET ELEMENT TO MODIFY:\n${targetHtml}\n\nUSER REQUEST: ${prompt}`
          : `CURRENT FULL PAGE HTML:\n${currentHtml}\n\nUSER REQUEST: ${prompt}`;

        const aiStream = await callAI(sysP, usrP, 32000);

        return new Response(new ReadableStream({
          async start(controller) {
            const enc = (s: string) => controller.enqueue(new TextEncoder().encode(s));
            try {
              const acc = await streamToString(aiStream, c => enc(c));
              let fh = cleanHtml(acc);
              let applied = false;

              if (targetHtml) {
                // Primary: selector-based DOM patch (reliable against DOM mutation)
                if (targetSelector) {
                  const patched = patchBySelector(currentHtml, targetSelector, fh);
                  if (patched) {
                    fs.writeFileSync(indexPath, patched, 'utf-8');
                    await snapshotAndCommit('AI Update: Targeted element modified via Inspector');
                    applied = true;
                  }
                }
                // Fallback: string replace if no selector or selector missed
                if (!applied) {
                  const patched = currentHtml.replace(targetHtml, fh);
                  if (patched !== currentHtml) {
                    fs.writeFileSync(indexPath, patched, 'utf-8');
                    await snapshotAndCommit('AI Update: Targeted element modified via Inspector');
                    applied = true;
                  } else {
                    console.warn('Both selector and string-replace missed — no change applied.');
                  }
                }
              } else {
                // Full page — reject truncated responses to prevent content loss
                if (fh.includes('<') && fh.includes('</html>')) {
                  fs.writeFileSync(indexPath, fh, 'utf-8');
                  await snapshotAndCommit('AI Update: Full layout redesigned via Inspector');
                  applied = true;
                } else if (fh.includes('<')) {
                  console.error('Full-page response truncated (missing </html>) — rejecting to prevent content loss.');
                }
              }

              enc(`\n\x00PATCH_STATUS:${applied ? 'ok' : 'fail'}\x00`);
              controller.close();
            } catch(err) { controller.error(err); }
          }
        }), { headers: { 'Content-Type': 'text/event-stream' } });

      } catch(error: any) {
        console.error('Error in /api/generate:', error);
        return new Response(JSON.stringify({ error: error.message }), { status: 500 });
      }
    }

    // Static file server
    let filePath = path.join(process.cwd(), url.pathname);
    if (filePath.endsWith('/')) { filePath += INDEX_FILE; }
    else { try { if (fs.statSync(filePath).isDirectory()) filePath = path.join(filePath, INDEX_FILE); } catch(_) {} }
    const file = Bun.file(filePath);
    if (await file.exists()) return new Response(file);
    return new Response('Not Found', { status: 404 });
  }
});

console.log(`✅ Server on port ${process.env.PORT || 3000} — primary: OpenRouter z-ai/glm-5.1, fallback: Minimax M2.7`);
console.log(`   S3: ${S3_BUCKET} @ ${S3_ENDPOINT}`);
