import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { test } from 'node:test';
import vm from 'node:vm';
import { createHash } from 'node:crypto';
const source = await readFile(new URL('../assets/site.js', import.meta.url), 'utf8');
const html = await readFile(new URL('../index.html', import.meta.url), 'utf8');

function fixture(saved = 'en', denyStorage = false, hash = '') {
  class Element {
    constructor(dataset = {}) { this.dataset = dataset; this.attrs = {}; this.events = {}; this.open = false; }
    setAttribute(key, value) { this.attrs[key] = value; }
    getAttribute(key) { return this.attrs[key] ?? null; }
    removeAttribute(key) { delete this.attrs[key]; }
    addEventListener(key, fn) { this.events[key] = fn; }
    focus() { this.focused = true; }
    click() { this.events.click?.({ target: this }); }
  }
  const root = new Element();
  const en = new Element(), bg = new Element();
  const text = new Element({en: 'A little more', bg: 'По-близо'});
  const image = new Element(); image.attrs = {'data-alt-en': 'Leaves', 'data-alt-bg': 'Листа'};
  const nav = new Element(); nav.attrs = {'data-aria-en': 'Primary', 'data-aria-bg': 'Основна навигация'};
  const menu = new Element(), summary = new Element(), menuLink = new Element();
  menu.querySelector = () => summary;
  menu.querySelectorAll = () => [menuLink];
  menu.contains = el => el === menu || el === summary || el === menuLink;
  const ids=['skincare', 'wellbeing', 'family', 'mental-health'];
  const topics = Object.fromEntries(ids.map(id => { const e = new Element(); e.details = new Element(); e.querySelector = () => e.details; return [id,e]; }));
  const links = ids.map(theme => new Element({theme}));
  const docEvents = {}, winEvents = {};
  const storage = new Map([['sa-lang', saved]]);
  const document = {
    documentElement: root,
    querySelector: () => menu,
    getElementById: id => ({'lang-en': en, 'lang-bg': bg, ...topics}[id]),
    querySelectorAll: selector => ({'[data-en][data-bg]': [text], '[data-alt-en][data-alt-bg]': [image], '[data-aria-en][data-aria-bg]': [nav], '[data-theme]': links}[selector] || []),
    addEventListener: (key, fn) => { docEvents[key] = fn; },
  };
  vm.runInNewContext(source, {document, window: {addEventListener: (key, fn) => {winEvents[key] = fn;}}, location: {hash}, localStorage: {
    getItem: key => { if (denyStorage) throw Error('denied'); return storage.get(key); },
    setItem: (key, value) => { if (denyStorage) throw Error('denied'); storage.set(key, value); }
  }});
  return {root, en, bg, text, image, nav, menu, summary, menuLink, topics, links, storage, docEvents, winEvents};
}

