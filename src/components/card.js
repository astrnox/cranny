/* ============================================================
   card.js · Poki 风格游戏卡片
   ============================================================ */

import { el } from '../utils/dom.js';

const STAR = `
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
       stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path d="M12 2l2.9 6.3 6.9.8-5.1 4.7 1.4 6.8L12 17l-6.1 3.6 1.4-6.8L2.2 9.1l6.9-.8z"/>
  </svg>`;
const STAR_FILLED = `
  <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
    <path d="M12 2l2.9 6.3 6.9.8-5.1 4.7 1.4 6.8L12 17l-6.1 3.6 1.4-6.8L2.2 9.1l6.9-.8z"/>
  </svg>`;

/** 封面调色板：暖向多彩，刻意避开蓝/紫 */
const PALETTE = [
  '#FF6B4A', '#FFB23E', '#2FBF71', '#18BFBF', '#FF5C8A',
  '#F2C14E', '#E5484D', '#8BD450', '#FF8A3D', '#36C5A0',
  '#FF7A59', '#37B24D', '#F08C2E', '#0FA3A3', '#E64980',
];

/** 占位封面仅作兜底：真实 SVG 封面就绪后基本不出现 */

function colorOf(id) {
  let hash = 0;
  for (const ch of String(id)) hash = (hash * 31 + ch.charCodeAt(0)) >>> 0;
  return PALETTE[hash % PALETTE.length];
}

// 需下载游戏的角标：安卓优先，其次按 platform 里的真实操作系统标，
// 别一律写「PC」——下载页要靠这个区分 Windows / Linux / macOS。
const OS_BADGE = [
  ['win', 'Windows', 'win'],
  ['lin', 'Linux', 'lin'],
  ['mac', 'macOS', 'mac'],
];

export function badgeInfo(game) {
  if (game.status === 'broken') return { key: 'broken', text: '暂不可用' };
  if (game.mode === 'download') {
    const plats = game.platform || [];
    const desk = OS_BADGE.filter(([p]) => plats.includes(p));
    const hasAndroid = plats.includes('android');
    // 只有一个桌面系统 → 直接写名字，用户能少点一次下载页
    if (!hasAndroid && desk.length === 1) {
      return { key: desk[0][2], text: desk[0][1] };
    }
    if (hasAndroid && desk.length) return { key: 'android', text: '安卓+电脑' };
    if (hasAndroid) return { key: 'android', text: '安卓' };
    if (desk.length > 1) return { key: 'pc', text: '跨平台' };
    return { key: 'pc', text: '电脑版' };
  }
  if (game.mode === 'embed') return { key: 'play', text: '直接玩' };
  if (game.mode === 'repo')   return { key: 'repo', text: '看仓库' };
  return { key: 'open', text: '新窗口' };
}

/**
 * @param {object} game
 * @param {object} ctx  { isFav, onFav, onOpen }
 */
export function createCard(game, ctx = {}) {
  const { isFav = false, onFav, onOpen } = ctx;
  const badge = badgeInfo(game);
  const color = colorOf(game.id);
  const initial = (game.title || '?').trim().charAt(0).toUpperCase();

  /* 收藏星 */
  const star = el('button', {
    className: `card__star${isFav ? ' is-active' : ''}`,
    html: isFav ? STAR_FILLED : STAR,
    attrs: {
      type: 'button',
      'aria-label': isFav ? `取消收藏 ${game.title}` : `收藏 ${game.title}`,
      'aria-pressed': String(isFav),
    },
  });
  star.addEventListener('click', e => {
    e.stopPropagation();
    const now = onFav?.(game.id);
    star.classList.toggle('is-active', Boolean(now));
    star.innerHTML = now ? STAR_FILLED : STAR;
    star.setAttribute('aria-pressed', String(Boolean(now)));
    star.setAttribute('aria-label', `${now ? '取消收藏' : '收藏'} ${game.title}`);
  });

  /* 封面（真实 SVG 封面 + 可选占位兜底，真实图淡入） */
  const cover = el('div', {
    className: 'card__cover',
    style: { '--c': color },
  });
  cover.innerHTML = `
    <div class="card__placeholder" aria-hidden="true">${initial}</div>
    <img class="card__img" alt="" loading="lazy" decoding="async"
         src="${game.cover}" style="opacity:0;transition:opacity var(--dur-3) var(--ease-out)"
         onload="this.style.opacity=1" onerror="this.remove()">`;

  /* 信息区 */
  const info = el('div', { className: 'card__info' }, [
    el('h3', { className: 'card__title', text: game.title }),
    el('p', { className: 'card__desc', text: game.desc || '' }),
  ]);

  const card = el('button', {
    className: 'card',
    attrs: {
      type: 'button',
      'aria-label': `${game.title}，${badge.text}`,
    },
    dataset: {
      id: game.id,
      ...(game.status === 'broken' ? { status: 'broken' } : {}),
    },
  }, [
    cover,
    el('span', { className: `card__badge badge--${badge.key}`, text: badge.text }),
    star,
    info,
  ]);

  card.addEventListener('click', () => onOpen?.(game));
  return card;
}

/** 骨架卡片（加载中：封面与文字条都有微光扫过动画） */
export function createSkeletonCard() {
  return el('div', { className: 'card card--skeleton' }, [
    el('div', { className: 'card__cover card__cover--sk' }),
    el('div', { className: 'card__info' }, [
      el('div', { className: 'skeleton', style: { height: '18px', width: '70%', marginBottom: '10px' } }),
      el('div', { className: 'skeleton', style: { height: '13px', width: '45%' } }),
    ]),
  ]);
}
