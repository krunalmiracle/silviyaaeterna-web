import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';

// ─── S3 Config ────────────────────────────────────────────────────────────────
const S3_ENDPOINT   = process.env.S3_ENDPOINT   || 'http://s3-rustfs-cdvlmf:9000';
const S3_ACCESS_KEY = process.env.S3_ACCESS_KEY || 'rustfsadmin';
const S3_SECRET_KEY = process.env.S3_SECRET_KEY || 'ecirjxhvfpuzn3ut';
const S3_BUCKET     = process.env.S3_BUCKET     || 'silviyaaeterna';
const MINIMAX_API_KEY = process.env.MINIMAX_API_KEY;

if (!MINIMAX_API_KEY) {
  console.error('Warning: MINIMAX_API_KEY is not set.');
}

// ─── AWS Signature v4 helpers (no external deps) ─────────────────────────────
async function hmac(key: BufferSource | string, data: string): Promise<ArrayBuffer> {
  const keyData = typeof key === 'string'
    ? new TextEncoder().encode(key)
    : key;
  const cryptoKey = await crypto.subtle.importKey(
    'raw', keyData, { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']
  );
  return crypto.subtle.sign('HMAC', cryptoKey, new TextEncoder().encode(data));
}

function toHex(buf: ArrayBuffer) {
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
}

async function sha256Hex(data: string | ArrayBuffer): Promise<string> {
  const buf = typeof data === 'string' ? new TextEncoder().encode(data) : data;
  return toHex(await crypto.subtle.digest('SHA-256', buf));
}

async function s3Request(method: string, key: string, body?: ArrayBuffer | null, contentType?: string) {
  const url = new URL(`${S3_ENDPOINT}/${S3_BUCKET}/${key}`);
  const now = new Date();
  const amzDate = now.toISOString().replace(/[:-]|\.\d{3}/g, '').slice(0, 15) + 'Z';
  const dateStamp = amzDate.slice(0, 8);
  const region = 'us-east-1';
  const service = 's3';

  const payloadHash = await sha256Hex(body ?? '');
  const ct = contentType ?? 'application/octet-stream';

  const headers: Record<string, string> = {
    'host': url.host,
    'x-amz-date': amzDate,
    'x-amz-content-sha256': payloadHash,
    ...(body != null ? { 'content-type': ct } : {}),
  };

  const signedHeadersList = Object.keys(headers).sort();
  const canonicalHeaders = signedHeadersList.map(h => `${h}:${headers[h]}`).join('\n') + '\n';
  const signedHeadersStr = signedHeadersList.join(';');
  const canonicalRequest = [method, `/${S3_BUCKET}/${key}`, '', canonicalHeaders, signedHeadersStr, payloadHash].join('\n');

  const credentialScope = `${dateStamp}/${region}/${service}/aws4_request`;
  const stringToSign = ['AWS4-HMAC-SHA256', amzDate, credentialScope, await sha256Hex(canonicalRequest)].join('\n');

  let sigKey: ArrayBuffer = await hmac('AWS4' + S3_SECRET_KEY, dateStamp);
  sigKey = await hmac(sigKey, region);
  sigKey = await hmac(sigKey, service);
  sigKey = await hmac(sigKey, 'aws4_request');
  const signature = toHex(await hmac(sigKey, stringToSign));

  const authHeader = `AWS4-HMAC-SHA256 Credential=${S3_ACCESS_KEY}/${credentialScope}, SignedHeaders=${signedHeadersStr}, Signature=${signature}`;

  const fetchHeaders: Record<string, string> = {
    ...headers,
    'Authorization': authHeader,
  };

  return fetch(url.toString(), {
    method,
    headers: fetchHeaders,
    body: body ?? undefined,
  });
}

// ─── Ensure bucket exists ─────────────────────────────────────────────────────
async function ensureBucket() {
  try {
    const res = await s3Request('HEAD', '');
    if (res.status === 404) {
      // Create bucket via PUT on the bucket root
      const url = new URL(`${S3_ENDPOINT}/${S3_BUCKET}`);
      const now = new Date();
      const amzDate = now.toISOString().replace(/[:-]|\.\d{3}/g, '').slice(0, 15) + 'Z';
      const dateStamp = amzDate.slice(0, 8);
      const region = 'us-east-1'; const service = 's3';
      const payloadHash = await sha256Hex('');
      const headers: Record<string, string> = { 'host': url.host, 'x-amz-date': amzDate, 'x-amz-content-sha256': payloadHash };
      const signedHeadersList = Object.keys(headers).sort();
      const canonicalHeaders = signedHeadersList.map(h => `${h}:${headers[h]}`).join('\n') + '\n';
      const signedHeadersStr = signedHeadersList.join(';');
      const canonicalRequest = ['PUT', `/${S3_BUCKET}`, '', canonicalHeaders, signedHeadersStr, payloadHash].join('\n');
      const credentialScope = `${dateStamp}/${region}/${service}/aws4_request`;
      const stringToSign = ['AWS4-HMAC-SHA256', amzDate, credentialScope, await sha256Hex(canonicalRequest)].join('\n');
      let sigKey: ArrayBuffer = await hmac('AWS4' + S3_SECRET_KEY, dateStamp);
      sigKey = await hmac(sigKey, region); sigKey = await hmac(sigKey, service); sigKey = await hmac(sigKey, 'aws4_request');
      const signature = toHex(await hmac(sigKey, stringToSign));
      await fetch(url.toString(), {
        method: 'PUT',
        headers: { ...headers, Authorization: `AWS4-HMAC-SHA256 Credential=${S3_ACCESS_KEY}/${credentialScope}, SignedHeaders=${signedHeadersStr}, Signature=${signature}` },
      });
      console.log(`✅ S3 bucket "${S3_BUCKET}" created.`);
    }
  } catch(e) {
    console.error('S3 bucket check failed (will retry on next write):', e);
  }
}

// ─── S3 versioning helpers ────────────────────────────────────────────────────
async function s3SaveVersion(html: string): Promise<string> {
  const timestamp = Math.floor(Date.now() / 1000);
  const key = `history/index_${timestamp}.html`;
  const buf = new TextEncoder().encode(html);
  const res = await s3Request('PUT', key, buf.buffer, 'text/html; charset=utf-8');
  if (!res.ok) throw new Error(`S3 PUT failed: ${res.status} ${await res.text()}`);
  console.log(`💾 S3 snapshot saved: ${key}`);
  return key;
}

async function s3ListVersions(): Promise<string[]> {
  const url = new URL(`${S3_ENDPOINT}/${S3_BUCKET}`);
  url.searchParams.set('prefix', 'history/index_');
  url.searchParams.set('list-type', '2');

  const now = new Date();
  const amzDate = now.toISOString().replace(/[:-]|\.\d{3}/g, '').slice(0, 15) + 'Z';
  const dateStamp = amzDate.slice(0, 8);
  const region = 'us-east-1'; const service = 's3';
  const payloadHash = await sha256Hex('');
  const query = `list-type=2&prefix=${encodeURIComponent('history/index_')}`;
  const headers: Record<string, string> = { 'host': url.host, 'x-amz-date': amzDate, 'x-amz-content-sha256': payloadHash };
  const signedHeadersList = Object.keys(headers).sort();
  const canonicalHeaders = signedHeadersList.map(h => `${h}:${headers[h]}`).join('\n') + '\n';
  const signedHeadersStr = signedHeadersList.join(';');
  const canonicalRequest = ['GET', `/${S3_BUCKET}`, query, canonicalHeaders, signedHeadersStr, payloadHash].join('\n');
  const credentialScope = `${dateStamp}/${region}/${service}/aws4_request`;
  const stringToSign = ['AWS4-HMAC-SHA256', amzDate, credentialScope, await sha256Hex(canonicalRequest)].join('\n');
  let sigKey: ArrayBuffer = await hmac('AWS4' + S3_SECRET_KEY, dateStamp);
  sigKey = await hmac(sigKey, region); sigKey = await hmac(sigKey, service); sigKey = await hmac(sigKey, 'aws4_request');
  const signature = toHex(await hmac(sigKey, stringToSign));

  const res = await fetch(url.toString(), {
    headers: { ...headers, Authorization: `AWS4-HMAC-SHA256 Credential=${S3_ACCESS_KEY}/${credentialScope}, SignedHeaders=${signedHeadersStr}, Signature=${signature}` },
  });
  const text = await res.text();
  const keys = [...text.matchAll(/<Key>([^<]+)<\/Key>/g)].map(m => m[1]);
  return keys.sort(); // chronological (timestamp embedded in key name)
}

async function s3GetVersion(key: string): Promise<string> {
  const res = await s3Request('GET', key);
  if (!res.ok) throw new Error(`S3 GET failed: ${res.status}`);
  return res.text();
}

async function s3DeleteVersion(key: string) {
  const res = await s3Request('DELETE', key);
  if (!res.ok) console.error(`S3 DELETE failed for ${key}: ${res.status}`);
}

// ─── Auto-commit to git ────────────────────────────────────────────────────────
function autoCommit(message: string) {
  exec(`git add index.html && git commit -m "${message}"`, { cwd: process.cwd() }, (err, stdout, stderr) => {
    if (err && !stdout.includes('nothing to commit') && !stderr.includes('nothing to commit')) {
      console.error('Git commit error:', stderr || err.message);
    } else {
      console.log(`✅ Git committed: "${message}"`);
    }
  });
}

// ─── Save current index.html to S3 then git commit ────────────────────────────
async function snapshotAndCommit(message: string) {
  const indexPath = path.join(process.cwd(), 'index.html');
  const html = fs.readFileSync(indexPath, 'utf-8');
  try {
    await s3SaveVersion(html);
  } catch(e) {
    console.error('S3 snapshot failed:', e);
  }
  autoCommit(message);
}

// ─── Server ───────────────────────────────────────────────────────────────────
await ensureBucket();

Bun.serve({
  port: process.env.PORT || 3000,
  async fetch(req) {
    const url = new URL(req.url);

    // ── Rollback endpoint ──────────────────────────────────────────────────────
    if (url.pathname === '/api/rollback' && req.method === 'POST') {
      try {
        const versions = await s3ListVersions();
        if (versions.length < 2) {
          return new Response(JSON.stringify({ success: false, error: 'Not enough history to rollback' }), { status: 400, headers: { 'Content-Type': 'application/json' } });
        }
        const newestKey  = versions[versions.length - 1];
        const targetKey  = versions[versions.length - 2];
        const targetHtml = await s3GetVersion(targetKey);

        const indexPath = path.join(process.cwd(), 'index.html');
        fs.writeFileSync(indexPath, targetHtml, 'utf-8');

        // Delete the newest version (it was undone)
        await s3DeleteVersion(newestKey);
        autoCommit(`AI Update ⏪ Rollback to ${targetKey}`);

        return new Response(JSON.stringify({ success: true, versionsLeft: versions.length - 2 }), { headers: { 'Content-Type': 'application/json' } });
      } catch(e: any) {
        console.error('Rollback error:', e);
        return new Response(JSON.stringify({ success: false, error: e.message }), { status: 500, headers: { 'Content-Type': 'application/json' } });
      }
    }

    // ── AI Generation endpoint ─────────────────────────────────────────────────
    if (url.pathname === '/api/generate' && req.method === 'POST') {
      try {
        const body = await req.json();
        const { prompt, targetHtml, chunks } = body;
        if (!prompt) return new Response(JSON.stringify({ error: 'Prompt is required' }), { status: 400 });

        const indexPath = path.join(process.cwd(), 'index.html');
        let currentHtml = '';
        try { currentHtml = fs.readFileSync(indexPath, 'utf-8'); }
        catch(e) { return new Response(JSON.stringify({ error: 'Could not read index.html' }), { status: 500 }); }

        // ── Chunked cluster mode ───────────────────────────────────────────────
        if (chunks && chunks.length > 0) {
          console.log(`Requesting Minimax AI in cluster mode (${chunks.length} chunks)...`);
          return new Response(
            new ReadableStream({
              async start(controller) {
                try {
                  for (let i = 0; i < chunks.length; i += 3) {
                    const batch = chunks.slice(i, i + 3);
                    const fetchPromises = batch.map(async (chunk: string, batchIndex: number) => {
                      const globalIdx = i + batchIndex;
                      const sysPrompt = `You are an expert Frontend Web Developer. Return ONLY the modified HTML for this specific layout section. DO NOT remove existing IDs or critical classes unless asked. CRITICAL: ONLY return the modified exact html block. No markdown, no explanations.`;
                      const usrPrompt = `TARGET SECTION HTML:\n${chunk}\n\nUSER REQUEST: ${prompt}`;
                      const response = await fetch('https://api.minimax.io/v1/chat/completions', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${MINIMAX_API_KEY}` },
                        body: JSON.stringify({ model: 'MiniMax-M2.7', messages: [{ role: 'system', content: sysPrompt }, { role: 'user', content: usrPrompt }], stream: true })
                      });
                      if (!response.ok) return null;
                      let accumulated = '';
                      const reader = response.body!.getReader();
                      const decoder = new TextDecoder('utf-8');
                      while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        const lines = decoder.decode(value, { stream: true }).split('\n');
                        for (const line of lines) {
                          if (line.startsWith('data: ') && !line.includes('[DONE]')) {
                            try {
                              const data = JSON.parse(line.slice(6));
                              const content = data.choices?.[0]?.delta?.content;
                              if (content) { accumulated += content; controller.enqueue(new TextEncoder().encode(content)); }
                            } catch(_) {}
                          }
                        }
                      }
                      return { chunk, globalIdx, accumulated };
                    });

                    const batchResults = await Promise.all(fetchPromises);
                    let liveHtml = fs.readFileSync(indexPath, 'utf-8');
                    let changed = false;
                    for (const res of batchResults) {
                      if (!res) continue;
                      let finalHtml = res.accumulated.trim().replace(/<think>[\s\S]*?<\/think>/gi, '').trim();
                      const mdMatch = finalHtml.match(/```(?:html)?\s*([\s\S]*?)```/);
                      if (mdMatch) finalHtml = mdMatch[1].trim();
                      else { const ft = finalHtml.indexOf('<'); if (ft !== -1) finalHtml = finalHtml.substring(ft).trim(); }
                      if (finalHtml) {
                        const newHtml = liveHtml.replace(res.chunk, finalHtml);
                        if (newHtml !== liveHtml) { liveHtml = newHtml; changed = true; console.log(`Chunk ${res.globalIdx + 1}/${chunks.length} injected.`); }
                      }
                    }
                    if (changed) {
                      fs.writeFileSync(indexPath, liveHtml, 'utf-8');
                      await snapshotAndCommit('AI Update: Applied batch chunk modifications via Inspector');
                    }
                  }
                  console.log(`Queue completed for ${chunks.length} chunks.`);
                  controller.close();
                } catch(e) { controller.error(e); }
              }
            }),
            { headers: { 'Content-Type': 'text/event-stream' } }
          );
        }

        // ── Single block / targeted mode ───────────────────────────────────────
        console.log('Requesting Minimax AI in single block mode...');
        let systemPrompt = `You are an expert Frontend Web Developer specializing in UI/UX. You are given the current HTML of a webpage. Return ONLY the complete, updated HTML starting with <!DOCTYPE html>. DO NOT use markdown code blocks. The design must feel extremely premium.`;
        let userPrompt = `CURRENT HTML:\n${currentHtml}\n\nUSER REQUEST: ${prompt}`;

        if (targetHtml) {
          systemPrompt = `You are an expert Frontend Web Developer. You are editing a specific section of a webpage. Return ONLY the modified HTML for this specific element. No markdown, no explanations.`;
          userPrompt = `TARGET ELEMENT HTML:\n${targetHtml}\n\nUSER REQUEST: ${prompt}`;
        }

        const response = await fetch('https://api.minimax.io/v1/chat/completions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${MINIMAX_API_KEY}` },
          body: JSON.stringify({ model: 'MiniMax-M2.7', messages: [{ role: 'system', content: systemPrompt }, { role: 'user', content: userPrompt }], stream: true })
        });

        if (!response.ok) {
          const errText = await response.text();
          return new Response(JSON.stringify({ error: 'Minimax API failed', details: errText }), { status: 500 });
        }

        const reader = response.body!.getReader();
        const decoder = new TextDecoder('utf-8');

        return new Response(
          new ReadableStream({
            async start(controller) {
              let accumulatedHtml = '';
              try {
                while (true) {
                  const { done, value } = await reader.read();
                  if (done) break;
                  const lines = decoder.decode(value, { stream: true }).split('\n');
                  for (const line of lines) {
                    if (line.startsWith('data: ') && !line.includes('[DONE]')) {
                      try {
                        const data = JSON.parse(line.slice(6));
                        const content = data.choices?.[0]?.delta?.content;
                        if (content) { accumulatedHtml += content; controller.enqueue(new TextEncoder().encode(content)); }
                      } catch(_) {}
                    }
                  }
                }

                let finalHtml = accumulatedHtml.trim().replace(/<think>[\s\S]*?<\/think>/gi, '').trim();
                const mdMatch = finalHtml.match(/```(?:html)?\s*([\s\S]*?)```/);
                if (mdMatch) finalHtml = mdMatch[1].trim();
                else { const ft = finalHtml.indexOf('<'); if (ft !== -1) finalHtml = finalHtml.substring(ft).trim(); }

                const indexPath2 = path.join(process.cwd(), 'index.html');
                if (targetHtml) {
                  fs.writeFileSync(indexPath2, currentHtml.replace(targetHtml, finalHtml), 'utf-8');
                  await snapshotAndCommit('AI Update: Targeted element modified via Inspector');
                } else {
                  fs.writeFileSync(indexPath2, finalHtml, 'utf-8');
                  await snapshotAndCommit('AI Update: Full layout redesigned via Inspector');
                }
                controller.close();
              } catch(err) { controller.error(err); }
            }
          }),
          { headers: { 'Content-Type': 'text/event-stream' } }
        );
      } catch(error: any) {
        console.error('Error in /api/generate:', error);
        return new Response(JSON.stringify({ error: error.message }), { status: 500 });
      }
    }

    // ── Static file server ─────────────────────────────────────────────────────
    let filePath = path.join(process.cwd(), url.pathname);
    if (filePath.endsWith('/')) {
      filePath += 'index.html';
    } else {
      try {
        const stats = fs.statSync(filePath);
        if (stats.isDirectory()) filePath = path.join(filePath, 'index.html');
      } catch(_) {}
    }

    const file = Bun.file(filePath);
    if (await file.exists()) return new Response(file);
    return new Response('Not Found', { status: 404 });
  }
});

console.log(`Server running on port ${process.env.PORT || 3000} — serving index.html`);
