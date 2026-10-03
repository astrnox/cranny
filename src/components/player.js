/* ============================================================
   player.js · 全屏游玩浮层
   降级面板（按需求）：主按钮「在新窗口打开」+
   次级卡片：GitHub 仓库链接 + 下载链接（若配置了）
   ============================================================ */

import { el } from '../utils/dom.js';
import { store } from '../core/storage.js';
import { UI } from '../utils/icons.js';

const LOAD_TIMEOUT = 8000;
const HINT_DELAY   = 4000;
const MIN_SPINNER  = 400;

const I_BACK  = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>`;
const I_FULL  = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 00-2 2v3M16 3h3a2 2 0 012 2v3M16 21h3a2 2 0 002-2v-3M8 21H5a2 2 0 01-2-2v-3"/></svg>`;
const I_FULLX = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3v3a2 2 0 01-2 2H3M16 3v3a2 2 0 002 2h3M16 21v-3a2 2 0 012-2h3M8 21v-3a2 2 0 00-2-2H3"/></svg>`;
const I_EXT   = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><path d="M15 3h6v6M10 14L21 3"/></svg>`;
const I_REPO  = `<svg viewBox="0 0 16 16" fill="currentColor" width="18" height="18"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>`;
const I_DL    = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12M7 11l5 5 5-5M4 20h16"/></svg>`;
const I_ARROW = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg>`;

let refs = null;
let current = null;
let timers = {};
let onCloseCb = null;

function build() {
  const backBtn = el('button', {
    className: 'player__back', html: `${I_BACK}<span>返回</span>`,
    attrs: { type: 'button', 'aria-label': '返回' },
  });
  const title = el('div', { className: 'player__title' });
  const fsBtn = el('button', {
    className: 'icon-btn', html: I_FULL,
    attrs: { type: 'button', 'aria-label': '全屏', title: '全屏（F）' },
  });
  const extBtn = el('button', {
    className: 'icon-btn', html: I_EXT,
    attrs: { type: 'button', 'aria-label': '新窗口打开', title: '新窗口打开' },
  });
  const bar = el('div', { className: 'player__bar' }, [backBtn, title, el('div', { className: 'player__actions' }, [fsBtn, extBtn])]);

  const loading = el('div', { className: 'player__loading', attrs: { hidden: '' } });
  loading.innerHTML = `<div class="spinner"></div><div class="player__loading-text">正在加载…</div>`;

  const frame = el('iframe', {
    className: 'player__frame',
    attrs: { referrerpolicy: 'no-referrer', allowfullscreen: '', allow: 'fullscreen; autoplay; gamepad', title: '游戏画面' },
  });

  const stage = el('div', { className: 'player__stage' }, [loading, frame]);
  const fallback = el('div', { className: 'player__fallback', attrs: { hidden: '' } });
  const hint = el('button', { className: 'player__hint', text: '打不开？点这里', attrs: { type: 'button' } });

  const root = el('div', { className: 'player', attrs: { hidden: '', role: 'dialog', 'aria-modal': 'true' } },
    [bar, stage, fallback, hint]);
  document.body.appendChild(root);

  return { root, backBtn, title, fsBtn, extBtn, loading, frame, stage, fallback, hint };
}

function clearTimers() { Object.values(timers).forEach(clearTimeout); timers = {}; }
function later(k, fn, ms) { clearTimeout(timers[k]); timers[k] = setTimeout(fn, ms); }

/* ------------------------------------------------------------
   降级面板：仓库 + 下载 + 打开
   ------------------------------------------------------------ */
function showFallback(reason) {
  clearTimers();
  refs.loading.hidden = true;
  refs.hint.classList.remove('is-visible');

  const copies = {
    timeout: { icon: UI.clock, title: '加载超时了', desc: '这个游戏可能在禁止嵌入，或者网络较慢。可以直接在新窗口打开，也可以去仓库看看。' },
    error:   { icon: UI.warn,  title: '加载出错', desc: '站内嵌入失败了。试试新窗口打开，或者去仓库查看详情。' },
    manual:  { icon: UI.wrench, title: '没正常显示？', desc: '有些游戏会禁止被其他网站嵌入。换到新窗口打开通常就能解决。' },
  };
  const c = copies[reason] || copies.manual;

  /* 主操作 */
  const actions = [el('button', {
    className: 'btn btn--primary', html: `${I_EXT}<span>在新窗口打开</span>`,
    attrs: { type: 'button' },
    on: { click: () => window.open(current.url, '_blank', 'noopener,noreferrer') },
  })];

  /* 次级：仓库 + 下载 */
  const links = [];
  if (current.repo) {
    links.push(linkCard({
      icon: I_REPO, label: 'GitHub 仓库', sub: '查看源码 / README',
      href: current.repo, isRepo: true,
    }));
  }
  if (current.downloads?.length) {
    const d = current.downloads[0];
    links.push(linkCard({
      icon: I_DL, label: `下载${current.mode === 'download' ? '' : '资源'}`,
      sub: d.size || d.label || '获取文件', href: d.url, isDownload: true,
    }));
  }

  refs.fallback.innerHTML = '';
  refs.fallback.appendChild(el('div', { className: 'fb__wrap' }, [
    el('div', { className: `fb__icon${reason === 'manual' ? ' fb__icon--info' : ''}`, html: c.icon }),
    el('h2', { className: 'fb__title', text: c.title }),
    el('p',  { className: 'fb__desc',  text: c.desc }),
    el('div', { className: 'fb__actions' }, actions),
    links.length ? el('div', { className: 'fb__links' }, links) : null,
  ]));
  refs.fallback.hidden = false;

  if (current && reason !== 'manual') {
    store.setEmbedResult(current.id, reason === 'timeout' ? 'blocked' : 'error');
  }
}

function linkCard({ icon, label, sub, href, isRepo, isDownload }) {
  const node = el('a', {
    className: 'fb__link',
    attrs: { href, target: '_blank', rel: 'noopener noreferrer' },
  });
  node.innerHTML = `
    <span class="fb__link-icon">${icon}</span>
    <span class="fb__link-body">
      <span class="fb__link-label">${label}</span>
      <span class="fb__link-sub">${sub}</span>
    </span>
    <span class="fb__link-arrow">${I_ARROW}</span>`;
  return node;
}

/* ------------------------------------------------------------
   打开 / 关闭
   ------------------------------------------------------------ */
export function openPlayer(game, { onClose } = {}) {
  if (!refs) refs = build();
  onCloseCb = onClose;
  current = game;

  refs.title.textContent = game.title;
  refs.root.hidden = false;
  refs.root.setAttribute('aria-label', `${game.title} 游玩窗口`);
  document.body.classList.add('is-locked');
  refs.loading.hidden = false;
  refs.loading.classList.remove('is-done');
  refs.fallback.hidden = true;
  refs.hint.classList.remove('is-visible');

  if (store.isKnownBlocked(game.id)) {
    refs.frame.src = 'about:blank';
    showFallback('manual');
  } else {
    refs.frame.src = game.url;
    let loaded = false;
    const start = Date.now();

    refs.frame.addEventListener('load', () => {
      loaded = true;
      clearTimeout(timers.timeout);
      later('done', () => refs.loading.classList.add('is-done'), Math.max(0, MIN_SPINNER - (Date.now() - start)));
      later('hint', () => { if (!refs.root.hidden && refs.fallback.hidden) refs.hint.classList.add('is-visible'); }, HINT_DELAY);
    }, { once: true });

    refs.frame.addEventListener('error', () => { if (!loaded) showFallback('error'); }, { once: true });
    later('timeout', () => { if (!loaded) showFallback('timeout'); }, LOAD_TIMEOUT);
  }

  store.pushRecent(game.id);
  store.bumpPlay(game.id);
  requestAnimationFrame(() => refs.root.classList.add('is-open'));
}

export function closePlayer() {
  if (!refs || refs.root.hidden) return;
  clearTimers();
  refs.root.classList.remove('is-open');
  document.body.classList.remove('is-locked');
  later('teardown', () => {
    refs.root.hidden = true;
    refs.frame.src = 'about:blank';
    refs.fallback.hidden = true;
    refs.hint.classList.remove('is-visible');
  }, 300);
  onCloseCb?.();
  current = null;
}

export function initPlayer() {
  if (!refs) refs = build();
  refs.backBtn.addEventListener('click', closePlayer);
  refs.hint.addEventListener('click', () => showFallback('manual'));
  refs.extBtn.addEventListener('click', () => current?.url && window.open(current.url, '_blank', 'noopener,noreferrer'));

  refs.fsBtn.addEventListener('click', () => {
    if (document.fullscreenElement) document.exitFullscreen?.().catch(() => {});
    else refs.stage.requestFullscreen?.().catch(() => {});
  });
  document.addEventListener('fullscreenchange', () => {
    if (refs) refs.fsBtn.innerHTML = document.fullscreenElement ? I_FULLX : I_FULL;
  });

  document.addEventListener('keydown', e => {
    if (!refs || refs.root.hidden) return;
    if (e.key === 'Escape') { if (!document.fullscreenElement) { e.preventDefault(); closePlayer(); } }
    else if ((e.key === 'f' || e.key === 'F') && e.target.tagName !== 'INPUT') { e.preventDefault(); refs.fsBtn.click(); }
  });
}