test('saved Bulgarian preference applies content, lang, translated aria and image alt', () => {
  const f = fixture('bg');
  assert.equal(f.root.lang, 'bg'); assert.equal(f.text.textContent, 'По-близо');
  assert.equal(f.bg.attrs['aria-pressed'], 'true'); assert.equal(f.en.attrs['aria-pressed'], 'false');
  assert.equal(f.image.alt, 'Листа'); assert.equal(f.nav.attrs['aria-label'], 'Основна навигация');
  f.en.click(); assert.equal(f.storage.get('sa-lang'), 'en'); assert.equal(f.text.textContent, 'A little more');
});
test('invalid preference and denied storage retain functional English and language toggle', () => {
  assert.equal(fixture('invalid').root.lang, 'en');
  const f = fixture('bg', true); assert.equal(f.root.lang, 'en'); f.bg.click(); assert.equal(f.root.lang, 'bg');
});
test('mobile menu closes on selection', () => {
  const f = fixture(); f.menu.open = true; f.menuLink.click(); assert.equal(f.menu.open, false);
});
test('mobile menu closes on Escape and restores summary focus', () => {
  const f = fixture(); f.menu.open = true; f.docEvents.keydown({key: 'Escape'});
  assert.equal(f.menu.open, false); assert.equal(f.summary.focused, true);
});
test('outside click closes mobile menu but inside click does not', () => {
  const f = fixture(); f.menu.open = true; f.docEvents.click({target: f.summary}); assert.equal(f.menu.open, true);
  f.docEvents.click({target: f.bg}); assert.equal(f.menu.open, false);
});
test('all four theme selections open useful prompts with selected aria and focus', () => {
  const f = fixture();
  for (const link of f.links) {
    link.click(); assert.equal(link.attrs['aria-current'], 'true');
    assert.equal(f.links.filter(l => l.attrs['aria-current'] === 'true').length, 1);
    assert.equal(f.topics[link.dataset.theme].details.open, true);
    assert.equal(f.topics[link.dataset.theme].focused, true);
  }
});
test('direct theme fragment enhances the correct topic', () => {
  const f = fixture('en', false, '#mental-health');
  assert.equal(f.topics['mental-health'].details.open, true);
  assert.equal(f.links[3].attrs['aria-current'], 'true');
});
test('four static descriptions and native prompt disclosures exist without JavaScript', () => {
  for (const id of ['skincare', 'wellbeing', 'family', 'mental-health']) {
    const article = html.match(new RegExp(`<article[^>]+id="${id}"[\\s\\S]*?</article>`))?.[0];
    assert.ok(article, id); assert.match(article, /<h3 data-en=/); assert.match(article, /<p data-en=/); assert.match(article, /<details class="reflection">/);
  }
  assert.equal((html.match(/class="reflection"/g) || []).length, 4);
});
test('original images and responsive hero are real WebP assets', async () => {
  const manifest = JSON.parse(await readFile(new URL('../tools/ASSET-MANIFEST.json', import.meta.url), 'utf8'));
  assert.equal(manifest.asset_count, 6);
  for (const asset of manifest.assets) {
    const bytes = await readFile(new URL(`../assets/images/${asset.filename}`, import.meta.url));
    assert.equal(createHash('sha256').update(bytes).digest('hex'), asset.sha256);
    const tag = [...html.matchAll(/<img\b[^>]*>/g)].map(m => m[0]).find(t => t.includes(`assets/images/${asset.filename}`));
    assert.ok(tag, `${asset.filename} is not integrated`);
    assert.ok(tag.includes(`width="${asset.width}" height="${asset.height}"`), 'intrinsic dimensions must match the original');
    assert.ok(tag.includes(`alt="${asset.alt.en}"`));
    assert.ok(tag.includes(`data-alt-bg="${asset.alt.bg}"`));
    assert.ok(asset.source_sha256 && asset.prompt && asset.source_path && asset.provider,
      'generated artwork must retain a sidecar provenance record');
    for (const derivative of asset.derivatives) {
      const optimized = await readFile(new URL(`../assets/images/${derivative.filename}`, import.meta.url));
      assert.equal(createHash('sha256').update(optimized).digest('hex'), derivative.sha256);
    }
  }
  for (const name of manifest.assets.flatMap(a => [a.id, a.id + '-small'])) {
    const bytes = await readFile(new URL(`../assets/images/${name}.webp`, import.meta.url));
    assert.equal(bytes.toString('ascii', 0, 4), 'RIFF'); assert.equal(bytes.toString('ascii', 8, 12), 'WEBP');
    assert.ok(bytes.length > 5000); assert.ok(bytes.length < 500000);
  }
  assert.match(html, /fetchpriority="high"/);
  assert.equal((html.match(/loading="lazy"/g) || []).length, 13);
});
test('social preview is a real 1200 by 630 PNG', async () => {
  const png = await readFile(new URL('../assets/social-og.png', import.meta.url));
  assert.equal(png.toString('ascii', 1, 4), 'PNG');
  assert.equal(png.readUInt32BE(16), 1200); assert.equal(png.readUInt32BE(20), 630);
});
