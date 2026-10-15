import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { after, before, test } from "node:test";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const PORT = 43117;
const BASE = `http://127.0.0.1:${PORT}`;

let child = null;

before(async () => {
  child = spawn(process.execPath, ["server.ts"], {
    cwd: ROOT,
    env: { ...process.env, PORT: String(PORT), HOST: "127.0.0.1" },
    stdio: ["ignore", "pipe", "pipe"],
  });
  child.stderr.on("data", (chunk) => process.stderr.write(chunk));
  await new Promise((resolve, reject) => {
    let buffer = "";
    const timer = setTimeout(() => reject(new Error("server did not start in time")), 12000);
    const fail = (code) => {
      clearTimeout(timer);
      reject(new Error(`server exited early with code ${code}`));
    };
    child.once("exit", fail);
    child.stdout.on("data", (chunk) => {
      buffer += String(chunk);
      if (buffer.includes("listening")) {
        clearTimeout(timer);
        child.removeListener("exit", fail);
        resolve(undefined);
      }
    });
  });
});

after(() => {
  if (child) child.kill("SIGTERM");
});

test("GET / serves the landing page with security headers", async () => {
  const res = await fetch(`${BASE}/`);
  assert.equal(res.status, 200);
  assert.match(res.headers.get("content-type"), /text\/html/);
  const csp = res.headers.get("content-security-policy") || "";
  assert.match(csp, /default-src 'none'/);
  assert.match(csp, /script-src 'self'/);
  assert.equal(res.headers.get("x-content-type-options"), "nosniff");
  assert.equal(res.headers.get("referrer-policy"), "no-referrer");
  assert.equal(res.headers.get("x-frame-options"), "DENY");
  const body = await res.text();
  assert.match(body, /Silviya Aeterna/);
  assert.match(body, /data-bg=/);
});

test("GET /index.html behaves like the root document", async () => {
  const res = await fetch(`${BASE}/index.html`);
  assert.equal(res.status, 200);
  assert.match(res.headers.get("content-type"), /text\/html/);
});

test("HEAD / returns headers without a body", async () => {
  const res = await fetch(`${BASE}/`, { method: "HEAD" });
  assert.equal(res.status, 200);
  assert.equal(await res.text(), "");
});

test("every local asset referenced by index.html answers 200", async () => {
  const html = await readFile(path.join(ROOT, "index.html"), "utf8");
  const refs = [...html.matchAll(/(?:src|href)="([^"]+)"/g)]
    .map((match) => match[1])
    .filter((ref) => !ref.startsWith("#") && !ref.startsWith("http") && !ref.startsWith("data:"));
  assert.ok(refs.length >= 8, `expected local references, found ${refs.length}`);
  for (const ref of new Set(refs)) {
    const res = await fetch(new URL(ref, BASE));
    assert.equal(res.status, 200, `${ref} returned ${res.status}`);
    await res.arrayBuffer();
  }
});

test("styles, script and images are served with correct types", async () => {
  const cases = [
    ["/assets/styles.css", /text\/css/],
    ["/assets/site.js", /javascript/],
    ["/assets/favicon.svg", /image\/svg\+xml/],
    ["/assets/images/hero-garden.webp", /image\/webp/],
    ["/assets/social-og.png", /image\/png/],
    ["/assets/fonts/CormorantGaramond-Variable.woff2", /font\/woff2/],
    ["/assets/fonts/Geist-Variable-subset.woff2", /font\/woff2/],
  ];
  for (const [pathName, type] of cases) {
    const res = await fetch(`${BASE}${pathName}`);
    assert.equal(res.status, 200, `${pathName} returned ${res.status}`);
    assert.match(res.headers.get("content-type"), type);
    await res.arrayBuffer();
  }
});

test("unknown routes return 404", async () => {
  for (const pathName of ["/nope", "/does/not/exist", "/assets/missing.svg", "/assets"]) {
    const res = await fetch(`${BASE}${pathName}`);
    assert.equal(res.status, 404, `${pathName} returned ${res.status}`);
  }
});

test("server sources and dev documents are never served", async () => {
  const hidden = [
    "/server.ts",
    "/package.json",
    "/PRODUCT.md",
    "/README.md",
    "/tests/server.test.mjs",
    "/.impeccable/surfaces/index-html.md",
    "/.gitignore",
    "/Dockerfile",
    "/tools/ASSET-MANIFEST.json",
    "/tools/ASSET-PROVENANCE.md",
    "/tools/prepare_images.py",
    "/tools/Onest-source.ttf",
    "/.impeccable/review/report.json",
    "/DESIGN.md",
  ];
  for (const pathName of hidden) {
    const res = await fetch(`${BASE}${pathName}`);
    assert.equal(res.status, 404, `${pathName} leaked with ${res.status}`);
  }
});

test("removed write and AI endpoints refuse every mutation method", async () => {
  const endpoints = [
    ["/", "POST"],
    ["/api/generate", "POST"],
    ["/api/edit", "POST"],
    ["/api/rollback", "POST"],
    ["/api/save", "PUT"],
    ["/api/sections", "PATCH"],
    ["/api/restore", "DELETE"],
  ];
  for (const [pathName, method] of endpoints) {
    const res = await fetch(`${BASE}${pathName}`, { method, body: "{}" });
    assert.equal(res.status, 405, `${method} ${pathName} returned ${res.status}`);
    assert.equal(res.headers.get("allow"), "GET, HEAD");
    const body = await res.text();
    assert.doesNotMatch(body, /AI|model|openrouter|minimax/i);
  }
});

test("path traversal stays inside the asset directory", async () => {
  const attempts = [
    "/assets/../server.ts",
    "/assets/../../etc/passwd",
    "/assets/%2e%2e/server.ts",
    "/assets/..%2f..%2fserver.ts",
    "/assets/%2e%2e%2f%2e%2e%2fpackage.json",
  ];
  for (const pathName of attempts) {
    const res = await fetch(`${BASE}${pathName}`);
    assert.equal(res.status, 404, `${pathName} returned ${res.status}`);
    const body = await res.text();
    assert.doesNotMatch(body, /createServer|MINIMAX|S3_SECRET/);
  }
});

test("the server keeps no secrets and makes no outbound calls", async () => {
  const source = await readFile(path.join(ROOT, "server.ts"), "utf8");
  for (const banned of ["fetch(", "child_process", "API_KEY", "SECRET", "MINIMAX", "OPENROUTER", "process.env.S3"]) {
    assert.ok(!source.includes(banned), `server.ts still references ${banned}`);
  }
});
