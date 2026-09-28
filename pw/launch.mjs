import { chromium } from 'playwright';
const b = await chromium.launch();
const p = await b.newPage();
await p.setContent('<p>ok</p>');
console.log('launched', b.version(), await p.textContent('p'));
const gl = await p.evaluate(() => { const c=document.createElement('canvas'); const g=c.getContext('webgl'); if(!g) return 'no-webgl'; const e=g.getExtension('WEBGL_debug_renderer_info'); return e? g.getParameter(e.UNMASKED_RENDERER_WEBGL):'webgl'; });
console.log('renderer', gl);
await b.close();
