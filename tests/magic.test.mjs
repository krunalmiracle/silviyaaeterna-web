import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {test} from 'node:test';
const html = await readFile(new URL('../index.html',import.meta.url),'utf8');
test('six separate original scenes remain in the no-JS document',()=>{
 const ids=['hero-garden','skincare-ritual','psychology-journal','family-grove','mental-health-haven','closing-bloom'];
 for(const id of ids) assert.match(html,new RegExp('assets/images/'+id+'\\.webp'),id);
 assert.equal((html.match(/<img\b/g)||[]).length,6);
});
