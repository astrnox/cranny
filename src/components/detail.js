/* ============================================================
   detail.js · 详情浮层（README 预览 + 下载源）
   点击任意卡片 → 打开详情
   详情里：README iframe 预览 + 下载源 + 主操作按钮
   ============================================================ */

import { el, clear } from '../utils/dom.js';
import { badgeInfo } from './card.js';
import { UI } from '../utils/icons.js';

const I_CLOSE = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>`;
const I_DOC   = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/></svg>`;
const I_COPY  = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>`;
const I_DL    = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12M7 11l5 5 5-5M4 20h16"/></svg>`;

let overlay = null;
let panel = null;
let onActionCb = null;

function colorOf(id) {
  const P = ['#FF6B6B','#4ECDC4','#45B7D1','#96CEB4','#DDA0DD','#98D8C8','#F7DC6F','#BB8FCE','#85C1E9','#F0B27A','#52BE80','#EC7063'];
  let h = 0; for (const c of String(id)) h = (h * 31 + c.charCodeAt(0)) >>> 0;
  return P[h % P.length];
}

/**
 * 加载本地预渲染的 README（/readme/{id}.{lang}.html），自包含样式、零外网依赖。
 * 全部 README 在构建期由各仓库原文渲染并随站部署，彻底避免 GitHub API 限流与跨域白屏。
 * @param {HTMLIFrameElement} frame
 * @param {object} game
 * @param {'en'|'zh'} lang
 * @returns {Promise<boolean>} 是否成功
 */
async function loadReadmeInto(frame, game, lang = 'en') {
  const url = `readme/${encodeURIComponent(game.id)}.${lang}.html`;
  try {
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) return false;
    frame.srcdoc = await res.text();   // 本地自包含 HTML，直接注入
    return true;
  } catch {
    return false;
  }
}

function build() {
  overlay = el('div', { className: 'overlay', attrs: { hidden: '' } });
  panel = el('div', { className: 'detail' });
  overlay.appendChild(panel);
  document.body.appendChild(overlay);

  overlay.addEventListener('click', e => { if (e.target === overlay) closeDetail(); });
}

export function closeDetail() {
  if (!overlay || overlay.hidden) return;
  overlay.classList.remove('is-open');
  document.body.classList.remove('is-locked');
  setTimeout(() => { overlay.hidden = true; }, 280);
}

/** 复制工具 */
async function copyText(text, msg) {
  try { await navigator.clipboard.writeText(text); toast(msg, UI.check); }
  catch {
    const ta = document.createElement('textarea');
    ta.value = text; ta.style.cssText = 'position:fixed;opacity:0';
    document.body.appendChild(ta); ta.select();
    const ok = document.execCommand('copy'); ta.remove();
    toast(ok ? msg : '复制失败', ok ? UI.check : UI.warn);
  }
}

function toast(msg, icon) {
  // 简版：复用 detail 内的轻提示
  import('./toast.js').then(m => m.toast(msg, icon));
}

/**
 * @param {object} game
 * @param {object} ctx  { onAction }  主按钮行为由外部注入
 */
