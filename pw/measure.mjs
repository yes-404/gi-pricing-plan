// SPIKE F2: pan/zoom fps, keyboard focus+delete, and live isValidConnection timings,
// headless Chromium (SwiftShader software rendering) against the Vite DEV server.
import { chromium } from 'playwright';
const URL = process.argv[2]; const RUNS = Number(process.argv[3] ?? 5);
const b = await chromium.launch();
const results = [];
async function fps(page, action) {
  await page.evaluate(() => { window.__f = []; const tick = (t) => { window.__f.push(t); window.__raf = requestAnimationFrame(tick); }; window.__raf = requestAnimationFrame(tick); });
  const t0 = Date.now(); await action(); const wall = Date.now() - t0;
  const f = await page.evaluate(() => { cancelAnimationFrame(window.__raf); return window.__f; });
  const gaps = f.slice(1).map((t, i) => t - f[i]).sort((a, c) => a - c);
  const span = f[f.length - 1] - f[0];
  return { fps: +(1000 * (f.length - 1) / span).toFixed(1), frames: f.length, wallMs: wall,
    gapP95: +gaps[Math.floor(0.95 * gaps.length)].toFixed(1), gapMax: +gaps[gaps.length - 1].toFixed(1) };
}
for (let r = 0; r < RUNS; r++) {
  const page = await b.newPage({ viewport: { width: 1600, height: 900 } });
  const t0 = Date.now();
  await page.goto(URL);
  await page.waitForFunction(() => document.querySelectorAll('.vue-flow__node').length === 200 && document.querySelectorAll('.vue-flow__edge').length > 0);
  const loadMs = Date.now() - t0;
  const counts = await page.evaluate(() => ({ nodes: document.querySelectorAll('.vue-flow__node').length, edges: document.querySelectorAll('.vue-flow__edge').length }));
  await page.waitForTimeout(500);
  // Pan: drag the empty pane corner by 800 px over 120 moves (~4 s).
  const pan = await fps(page, async () => {
    await page.mouse.move(8, 890); await page.mouse.down();
    for (let i = 1; i <= 120; i++) { await page.mouse.move(8 + i * 6, 890 - i * 3); await page.waitForTimeout(33); }
    await page.mouse.up();
  });
  // Zoom: 60 wheel ticks in, then out, at the canvas centre (~4 s).
  const zoom = await fps(page, async () => {
    await page.mouse.move(800, 450);
    for (let i = 0; i < 60; i++) { await page.mouse.wheel(0, i < 30 ? -120 : 120); await page.waitForTimeout(33); }
  });
  // Live validation timings from a real drag: from constraint_19's source handle across every
  // visible target handle (Vue Flow calls isValidConnection while hovering handles).
  await page.evaluate(() => { window.__f2Timings = []; });
  const fit = page.locator('.vue-flow__controls-fitview'); if (await fit.count()) await fit.click();
  const src = page.locator('[data-id="s_constraint_19"] .vue-flow__handle.source');
  const sb = await src.boundingBox();
  const targets = await page.locator('.vue-flow__handle.target').evaluateAll((els) => els.slice(0, 400).map((e) => { const r = e.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; }));
  await page.mouse.move(sb.x + sb.width / 2, sb.y + sb.height / 2); await page.mouse.down();
  for (const [x, y] of targets) await page.mouse.move(x, y, { steps: 2 });
  await page.mouse.up();
  const tv = (await page.evaluate(() => window.__f2Timings)).sort((a, c) => a - c);
  const live = { calls: tv.length, p50: tv.length ? +tv[Math.floor(0.5 * tv.length)].toFixed(3) : null, p99: tv.length ? +tv[Math.floor(0.99 * tv.length)].toFixed(3) : null, max: tv.length ? +tv[tv.length - 1].toFixed(3) : null };
  // Keyboard: Tab to the first focusable node, Enter selects, Delete removes it and its edges.
  await page.mouse.click(1590, 10); // blur
  let focused = null;
  for (let i = 0; i < 40 && !focused; i++) { await page.keyboard.press('Tab'); focused = await page.evaluate(() => document.activeElement?.classList.contains('vue-flow__node') ? document.activeElement.getAttribute('data-id') : null); }
  let kb = { focused };
  if (focused) {
    const edgesBefore = await page.locator('.vue-flow__edge').count();
    await page.keyboard.press('Enter');
    const selected = await page.locator(`[data-id="${focused}"]`).evaluate((e) => e.classList.contains('selected'));
    await page.keyboard.press('Delete');
    await page.waitForTimeout(200);
    kb = { focused, selected, nodesAfter: await page.locator('.vue-flow__node').count(), stillPresent: await page.locator(`.vue-flow__node[data-id="${focused}"]`).count(), edgesBefore, edgesAfter: await page.locator('.vue-flow__edge').count() };
  }
  results.push({ run: r + 1, loadMs, counts, pan, zoom, live, kb });
  console.log('F2-RUN ' + JSON.stringify(results[results.length - 1]));
  await page.close();
}
await b.close();
