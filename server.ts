import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';

// ─── Config ───────────────────────────────────────────────────────────────────
const MINIMAX_API_KEY = process.env.MINIMAX_API_KEY;
if (!MINIMAX_API_KEY) console.error('Warning: MINIMAX_API_KEY is not set.');

// S3 — use external Traefik URL so it works from any isolated container
const S3_ENDPOINT   = process.env.S3_ENDPOINT   || 'https://s3-rustfs-6bfb08-82-165-172-78.traefik.me';
const S3_ACCESS_KEY = process.env.S3_ACCESS_KEY  || 'rustfsadmin';
const S3_SECRET_KEY = process.env.S3_SECRET_KEY  || 'ecirjxhvfpuzn3ut';
const S3_BUCKET     = process.env.S3_BUCKET      || 'silviyaaeterna';  // bucket for silviyaaeterna.com

const INDEX_FILE = 'index.html';

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
  const region    = 'us-east-1';
  const service   = 's3';

  const payload     = body ?? new Uint8Array(0);
  const payloadHash = await sha256Hex(payload.buffer ?? payload);
  const ct          = contentType ?? (body ? 'text/html; charset=utf-8' : 'application/octet-stream');

  const headers: Record<string, string> = {
    'host':                 urlObj.host,
    'x-amz-date':          amzDate,
    'x-amz-content-sha256': payloadHash,
    ...(body ? { 'content-type': ct } : {}),
  };

  const signedList    = Object.keys(headers).sort();
  const canonHeaders  = signedList.map(h => `${h}:${headers[h]}`).join('\n') + '\n';
  const signedStr     = signedList.join(';');
  const canonReq      = [method, `/${S3_BUCKET}/${objectKey}`, '', canonHeaders, signedStr, payloadHash].join('\n');
  const credScope     = `${dateStamp}/${region}/${service}/aws4_request`;
  const stringToSign  = ['AWS4-HMAC-SHA256', amzDate, credScope, await sha256Hex(canonReq)].join('\n');

  let sigKey: ArrayBuffer = await hmac('AWS4' + S3_SECRET_KEY, dateStamp);
  sigKey = await hmac(sigKey, region);
  sigKey = await hmac(sigKey, service);
  sigKey = await hmac(sigKey, 'aws4_request');
  const signature = toHex(await hmac(sigKey, stringToSign));
  const auth      = `AWS4-HMAC-SHA256 Credential=${S3_ACCESS_KEY}/${credScope}, SignedHeaders=${signedStr}, Signature=${signature}`;

  return fetch(urlStr, { method, headers: { ...headers, Authorization: auth }, body: body ?? undefined });
}

// ─── Bucket bootstrap ─────────────────────────────────────────────────────────
async function ensureBucket() {
  try {
    const res = await s3Fetch('HEAD', '');
    if (res.status === 404 || res.status === 403) {
      // Try creating bucket
      const endpoint  = S3_ENDPOINT.replace(/\/$/, '');
      const urlStr    = `${endpoint}/${S3_BUCKET}`;
      const urlObj    = new URL(urlStr);
      const now       = new Date();
      const amzDate   = now.toISOString().replace(/[:\-]|\.\d{3}/g, '').slice(0, 15) + 'Z';
      const dateStamp = amzDate.slice(0, 8);
      const ph        = await sha256Hex('');
      const headers: Record<string, string> = { 'host': urlObj.host, 'x-amz-date': amzDate, 'x-amz-content-sha256': ph };
      const sl        = Object.keys(headers).sort();
      const ch        = sl.map(h => `${h}:${headers[h]}`).join('\n') + '\n';
      const ss        = sl.join(';');
      const cr        = ['PUT', `/${S3_BUCKET}`, '', ch, ss, ph].join('\n');
      const cs        = `${dateStamp}/us-east-1/s3/aws4_request`;
      const sts       = ['AWS4-HMAC-SHA256', amzDate, cs, await sha256Hex(cr)].join('\n');
      let sk: ArrayBuffer = await hmac('AWS4' + S3_SECRET_KEY, dateStamp);
      sk = await hmac(sk, 'us-east-1'); sk = await hmac(sk, 's3'); sk = await hmac(sk, 'aws4_request');
      const sig = toHex(await hmac(sk, sts));
      await fetch(urlStr, { method: 'PUT', headers: { ...headers, Authorization: `AWS4-HMAC-SHA256 Credential=${S3_ACCESS_KEY}/${cs}, SignedHeaders=${ss}, Signature=${sig}` } });
      console.log(`✅ S3 bucket "${S3_BUCKET}" created.`);
    } else {
      console.log(`✅ S3 bucket "${S3_BUCKET}" is accessible.`);
    }
  } catch(e) { console.error('S3 bucket check failed:', e); }
}

