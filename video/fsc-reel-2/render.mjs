// Usage:
//   node render.mjs frames <outDir> [workers]   -> renders every frame as JPEG
//   node render.mjs stills <outDir> t1 t2 ...    -> renders selected timestamps (seconds)
import { createRequire } from 'module';
import { mkdirSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const require = createRequire(import.meta.url);
let pw;
try { pw = require('playwright'); } catch { pw = require('/opt/node-tools/node_modules/playwright'); }
const { chromium } = pw;

const here = path.dirname(fileURLToPath(import.meta.url));
const url = 'file://' + path.join(here, 'index.html');
const FPS = 30;
const [mode, outDir, ...rest] = process.argv.slice(2);
mkdirSync(outDir, { recursive: true });

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto(url);
  await page.evaluate(() => window.ready);
  return page;
}

const browser = await chromium.launch({ args: ['--disable-web-security', '--allow-file-access-from-files'] });
if (mode === 'stills') {
  const page = await openPage(browser);
  for (const t of rest.map(Number)) {
    await page.evaluate(t => window.seek(t), t);
    await page.screenshot({ path: path.join(outDir, `still_${t.toFixed(2)}.jpg`), type: 'jpeg', quality: 85 });
  }
} else {
  const workers = Number(rest[0] || 4);
  const dur = await (await openPage(browser)).evaluate(() => window.DURATION);
  const total = Math.round(dur * FPS);
  let done = 0;
  await Promise.all([...Array(workers)].map(async (_, w) => {
    const page = await openPage(browser);
    for (let f = w; f < total; f += workers) {
      await page.evaluate(t => window.seek(t), f / FPS);
      await page.screenshot({ path: path.join(outDir, `f${String(f).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 93 });
      if (++done % 90 === 0) console.log(`${done}/${total}`);
    }
  }));
  console.log('frames done', total);
}
await browser.close();
