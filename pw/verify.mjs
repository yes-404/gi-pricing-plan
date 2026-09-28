// SPIKE F2 second instrument: viewport transform moves + Chrome trace frame counts.
import { chromium } from 'playwright';
const URL = process.argv[2];
const b = await chromium.launch();
const page = await b.newPage({ viewport: { width: 1600, height: 900 } });
await page.goto(URL);
await page.waitForFunction(() => document.querySelectorAll('.vue-flow__node').length === 200);
await page.waitForTimeout(500);
const tf = () => page.evaluate(() => getComputedStyle(document.querySelector('.vue-flow__transformationpane')).transform);
async function traced(name, action) {
  await b.startTracing(page, { categories: ['disabled-by-default-devtools.timeline.frame', 'devtools.timeline', 'disabled-by-default-devtools.timeline'] });
  const before = await tf(); const t0 = Date.now(); await action(); const wall = Date.now() - t0; const after = await tf();
  const buf = await b.stopTracing(); const ev = JSON.parse(buf.toString()).traceEvents;
  const count = (n) => ev.filter((e) => e.name === n).length;
  const draws = ev.filter((e) => e.name === 'DrawFrame').map((e) => e.ts).sort((a, c) => a - c);
  const span = draws.length > 1 ? (draws[draws.length - 1] - draws[0]) / 1e3 : 0;
  const gaps = draws.slice(1).map((t, i) => (t - draws[i]) / 1e3).sort((a, c) => a - c);
  console.log('F2-VERIFY ' + JSON.stringify({ name, wall, moved: before !== after, before, after,
    DrawFrame: draws.length, drawFps: span ? +(1000 * (draws.length - 1) / span).toFixed(1) : null,
    drawGapP95: gaps.length ? +gaps[Math.floor(0.95 * gaps.length)].toFixed(1) : null, drawGapMax: gaps.length ? +gaps[gaps.length - 1].toFixed(1) : null,
    DroppedFrame: count('DroppedFrame'), BeginMainThreadFrame: count('BeginMainThreadFrame'), Paint: count('Paint') }));
}
await traced('pan', async () => { await page.mouse.move(8, 890); await page.mouse.down(); for (let i = 1; i <= 120; i++) { await page.mouse.move(8 + i * 6, 890 - i * 3); await page.waitForTimeout(33); } await page.mouse.up(); });
await traced('zoom', async () => { await page.mouse.move(800, 450); for (let i = 0; i < 60; i++) { await page.mouse.wheel(0, i < 30 ? -120 : 120); await page.waitForTimeout(33); } });
await traced('zoom-in-only', async () => { await page.mouse.move(800, 450); for (let i = 0; i < 30; i++) { await page.mouse.wheel(0, -120); await page.waitForTimeout(33); } });
await b.close();