export function openDetail(game, { onAction } = {}) {
  if (!overlay) build();
  onActionCb = onAction;

  const badge = badgeInfo(game);
  const color = colorOf(game.id);
  const initial = (game.title || '?').trim().charAt(0).toUpperCase();

  /* 头部 */
  const cover = el('div', { className: 'detail__cover', style: { '--c': color } });
  cover.innerHTML = `${initial}<img src="${game.cover}" alt="" onerror="this.remove()">`;

  const head = el('div', { className: 'detail__head' }, [
    cover,
    el('div', { className: 'detail__head-text' }, [
      el('h2', { className: 'detail__title', text: game.title }),
      el('div', { className: 'detail__meta' }, [
        el('span', { className: `card__badge badge--${badge.key}`, text: badge.text, style: { position: 'static', height: '22px' } }),
        el('span', { className: 'card__badge', text: (game.platform || []).join(' / '), style: { position: 'static', background: 'var(--bg-sunken)', color: 'var(--text-secondary)', height: '22px' } }),
      ]),
    ]),
    (() => { const b = el('button', { className: 'detail__close', html: I_CLOSE, attrs: { type: 'button', 'aria-label': '关闭' } });
      b.addEventListener('click', closeDetail); return b; })(),
  ]);

  /* 正文 */
  const body = el('div', { className: 'detail__body' });

  if (game.desc) {
    body.appendChild(el('p', { className: 'detail__desc', text: game.desc }));
  }

  /* 下载源 */
  if (game.downloads?.length) {
    const dlWrap = el('div', { className: 'detail__dl' });
    game.downloads.forEach(src => {
      const sub = [src.size, src.version, src.code ? `提取码 ${src.code}` : null]
        .filter(Boolean).join(' · ');
      const copyBtn = el('button', { className: 'dl-row__copy', html: I_COPY, attrs: { type: 'button', 'aria-label': '复制链接' } });
      copyBtn.addEventListener('click', () =>
        copyText(src.code ? `${src.url} 提取码：${src.code}` : src.url, `${src.label} 已复制`));

      dlWrap.appendChild(el('div', { className: 'dl-row' }, [
        el('div', { className: 'dl-row__info' }, [
          el('div', { className: 'dl-row__label', text: src.label }),
          sub ? el('div', { className: 'dl-row__sub', html: `<span class="dl-row__code">${sub}</span>` }) : null,
        ]),
        copyBtn,
        el('a', { className: 'dl-row__go', html: `${I_DL}<span>下载</span>`, attrs: { href: src.url, target: '_blank', rel: 'noopener noreferrer' } }),
      ]));
    });
    body.appendChild(dlWrap);
  }

  /* README 预览：双语（默认英文，可切简体中文），加载本地预渲染 HTML */
  if (game.repo) {
    const langs = game.readmeLangs?.available?.length ? game.readmeLangs.available : ['en'];
    let curLang = game.readmeLangs?.default || langs[0];
    const LANGS = { en: 'English', zh: '简体中文' };

    const label = el('div', { className: 'readme-label' });
    label.innerHTML = `${I_DOC}<span>README 预览</span>`;

    const frameWrap = el('div', { className: 'readme-loading' });
    frameWrap.innerHTML = `<div class="spinner"></div><div>正在加载 README…</div>`;

    const frame = el('iframe', {
      className: 'readme-frame',
      attrs: { title: `${game.title} README`, loading: 'lazy',
                referrerpolicy: 'no-referrer', sandbox: 'allow-same-origin' },
    });
    frame.hidden = true;
    frame.addEventListener('load', () => {
      // 同步站点深浅色主题到 README 文档
      try {
        const siteTheme = document.documentElement.dataset.theme
          || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
        frame.contentDocument?.documentElement?.setAttribute('data-theme', siteTheme);
      } catch {}
      try {
        const h = frame.contentDocument?.body?.scrollHeight || 0;
        if (h) frame.style.height = Math.min(h + 24, 660) + 'px';
      } catch {}
      frame.hidden = false;
      if (frameWrap.isConnected) frameWrap.replaceWith(frame);
    });

    const showError = () => {
      frameWrap.innerHTML =
        `<div class="readme-error">该游戏暂未打包 README。<br>`
        + `<a href="${game.repo}" target="_blank" rel="noopener noreferrer">去 GitHub 查看</a></div>`;
    };

    /* 语言切换：默认英文，点「简体中文」切中文（仅一语种时不显示） */
    if (langs.length > 1) {
      const toggle = el('div', { className: 'readme-lang' });
      langs.forEach(l => {
        const b = el('button', {
          className: 'readme-lang__btn', text: LANGS[l] || l,
          attrs: { type: 'button', 'aria-selected': String(l === curLang) },
        });
        b.addEventListener('click', () => {
          if (l === curLang) return;
          curLang = l;
          toggle.querySelectorAll('.readme-lang__btn')
            .forEach(x => x.setAttribute('aria-selected', String(x === b)));
          frame.hidden = true;
          if (!frameWrap.isConnected) body.insertBefore(frameWrap, frame);
          frameWrap.innerHTML = `<div class="spinner"></div><div>正在加载 README…</div>`;
          loadReadmeInto(frame, game, curLang).then(ok => { if (!ok) showError(); });
        });
        toggle.appendChild(b);
      });
      label.appendChild(toggle);
    }

    body.append(label, frameWrap, frame);
    loadReadmeInto(frame, game, curLang).then(ok => { if (!ok) showError(); });
  }

  /* 底部操作 */
  const foot = el('div', { className: 'detail__foot' });
  const primaryLabel = { embed: '直接玩', redirect: '新窗口打开', download: '获取下载', repo: '打开仓库' }[game.mode] || '打开';
  const primaryIcon = game.mode === 'download' ? I_DL : game.mode === 'repo' ? I_REPO : I_DL;
  const primaryBtn = el('button', { className: 'btn btn--primary', html: `${primaryIcon}<span>${primaryLabel}</span>`, attrs: { type: 'button' } });
  primaryBtn.addEventListener('click', () => { onActionCb?.(game); });

  const repoBtn = el('a', { className: 'btn btn--outline', html: `${I_DOC}<span>仓库</span>`, attrs: { href: game.repo || '#', target: '_blank', rel: 'noopener noreferrer' } });

  foot.append(primaryBtn, repoBtn);

  clear(panel);
  panel.append(head, body, foot);

  overlay.hidden = false;
  document.body.classList.add('is-locked');
  requestAnimationFrame(() => overlay.classList.add('is-open'));
}

export function initDetail() {
  if (!overlay) build();
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && overlay && !overlay.hidden) closeDetail();
  });
}

const I_REPO = `<svg viewBox="0 0 16 16" fill="currentColor" width="18" height="18"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>`;
