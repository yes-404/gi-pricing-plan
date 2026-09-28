// Control: the same 240-wheel loop and 800-move drag on a blank page, with no Vue Flow.
import { chromium } from 'playwright';
const b = await chromium.launch(); const page = await b.newPage({ viewport: { width: 1600, height: 900 } });
await page.setContent('<div id=d style="width:100vw;height:100vh"></div><script>let n=0;addEventListener("wheel",e=>{n++;document.getElementById("d").style.transform="scale("+(1+(n%10)/100)+")"},{passive:true});addEventListener("mousemove",e=>{document.getElementById("d").style.transform="translateX("+(e.clientX%50)+"px)"})</script>');
for (const [name, act] of [['wheel', async () => { await page.mouse.move(800, 450); for (let i = 0; i < 240; i++) await page.mouse.wheel(0, 25); }], ['drag', async () => { await page.mouse.move(300, 300); await page.mouse.down(); await page.mouse.move(800, 600, { steps: 400 }); await page.mouse.move(300, 300, { steps: 400 }); await page.mouse.up(); }]]) {
  await b.startTracing(page, { categories: ['disabled-by-default-devtools.timeline.frame'] });
  const t0 = Date.now(); await act(); const wall = Date.now() - t0;
  const ev = JSON.parse((await b.stopTracing()).toString()).traceEvents; const d = ev.filter((e) => e.name === 'DrawFrame').map((e) => e.ts).sort((a, c) => a - c);
  console.log('F2-CONTROL ' + JSON.stringify({ name, wall, DrawFrame: d.length, drawFps: +(1000 * (d.length - 1) / ((d[d.length - 1] - d[0]) / 1e3)).toFixed(1) }));
}
await b.close();
