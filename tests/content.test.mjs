import assert from "node:assert/strict";
import { readFile, access } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { test } from "node:test";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const html = await readFile(path.join(ROOT, "index.html"), "utf8");
const css = await readFile(path.join(ROOT, "assets/styles.css"), "utf8");
const js = await readFile(path.join(ROOT, "assets/site.js"), "utf8");

test("no em dash or en dash anywhere in the shipped page", () => {
  assert.ok(!html.includes("—"), "em dash found in index.html");
  assert.ok(!html.includes("–"), "en dash found in index.html");
  assert.ok(!css.includes("—"), "em dash found in styles.css");
  assert.ok(!js.includes("—"), "em dash found in site.js");
});

test("the page makes no third-party runtime requests", () => {
  const productionOrigin = "https://silviyaaeterna.krusil.com";
  const absoluteUrls = [...html.matchAll(/https?:\/\/[^\"'\s<]+/g)].map((match) => match[0]);
  assert.ok(absoluteUrls.length >= 3, "expected canonical and social metadata URLs");
  const allowedOrigins = [productionOrigin, "https://bg.oriflame.com"];
  for (const url of absoluteUrls) {
    assert.ok(allowedOrigins.some(origin => url.startsWith(origin)), `unexpected external URL: ${url}`);
  }
  assert.ok(!/<(?:script|img)[^>]+(?:src|href)="https?:\/\//.test(html), "runtime asset uses an absolute URL");
  for (const [name, source] of [["styles.css", css], ["site.js", js]]) {
    assert.ok(!/https?:\/\//.test(source), `${name} contains an absolute URL`);
    assert.ok(!source.includes("fonts.googleapis.com"), `${name} links Google Fonts`);
    assert.ok(!source.includes("//cdn"), `${name} references a CDN`);
  }
});

test("no inline styles or scripts that the CSP would block", () => {
  assert.ok(!/ style="/.test(html), "inline style attribute found");
  assert.ok(!/<style[\s>]/.test(html), "inline style block found");
  assert.ok(!/<script(?![^>]*src=)/.test(html), "inline script found");
});

test("every translatable node carries both languages", () => {
  const pairs = [...html.matchAll(/<([a-z]+)([^>]*\sdata-en="[^"]*"[^>]*)>/g)];
  assert.ok(pairs.length >= 40, `expected many bilingual nodes, found ${pairs.length}`);
  let translated = 0;
  for (const [, , attrs] of pairs) {
    const en = (attrs.match(/\sdata-en="([^"]*)"/) || [])[1];
    const bg = (attrs.match(/\sdata-bg="([^"]*)"/) || [])[1];
    assert.ok(bg, `node with data-en is missing data-bg: ${attrs.slice(0, 80)}`);
    if (en !== bg) translated += 1;
  }
  assert.ok(translated >= 30, `only ${translated} nodes actually differ between languages`);
});

test("every image has alt text", () => {
  const imgs = [...html.matchAll(/<img\b[^>]*>/g)];
  assert.equal(imgs.length, 6, "six original sanctuary scenes remain");
  let decorative = 0;
  for (const [tag] of imgs) {
    assert.match(tag, /\salt="/, `image missing alt: ${tag}`);
    const alt = (tag.match(/\salt="([^"]*)"/) || [])[1];
    if (alt === "") {
      /* only the brand marks sit next to the wordmark, so they stay silent */
      assert.match(tag, /assets\/brand-mark\.svg/, `unexpected decorative image: ${tag}`);
      decorative += 1;
      continue;
    }
    assert.match(tag, /\sdata-alt-en="/, `image missing English alt: ${tag}`);
    assert.match(tag, /\sdata-alt-bg="/, `image missing Bulgarian alt: ${tag}`);
  }
  assert.equal(decorative, 0, "every still life has a meaningful bilingual description");
});

test("every local reference resolves to a file on disk", async () => {
  const refs = [...html.matchAll(/(?:src|href)="([^"#][^"]*)"/g)]
    .map((match) => match[1])
    .filter((ref) => !ref.startsWith("http"));
  assert.ok(refs.length >= 8);
  for (const ref of new Set(refs)) {
    await access(path.join(ROOT, ref));
  }
});

test("navigation anchors all point at real sections", () => {
  const ids = new Set([...html.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]));
  for (const id of ["main", "manifesto", "atlas", "channel", "shop", "safety", "hero-title"]) {
    assert.ok(ids.has(id), `missing section id ${id}`);
  }
  const anchors = [...html.matchAll(/href="#([^"]+)"/g)].map((match) => match[1]);
  assert.ok(anchors.length >= 10);
  for (const anchor of new Set(anchors)) {
    assert.ok(ids.has(anchor), `broken anchor #${anchor}`);
  }
});

test("heading structure is a single h1 with ordered levels", () => {
  const levels = [...html.matchAll(/<h([1-6])\b/g)].map((match) => Number(match[1]));
  assert.equal(levels.filter((level) => level === 1).length, 1);
  let previous = 1;
  for (const level of levels) {
    assert.ok(level <= previous + 1, `heading jumps from h${previous} to h${level}`);
    previous = level;
  }
});

test("only the YouTube channel is still coming soon; official shopping links are honest", () => {
  const chips = [...html.matchAll(/<(\w+)([^>]*class="[^"]*soon-state[^"]*"[^>]*)>/g)];
  assert.equal(chips.length, 1);
  assert.match(html, /href="https:\/\/bg\.oriflame\.com\/"/);
  assert.match(html, /href="https:\/\/bg\.oriflame\.com\/join-us\/self-registration"/);
  assert.match(html, /Silviya’s personal link has not been confirmed/);
  assert.doesNotMatch(html, /astrology|numerology|астролог|нумеролог/i);
});

test("language toggle is exposed accessibly", () => {
  assert.match(html, /id="lang-en"[^>]*aria-pressed="true"/);
  assert.match(html, /id="lang-bg"[^>]*aria-pressed="false"/);
  assert.match(html, /<button type="button" id="lang-en" lang="en"/);
  assert.match(html, /<button type="button" id="lang-bg" lang="bg"/);
  assert.match(html, /role="group" aria-label="Language"/);
});

test("motion respects reduced motion and survives failed JavaScript", () => {
  assert.match(css, /@media\s*\(prefers-reduced-motion:\s*no-preference\)/);
  assert.match(css, /@media\s*\(prefers-reduced-motion:\s*reduce\)/);
  assert.ok(!css.includes("opacity: 0"), "content must never depend on a reveal");
  assert.ok(!css.includes("visibility: hidden"), "content must remain readable without JS");
  assert.ok(!js.includes('addEventListener("scroll"'), "no window scroll listeners");
  assert.ok(!js.includes("addEventListener('scroll'"), "no window scroll listeners");
});

test("the page declares the two languages and viewport", () => {
  assert.match(html, /<html lang="en">/);
  assert.match(html, /name="viewport" content="width=device-width, initial-scale=1"/);
  assert.match(html, /https:\/\/silviyaaeterna\.krusil\.com\/assets\/social-og\.png/);
  assert.match(html, /assets\/favicon\.svg/);
});
