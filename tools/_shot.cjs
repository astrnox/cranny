const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 900, height: 1000 } });
  for (const [name, url] of [
    ['card', 'http://localhost:8899/readme/candy-box-2.en.html'],
    ['real', 'http://localhost:8899/readme/openra.en.html'],
  ]) {
    await p.goto(url, { waitUntil: 'networkidle' });
    await p.screenshot({ path: `/tmp/rm_${name}.png` });
  }
  await b.close();
})();
