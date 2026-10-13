/* Minimal hardened static server for Silviya Aeterna.
 * Serves the landing page and allow-listed files from this directory.
 * No secrets, no outbound network, no write endpoints, no database, no auth.
 * Runs on Bun (Docker) and on Node 22+ (`node server.ts`).
 */
import { createServer } from "node:http";
import { createReadStream, statSync } from "node:fs";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)));
const PORT = Number.parseInt(process.env.PORT || "3000", 10);
const HOST = process.env.HOST || "0.0.0.0";

const INDEX = path.join(ROOT, "index.html");
const HTML_PATHS = new Set(["/", "/index.html", "/index.htm"]);
const ASSET_DIR = path.join(ROOT, "assets");
const ASSET_EXT = new Set([
  ".svg", ".css", ".js", ".woff2", ".woff", ".png", ".ico", ".jpg", ".jpeg", ".webp", ".txt",
]);

const CONTENT_TYPES = new Map([
  [".html", "text/html; charset=utf-8"],
  [".css", "text/css; charset=utf-8"],
  [".js", "text/javascript; charset=utf-8"],
  [".svg", "image/svg+xml"],
  [".png", "image/png"],
  [".jpg", "image/jpeg"],
  [".jpeg", "image/jpeg"],
  [".webp", "image/webp"],
  [".ico", "image/x-icon"],
  [".woff2", "font/woff2"],
  [".woff", "font/woff"],
  [".txt", "text/plain; charset=utf-8"],
]);

const SECURITY_HEADERS = {
  "content-security-policy":
    "default-src 'none'; style-src 'self'; script-src 'self'; img-src 'self'; font-src 'self'; connect-src 'none'; form-action 'none'; base-uri 'none'; frame-ancestors 'none'; object-src 'none'",
  "x-content-type-options": "nosniff",
  "referrer-policy": "no-referrer",
  "permissions-policy":
    "camera=(), microphone=(), geolocation=(), payment=(), usb=(), browsing-topics=()",
  "x-frame-options": "DENY",
  "cross-origin-opener-policy": "same-origin",
  "cross-origin-resource-policy": "same-origin",
  "x-permitted-cross-domain-policies": "none",
  "strict-transport-security": "max-age=31536000; includeSubDomains",
  "cache-control": "no-cache",
};

const NOT_FOUND = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Not found</title></head>
<body style="font-family:system-ui,sans-serif;background:#060a17;color:#edf1f8;padding:3rem">
<h1>404</h1><p>This page does not exist.</p><p><a style="color:#9fe7ce" href="/">Back to Silviya Aeterna</a></p>
</body></html>`;

const METHOD_NOT_ALLOWED = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Method not allowed</title></head>
<body style="font-family:system-ui,sans-serif;background:#060a17;color:#edf1f8;padding:3rem">
<h1>405</h1><p>This server only answers GET and HEAD.</p>
</body></html>`;

function resolveAsset(urlPath) {
  let decoded;
  try {
    decoded = decodeURIComponent(urlPath);
  } catch (error) {
    return null;
  }
  if (decoded.includes("\0")) return null;
  const rel = decoded.replace(/^\/+/, "");
  if (rel.split("/").some((segment) => segment.startsWith("."))) return null;
  const abs = path.resolve(ROOT, rel);
  if (abs !== ASSET_DIR && !abs.startsWith(ASSET_DIR + path.sep)) return null;
  if (!ASSET_EXT.has(path.extname(abs).toLowerCase())) return null;
  return abs;
}

function send(res, status, headers, body, headOnly) {
  res.writeHead(status, { ...SECURITY_HEADERS, ...headers });
  if (headOnly) {
    res.end();
    return;
  }
  res.end(body);
}

function sendFile(res, filePath, headOnly) {
  let stat;
  try {
    stat = statSync(filePath);
  } catch (error) {
    send(res, 404, { "content-type": "text/html; charset=utf-8" }, NOT_FOUND, headOnly);
    return;
  }
  const etag = `W/"${stat.size}-${Math.floor(stat.mtimeMs)}"`;
  const type = CONTENT_TYPES.get(path.extname(filePath).toLowerCase()) || "application/octet-stream";
  if (headOnly) {
    send(res, 200, { "content-type": type, "content-length": String(stat.size), etag }, null, true);
    return;
  }
  res.writeHead(200, { ...SECURITY_HEADERS, "content-type": type, "content-length": String(stat.size), etag });
  createReadStream(filePath).pipe(res);
}

const server = createServer((req, res) => {
  const method = (req.method || "GET").toUpperCase();

  if (method !== "GET" && method !== "HEAD") {
    send(
      res,
      405,
      { allow: "GET, HEAD", "content-type": "text/html; charset=utf-8" },
      METHOD_NOT_ALLOWED,
      method === "HEAD"
    );
    return;
  }

  const headOnly = method === "HEAD";
  let pathname = "/";
  try {
    pathname = new URL(req.url || "/", "http://localhost").pathname;
  } catch (error) {
    send(res, 400, { "content-type": "text/plain; charset=utf-8" }, "Bad request", headOnly);
    return;
  }

  if (HTML_PATHS.has(pathname)) {
    sendFile(res, INDEX, headOnly);
    return;
  }

  if (pathname === "/assets" || pathname.startsWith("/assets/")) {
    const target = resolveAsset(pathname);
    if (!target || !existsSync(target) || !statSync(target).isFile()) {
      send(res, 404, { "content-type": "text/html; charset=utf-8" }, NOT_FOUND, headOnly);
      return;
    }
    sendFile(res, target, headOnly);
    return;
  }

  send(res, 404, { "content-type": "text/html; charset=utf-8" }, NOT_FOUND, headOnly);
});

server.listen(PORT, HOST, () => {
  console.log(`silviyaaeterna static server listening on http://localhost:${PORT}`);
});

server.on("error", (error) => {
  console.error(`server error: ${error && error.message ? error.message : error}`);
  process.exit(1);
});
