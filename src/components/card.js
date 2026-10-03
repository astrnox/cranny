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

export function badgeInfo(game) {
  if (game.status === 'broken') return { key: 'broken', text: '暂不可用' };
  if (game.mode === 'download') {
    return (game.platform || []).includes('android')
      ? { key: 'android', text: '安卓' }
      : { key: 'pc', text: 'PC' };
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
