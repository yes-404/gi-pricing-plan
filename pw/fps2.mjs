// SPIKE F2 fps instrument v2: presented frames = Chrome trace DrawFrame events; each action is
// checked to have moved the viewport; input is sent faster than a frame so input is not the cap.
import { chromium } from 'playwright';
const URL = process.argv[2];
const b = await chromium.launch();
const page = await b.newPage({ viewport: { width: 1600, height: 900 } });
await page.goto(URL);
await page.waitForFunction(() => document.querySelectorAll('.vue-flow__node').length === 200 && window.__f2SetViewport);
await page.waitForTimeout(500);
const tf = () => page.evaluate(() => getComputedStyle(document.querySelector('.vue-flow__transformationpane')).transform);
const reset = () => page.evaluate(() => window.__f2SetViewport({ x: 400, y: 40, zoom: 0.17 }));
async function traced(name, action) {
  await reset(); await page.waitForTimeout(300);
  await b.startTracing(page, { categories: ['disabled-by-default-devtools.timeline.frame', 'devtools.timeline'] });
  await page.evaluate(() => { window.__tfs = new Set(); const el = document.querySelector('.vue-flow__transformationpane'); window.__mo = new MutationObserver(() => window.__tfs.add(el.style.transform)); window.__mo.observe(el, { attributes: true, attributeFilter: ['style'] }); });
  const before = await tf(); const t0 = Date.now(); await action(); const wall = Date.now() - t0; const after = await tf(); const distinct = await page.evaluate(() => { window.__mo.disconnect(); return window.__tfs.size; });
  const ev = JSON.parse((await b.stopTracing()).toString()).traceEvents;
  const draws = ev.filter((e) => e.name === 'DrawFrame').map((e) => e.ts).sort((a, c) => a - c);
  const span = draws.length > 1 ? (draws[draws.length - 1] - draws[0]) / 1e3 : 0;
  const gaps = draws.slice(1).map((t, i) => (t - draws[i]) / 1e3).sort((a, c) => a - c);
  const q = (p) => gaps.length ? +gaps[Math.min(gaps.length - 1, Math.floor(p * gaps.length))].toFixed(1) : null;
  const r = { name, wall, distinctTransforms: distinct, DrawFrame: draws.length, spanMs: Math.round(span),
    drawFps: span ? +(1000 * (draws.length - 1) / span).toFixed(1) : null, gapP50: q(0.5), gapP95: q(0.95), gapMax: q(1),
    DroppedFrame: ev.filter((e) => e.name === 'DroppedFrame').length };
  console.log('F2-FPS ' + JSON.stringify(r));
}
// Pan point: must be the pane itself.
const pt = await page.evaluate(() => { const r = document.querySelector('.vue-flow').getBoundingClientRect(); for (let y = r.y + 20; y < Math.min(r.bottom, innerHeight) - 20; y += 20) for (let x = r.x + 20; x < r.right - 20; x += 20) { const e = document.elementFromPoint(x, y); if (e && e.classList.contains('vue-flow__pane')) return [x, y]; } return null; });
console.log('F2-PANPOINT ' + JSON.stringify(pt));
await traced('pan-drag', async () => { await page.mouse.move(pt[0], pt[1]); await page.mouse.down(); await page.mouse.move(pt[0] + (pt[0] > 800 ? -500 : 500), pt[1] + (pt[1] > 450 ? -300 : 300), { steps: 400 }); await page.mouse.move(pt[0], pt[1], { steps: 400 }); await page.mouse.up(); });
await traced('zoom-wheel', async () => { await page.mouse.move(pt[0], pt[1]); for (let i = 0; i < 240; i++) await page.mouse.wheel(0, (Math.floor(i / 30) % 2 ? 25 : -25)); });
await traced('viewport-transition-3s', async () => { await page.evaluate(() => window.__f2SetViewport({ x: -600, y: -900, zoom: 1.2 }, { duration: 3000 })); });
await b.close();
