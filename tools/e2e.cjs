/* 端到端验证：真实浏览器里跑一遍新 UI
 *
 * 默认打本地 http://localhost:8899/（先 python3 -m http.server 8899）。
 * 传参可打线上：node tools/e2e.cjs http://cranny.bbroot.com/
 */
const { chromium } = require('playwright');

const BASE = (process.argv[2] || 'http://localhost:8899/').replace(/\/?$/, '/');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errors = [];
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', e => errors.push('PAGEERROR: ' + e.message));
  const bad = [];
  page.on('response', r => { if (r.status() >= 400) bad.push(`${r.status()} ${r.url()}`); });

  await page.goto(BASE, { waitUntil: 'networkidle' });
  await page.waitForSelector('.card', { timeout: 8000 });

  const snap = async label => {
    const s = await page.evaluate(() => ({
      sub: document.querySelector('#pageSub')?.textContent,
      title: document.querySelector('#gridTitle')?.textContent,
      count: document.querySelector('#gridCount')?.textContent,
      cards: document.querySelectorAll('#grid .card').length,
      pills: document.querySelectorAll('#pills .pill').length,
    }));
    console.log(`${label.padEnd(22)} 卡片=${String(s.cards).padStart(3)} 分类=${String(s.pills).padStart(2)} | ${s.title} · ${s.count}`);
    return s;
  };

  console.log('=== 初始 ===');
  const base = await snap('全部');

  // 展开细筛
  await page.click('#facetsToggle');
  await page.waitForSelector('#facetsBody:not([hidden])');
  const facetOpts = await page.evaluate(() => ({
    embed: [...document.querySelectorAll('#embedOpts .opt')].map(b => b.textContent.trim()),
    license: [...document.querySelectorAll('#licenseOpts .opt')].map(b => b.textContent.trim()),
  }));
  console.log('\n=== 细筛选项 ===');
  console.log('  怎么玩:', facetOpts.embed.join(' | '));
  console.log('  许可证:', facetOpts.license.join(' | '));

  console.log('\n=== 细筛：站内直接玩 ===');
  await page.click('#embedOpts .opt:first-child');
  await page.waitForTimeout(150);
  await snap('站内可玩');
  console.log('  badge:', await page.textContent('#facetsBadge'),
              '| 标题应为带「站内可玩」:', (await page.textContent('#gridTitle')).includes('站内可玩'));

  console.log('\n=== 叠加许可证：宽松 ===');
  await page.click('#licenseOpts .opt:first-child');
  await page.waitForTimeout(150);
  await snap('站内可玩 + 宽松');
  console.log('  badge:', await page.textContent('#facetsBadge'));

  console.log('\n=== 需下载 tab ===');
  await page.click('#facetsReset');
  await page.click('.segmented__item[data-tab="local"]');
  await page.waitForTimeout(200);
  const dl = await snap('需下载');
  const dlBadges = await page.evaluate(() => [...document.querySelectorAll('#grid .card__badge')].map(b => b.textContent).slice(0, 5));
  console.log('  角标样例:', dlBadges.join(' '), '| 细筛是否被清:', await page.getAttribute('#facetsBadge', 'hidden') !== null);

  console.log('\n=== 分类药丸点击 ===');
  await page.click('.segmented__item[data-tab="all"]');
  await page.waitForTimeout(150);
  await page.click('#pills .pill:nth-child(4)');
  await page.waitForTimeout(150);
  await snap('分类筛选');

  console.log('\n=== 搜索 ===');
  await page.click('.segmented__item[data-tab="all"]');
  await page.fill('#search', 'tetris');
  await page.waitForTimeout(200);
  await snap('搜 tetris');
  const hits = await page.evaluate(() => [...document.querySelectorAll('#grid .card__title')].map(t => t.textContent));
  console.log('  命中:', hits.join(' / '));

  console.log('\n=== 详情页许可证展示 ===');
  await page.fill('#search', 'mindustry');
  await page.waitForTimeout(200);
  await page.click('#grid .card');
  await page.waitForSelector('.detail:not([hidden]), .overlay.is-open', { timeout: 5000 });
  await page.waitForTimeout(400);
  const detail = await page.evaluate(() => ({
    title: document.querySelector('.detail__title')?.textContent,
    tags: [...document.querySelectorAll('.detail__meta .tag')].map(t => t.textContent),
    desc: document.querySelector('.detail__desc')?.textContent,
    license: document.querySelector('.license__name')?.textContent,
    flags: [...document.querySelectorAll('.license__flags .flag')].map(f => f.textContent.trim()),
    caveats: [...document.querySelectorAll('.caveat')].map(c => c.textContent.trim().slice(0, 40)),
  }));
  console.log('  标题:', detail.title);
  console.log('  标签:', detail.tags.join(' | '));
  console.log('  许可证:', detail.license, '|', detail.flags.join(' / '));
  if (detail.caveats.length) console.log('  注意事项:', detail.caveats.join(' / '));

  // 下载源只在「需下载」类游戏里有，单独开一个 0 A.D. 来看
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);
  await page.fill('#search', '0 A.D.');
  await page.waitForTimeout(300);
  await page.click('#grid .card');
  await page.waitForSelector('.detail:not([hidden]), .overlay.is-open', { timeout: 5000 });
  await page.waitForTimeout(500);
  const dlRows = await page.evaluate(() =>
    [...document.querySelectorAll('.dl-row__label')].map(e => e.textContent.trim()));
  console.log('  下载源:', dlRows.length ? dlRows.join(' / ') : '（无）');

  console.log('\n=== 封面图加载情况 ===');
  const covers = await page.evaluate(() => {
    const imgs = [...document.querySelectorAll('.card__img')];
    const ok = imgs.filter(i => i.naturalWidth > 0);
    const ph = document.querySelectorAll('.card__placeholder').length;
    return { total: imgs.length, loaded: ok.length, placeholders: ph };
  });
  console.log(`  共 ${covers.total} 张，加载成功 ${covers.loaded}，占位符残留 ${covers.placeholders}`);

  console.log('\n=== 固定高度控件是否换行 ===');
  // 「下载」两个字被折成两行（height 固定 + 容器窄）是这站反复出现的坑。
  // 注意不能靠量 offsetHeight 判：这些控件写死了 height，文字换行时盒子不会变高，
  // 只会溢出。正确做法是用 Range 数文本节点占了几行。
  const wrapped = await page.evaluate(() => {
    const SEL = ['.dl-row__go', '.pill', '.opt', '.facets__toggle', '.btn'];
    const bad = [];

    // 量「一个元素里的文字占了几行」：逐个子节点分别量，
    // 不能把整个元素一起量——.opt 里 label 和计数是两个并排的 span，
    // 合起来量会把并排误判成换行。
    const lineCountOf = node => {
      const r = document.createRange();
      r.selectNodeContents(node);
      const tops = new Set();
      for (const rect of r.getClientRects()) {
        if (rect.height > 0) tops.add(Math.round(rect.top));
      }
      return tops.size;
    };

    for (const sel of SEL) {
      for (const el of document.querySelectorAll(sel)) {
        if (el.offsetHeight === 0) continue;              // 隐藏的跳过
        for (const node of el.childNodes) {
          if (node.nodeType !== Node.TEXT_NODE && node.nodeType !== Node.ELEMENT_NODE) continue;
          if (!node.textContent.trim()) continue;          // 纯图标 svg 跳过
          if (node.nodeType === Node.ELEMENT_NODE
              && ![...node.childNodes].some(c => c.nodeType === Node.TEXT_NODE && c.textContent.trim())) {
            continue;                                      // 容器本身不直接含文字
          }
          if (lineCountOf(node) > 1) {
            bad.push(`${sel}「${node.textContent.trim().slice(0, 10)}」`);
            break;
          }
        }
      }
    }
    return bad;
  });
  console.log(wrapped.length ? '  ✗ 换行: ' + wrapped.slice(0, 6).join('; ')
                              : '  全部单行 ✓');

  console.log('\n=== 错误汇总 ===');
  console.log('  JS 错误:', errors.length ? errors.slice(0, 5) : '无 ✓');
  console.log('  4xx/5xx:', bad.length ? bad.slice(0, 8) : '无 ✓');

  await page.screenshot({ path: '/tmp/shot-list.png', fullPage: false });
  await page.click('.detail__close');
  await page.waitForTimeout(300);
  await page.click('#facetsToggle');
  await page.screenshot({ path: '/tmp/shot-facets.png' });

  await browser.close();
})();
