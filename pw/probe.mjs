import { chromium } from 'playwright';
const b = await chromium.launch(); const page = await b.newPage({ viewport: { width: 1600, height: 900 } });
await page.goto(process.argv[2]); await page.waitForFunction(() => document.querySelectorAll('.vue-flow__node').length === 200);
console.log(JSON.stringify(await page.evaluate(() => [[1560,120],[1560,450],[40,450],[800,20],[8,890]].map(([x,y]) => { const e = document.elementFromPoint(x,y); return [x,y,e?.tagName, e?.className?.baseVal ?? e?.className]; }))));
console.log(JSON.stringify(await page.evaluate(() => { const r = document.querySelector('.vue-flow').getBoundingClientRect(); return [r.x,r.y,r.width,r.height]; })));
await b.close();
