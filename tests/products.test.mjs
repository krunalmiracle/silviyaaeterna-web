import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {test} from 'node:test';
const manifest=JSON.parse(await readFile(new URL('../tools/ORIFLAME-PRODUCTS.json',import.meta.url),'utf8'));
const html=await readFile(new URL('../index.html',import.meta.url),'utf8');
const hash=b=>createHash('sha256').update(b).digest('hex');
test('eight individually sourced Oriflame Bulgaria products, images and displayed prices match the evidence',async()=>{
 assert.equal(manifest.market,'Bulgaria');assert.equal(manifest.currency,'EUR');
 assert.equal(manifest.count,8);assert.equal(manifest.products.length,8);
 assert.equal(new Set(manifest.products.map(p=>p.code)).size,8);
 for(const p of manifest.products){
  assert.match(p.code,/^\d{5}$/);assert.equal(p.availability,'InStock');
  assert.equal(p.product_url,'https://bg.oriflame.com/products/product?code='+p.code);
  assert.match(p.image_source_url,/^https:\/\/media-cdn\.oriflame\.com\/productImage\?/);
  assert.match(p.image_source_url,new RegExp(p.code));
  assert.ok(p.verified_at.startsWith('2026-10-22T'));
  const bytes=await readFile(new URL('../'+p.image_file,import.meta.url));
  assert.equal(bytes.length,p.image_bytes);assert.equal(hash(bytes),p.image_sha256);
  assert.equal(bytes.toString('ascii',0,4),'RIFF');assert.equal(bytes.toString('ascii',8,12),'WEBP');
  const item=html.match(new RegExp(`<article class="product-card" data-sku="${p.code}">([\\s\\S]*?)</article>`))?.[1];
  assert.ok(item,'missing card '+p.code);
  assert.ok(item.includes(`href="${p.product_url}"`));
  assert.ok(item.includes(`src="${p.image_file}"`));
  assert.ok(item.includes(`€${p.price_eur}`));
  assert.ok(item.includes(`data-bg="${p.name_bg.replaceAll('&','&amp;').replaceAll('"','&quot;')}"`));
  assert.ok(item.includes(`data-en="${p.name_en}"`));
 }
 assert.match(html,/checked on 22 October 2026/);
 assert.match(html,/Prices and availability were checked/);
 assert.match(html,/check the final price, stock and delivery terms on Oriflame/);
 assert.match(html,/€10 annual partner fee, added to the first order/);
 assert.match(html,/There is no purchase minimum, and income is not guaranteed/);
 assert.match(html,/general Oriflame links, not personal referral links/);
});