// ─── S3 versioning ────────────────────────────────────────────────────────────
async function s3SaveSnapshot(html: string): Promise<string> {
  const timestamp = Math.floor(Date.now() / 1000); // second precision
  const key       = `history/${INDEX_FILE.replace('.html', '')}_${timestamp}.html`;
  const buf       = new TextEncoder().encode(html);
  const res       = await s3Fetch('PUT', key, buf, 'text/html; charset=utf-8');
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`S3 PUT failed [${res.status}]: ${body}`);
  }
  console.log(`💾 S3 snapshot: ${key}`);
  return key;
}

async function s3ListVersions(): Promise<string[]> {
  const endpoint = S3_ENDPOINT.replace(/\/$/, '');
  const prefix   = `history/${INDEX_FILE.replace('.html', '')}_`;
  const query    = `list-type=2&prefix=${encodeURIComponent(prefix)}`;
  const urlObj   = new URL(`${endpoint}/${S3_BUCKET}?${query}`);

  const now       = new Date();
  const amzDate   = now.toISOString().replace(/[:\-]|\.\d{3}/g, '').slice(0, 15) + 'Z';
  const dateStamp = amzDate.slice(0, 8);
  const ph        = await sha256Hex('');
  const headers: Record<string, string> = { 'host': urlObj.host, 'x-amz-date': amzDate, 'x-amz-content-sha256': ph };
  const sl        = Object.keys(headers).sort();
  const ch        = sl.map(h => `${h}:${headers[h]}`).join('\n') + '\n';
  const ss        = sl.join(';');
  const cr        = ['GET', `/${S3_BUCKET}`, query, ch, ss, ph].join('\n');
  const cs        = `${dateStamp}/us-east-1/s3/aws4_request`;
  const sts       = ['AWS4-HMAC-SHA256', amzDate, cs, await sha256Hex(cr)].join('\n');
  let sk: ArrayBuffer = await hmac('AWS4' + S3_SECRET_KEY, dateStamp);
  sk = await hmac(sk, 'us-east-1'); sk = await hmac(sk, 's3'); sk = await hmac(sk, 'aws4_request');
  const sig = toHex(await hmac(sk, sts));

  const res = await fetch(urlObj.toString(), {
    headers: { ...headers, Authorization: `AWS4-HMAC-SHA256 Credential=${S3_ACCESS_KEY}/${cs}, SignedHeaders=${ss}, Signature=${sig}` }
  });
  const text = await res.text();
  const keys = [...text.matchAll(/<Key>([^<]+)<\/Key>/g)].map(m => m[1]);
  return keys.sort();
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

// ─── Git auto-commit ──────────────────────────────────────────────────────────
function autoCommit(message: string) {
  exec(`git add ${INDEX_FILE} && git commit -m "${message}"`, { cwd: process.cwd() }, (err, stdout, stderr) => {
    if (err && !stdout.includes('nothing to commit') && !stderr.includes('nothing to commit')) {
      console.error('Git commit error:', stderr || err.message);
    } else {
      console.log(`✅ Git: "${message}"`);
    }
  });
}

// ─── Save snapshot then commit ─────────────────────────────────────────────────
async function snapshotAndCommit(message: string) {
  const indexPath = path.join(process.cwd(), INDEX_FILE);
  const html      = fs.readFileSync(indexPath, 'utf-8');
  try {
    await s3SaveSnapshot(html);
  } catch(e) { console.error('S3 snapshot error:', e); }
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
        if (versions.length < 2) {
          return new Response(JSON.stringify({ success: false, error: 'Not enough history to rollback' }), { status: 400, headers: { 'Content-Type': 'application/json' } });
        }
        const newest = versions[versions.length - 1];
        const target = versions[versions.length - 2];
        const html   = await s3GetVersion(target);
        fs.writeFileSync(path.join(process.cwd(), INDEX_FILE), html, 'utf-8');
        await s3DeleteVersion(newest);
        autoCommit(`AI Update ⏪ Rollback to ${target}`);
        return new Response(JSON.stringify({ success: true, versionsLeft: versions.length - 2 }), { headers: { 'Content-Type': 'application/json' } });
      } catch(e: any) {
        console.error('Rollback error:', e);
        return new Response(JSON.stringify({ success: false, error: e.message }), { status: 500, headers: { 'Content-Type': 'application/json' } });
      }
    }

    // AI Generate
    if (url.pathname === '/api/generate' && req.method === 'POST') {
      try {
        const body = await req.json();
        const { prompt, targetHtml, chunks } = body;
        if (!prompt) return new Response(JSON.stringify({ error: 'Prompt is required' }), { status: 400 });

        const indexPath  = path.join(process.cwd(), INDEX_FILE);
        let currentHtml  = '';
        try { currentHtml = fs.readFileSync(indexPath, 'utf-8'); }
        catch(e) { return new Response(JSON.stringify({ error: `Could not read ${INDEX_FILE}` }), { status: 500 }); }

        // ── Chunk / cluster mode ───────────────────────────────────────────────
        if (chunks && chunks.length > 0) {
          console.log(`Minimax cluster mode: ${chunks.length} chunks...`);
          return new Response(new ReadableStream({
            async start(controller) {
              try {
                for (let i = 0; i < chunks.length; i += 3) {
                  const batch = chunks.slice(i, i + 3);
                  const results = await Promise.all(batch.map(async (chunk: string, bi: number) => {
                    const gi = i + bi;
                    const sysP = `You are an expert Frontend Web Developer. Return ONLY the modified HTML for this specific layout section. Keep TailwindCSS. No markdown.`;
                    const res  = await fetch('https://api.minimax.io/v1/chat/completions', {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${MINIMAX_API_KEY}` },
                      body: JSON.stringify({ model: 'MiniMax-M2.7', messages: [{ role: 'system', content: sysP }, { role: 'user', content: `TARGET:\n${chunk}\n\nREQUEST: ${prompt}` }], stream: true })
                    });
                    if (!res.ok) return null;
                    let acc = ''; const reader = res.body!.getReader(); const dec = new TextDecoder();
                    while (true) {
                      const { done, value } = await reader.read(); if (done) break;
                      for (const line of dec.decode(value, { stream: true }).split('\n')) {
                        if (line.startsWith('data: ') && !line.includes('[DONE]')) {
                          try { const d = JSON.parse(line.slice(6)); const c = d.choices?.[0]?.delta?.content; if (c) { acc += c; controller.enqueue(new TextEncoder().encode(c)); } } catch(_) {}
                        }
                      }
                    }
                    return { chunk, gi, acc };
                  }));

                  let liveHtml = fs.readFileSync(indexPath, 'utf-8'); let changed = false;
                  for (const r of results) {
                    if (!r) continue;
                    let fh = r.acc.trim().replace(/<think>[\s\S]*?<\/think>/gi, '').trim();
                    const m = fh.match(/```(?:html)?\s*([\s\S]*?)```/); if (m) fh = m[1].trim(); else { const ft = fh.indexOf('<'); if (ft !== -1) fh = fh.substring(ft).trim(); }
                    if (fh) { const nh = liveHtml.replace(r.chunk, fh); if (nh !== liveHtml) { liveHtml = nh; changed = true; console.log(`Chunk ${r.gi+1}/${chunks.length} injected.`); } }
                  }
                  if (changed) { fs.writeFileSync(indexPath, liveHtml, 'utf-8'); await snapshotAndCommit('AI Update: Batch chunk modifications via Inspector'); }
                }
                controller.close();
              } catch(e) { controller.error(e); }
            }
          }), { headers: { 'Content-Type': 'text/event-stream' } });
        }

        // ── Single mode ────────────────────────────────────────────────────────
        console.log('Minimax single block mode...');
        let sysP = `You are an expert Frontend Web Developer specializing in UI/UX and TailwindCSS. Return ONLY the complete updated HTML starting with <!DOCTYPE html>. No markdown. Premium design.`;
        let usrP = `CURRENT HTML:\n${currentHtml}\n\nREQUEST: ${prompt}`;
        if (targetHtml) {
          sysP = `Return ONLY the modified HTML for this specific element. No markdown, no explanation.`;
          usrP = `TARGET:\n${targetHtml}\n\nREQUEST: ${prompt}`;
        }

        const apiRes = await fetch('https://api.minimax.io/v1/chat/completions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${MINIMAX_API_KEY}` },
          body: JSON.stringify({ model: 'MiniMax-M2.7', messages: [{ role: 'system', content: sysP }, { role: 'user', content: usrP }], stream: true })
        });
        if (!apiRes.ok) {
          const et = await apiRes.text();
          return new Response(JSON.stringify({ error: 'Minimax API failed', details: et }), { status: 500 });
        }

        const reader = apiRes.body!.getReader(); const dec = new TextDecoder();
        return new Response(new ReadableStream({
          async start(controller) {
            let acc = '';
            try {
              while (true) {
                const { done, value } = await reader.read(); if (done) break;
                for (const line of dec.decode(value, { stream: true }).split('\n')) {
                  if (line.startsWith('data: ') && !line.includes('[DONE]')) {
                    try { const d = JSON.parse(line.slice(6)); const c = d.choices?.[0]?.delta?.content; if (c) { acc += c; controller.enqueue(new TextEncoder().encode(c)); } } catch(_) {}
                  }
                }
              }
              let fh = acc.trim().replace(/<think>[\s\S]*?<\/think>/gi, '').trim();
              const m = fh.match(/```(?:html)?\s*([\s\S]*?)```/); if (m) fh = m[1].trim(); else { const ft = fh.indexOf('<'); if (ft !== -1) fh = fh.substring(ft).trim(); }
              if (targetHtml) {
                fs.writeFileSync(indexPath, currentHtml.replace(targetHtml, fh), 'utf-8');
                await snapshotAndCommit('AI Update: Targeted element modified via Inspector');
              } else {
                fs.writeFileSync(indexPath, fh, 'utf-8');
                await snapshotAndCommit('AI Update: Full layout redesigned via Inspector');
              }
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

console.log(`✅ Server on port ${process.env.PORT || 3000} — S3: ${S3_BUCKET} @ ${S3_ENDPOINT}`);
