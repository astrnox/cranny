/* ============================================================
   app.js · 应用入口
   ============================================================ */

import { $, $$, el, clear } from './utils/dom.js';
import { state, normalize, visibleGames, stats, invalidateFavCache } from './core/state.js';
import { loadGames } from './core/loader.js';
import { initTheme } from './core/theme.js';
import { store } from './core/storage.js';

import { createCard } from './components/card.js';
import { renderPills, syncSegmented, initSegmented } from './features/filters.js';
import { initSearch, initSearchShortcut } from './features/search.js';
import { openPlayer, closePlayer, initPlayer } from './components/player.js';
import { openDetail, closeDetail, initDetail } from './components/detail.js';
import { toast } from './components/toast.js';
import { UI } from './utils/icons.js';

const dom = {
  topbar:      $('#topbar'),
  loadbar:     $('#loadbar'),
  pageSub:     $('#pageSub'),
  searchInput: $('#search'),
  searchWrap:  $('#searchWrap'),
  searchClear: $('#searchClear'),
  themeToggle: $('#themeToggle'),
  pills:       $('#pills'),
  segmented:   $$('.segmented__item'),
  featSec:     $('#featuredSection'),
  featRow:     $('#featuredRow'),
  featCount:   $('#featuredCount'),
  recentSec:   $('#recentSection'),
  recentRow:   $('#recentRow'),
  recentClear: $('#recentClear'),
  grid:        $('#grid'),
  gridTitle:   $('#gridTitle'),
  gridCount:   $('#gridCount'),
  emptyState:  $('#emptyState'),
};

/* ============================================================
   卡片渲染（内置，替代已删除的 grid.js）
   ============================================================ */
function renderCards(container, games) {
  clear(container);
  const favs = new Set(store.getFavs());
  const frag = document.createDocumentFragment();
  games.forEach((game, i) => {
    const card = createCard(game, {
      isFav: favs.has(game.id),
      onFav: handleFav,
      onOpen: openGame,
    });
    card.style.setProperty('--i', Math.min(i, 14));   // 错峰入场上限，避免长列表拖沓
    if (game.featured) card.classList.add('card--featured');
    frag.appendChild(card);
  });
  container.appendChild(frag);
}

/** 加载中：居中圆环 + 文案，明确的加载动画 */
function showLoading(container) {
  clear(container);
  container.appendChild(el('div', { className: 'boot' }, [
    el('div', { className: 'boot__spinner', attrs: { role: 'status', 'aria-label': '正在加载游戏' } }),
    el('div', { className: 'boot__text', text: '正在加载游戏…' }),
  ]));
}

function renderEmpty(container, opts = {}) {
  const { kind = 'default', title, desc, actionText = '清除筛选', onAction } = opts;
  const S = (inner) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${inner}</svg>`;
  const icons = {
    search: S('<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>'),
    fav:    S('<path d="M12 21C7 17 4 14 4 10a4 4 0 0 1 8-1 4 4 0 0 1 8 1c0 4-3 7-8 11Z"/>'),
    local:  S('<path d="M3 8l9-4 9 4-9 4z"/><path d="M3 8v8l9 4 9-4V8"/>'),
    default:S('<rect x="3" y="7" width="18" height="11" rx="4"/><path d="M7 11v3M17 11v3M11 12h2"/>'),
  };
  clear(container);
  const btn = el('button', { className: 'btn btn--primary', text: actionText, attrs: { type: 'button' } });
  btn.addEventListener('click', () => onAction?.());
  container.appendChild(el('div', { className: 'empty' }, [
    el('div', { className: 'empty__icon', html: icons[kind] || icons.default }),
    el('p', { className: 'empty__title', text: title }),
    el('p', { className: 'empty__desc', text: desc }),
    btn,
  ]));
}

function handleFav(id) {
  invalidateFavCache();
  const now = store.toggleFav(id);
  const game = state.games.find(g => g.id === id);
  const heart = now
    ? '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 21C7 17 4 14 4 10a4 4 0 0 1 8-1 4 4 0 0 1 8 1c0 4-3 7-8 11Z"/></svg>'
    : '';
  toast(now ? `已收藏「${game?.title ?? ''}」` : '已取消收藏', heart);
  if (state.tab === 'fav') setTimeout(render, 200);
  else updateSubtitle();
  return now;
}

/* ============================================================
   打开游戏：按运行方式分发
   embed → 详情浮层（含 README + 直接玩）
   download / repo / redirect → 详情浮层
   所有卡片统一打开详情，详情里再按 mode 给主按钮
   ============================================================ */
function openGame(game) {
  if (game.status === 'broken') {
    toast(`「${game.title}」当前不可用`, UI.warn);
    return;
  }
  openDetail(game, {
    onAction: (g) => {
      closeDetail();
      setTimeout(() => routeAction(g), 250);
    },
  });
}

/** 详情主按钮的实际行为 */
function routeAction(g) {
  if (g.mode === 'embed') {
    if (store.isKnownBlocked(g.id)) {
      window.open(g.url, '_blank', 'noopener,noreferrer');
    } else {
      openPlayer(g, { onClose: () => setTimeout(render, 60) });
    }
  } else if (g.url) {
    window.open(g.url, '_blank', 'noopener,noreferrer');
    store.pushRecent(g.id);
    store.bumpPlay(g.id);
  }
}

/* ============================================================
   渲染
   ============================================================ */
function render() {
  renderPills(dom.pills, { onChange: render });

  const focusMode = Boolean(state.query.trim()) || state.category !== null;

  /* 精选 */
  const featured = state.games.filter(g => g.featured && g.status === 'active');
  const showFeat = !focusMode && state.tab !== 'local' && featured.length > 0;
  dom.featSec.hidden = !showFeat;
  if (showFeat) {
    dom.featCount.textContent = `${featured.length} 个`;
    renderCards(dom.featRow, featured);
  }

  /* 最近游玩 */
  const recent = store.getRecent()
    .map(id => state.games.find(g => g.id === id))
    .filter(Boolean);
  const showRecent = !focusMode && recent.length > 0;
  dom.recentSec.hidden = !showRecent;
  if (showRecent) renderCards(dom.recentRow, recent);

  /* 主网格 */
  const list = visibleGames();
  renderCards(dom.grid, list);

  /* 标题 */
  const tabName = { all: '全部', web: '网页', local: '本地', fav: '收藏' }[state.tab];
  const catName = state.category ? state.categories.find(c => c.id === state.category)?.name : null;
  dom.gridTitle.textContent = state.query.trim()
    ? `搜索「${state.query.trim()}」`
    : (catName ? `${catName} · ${tabName}` : (state.tab === 'all' ? '全部游戏' : `${tabName}游戏`));
  dom.gridCount.textContent = list.length ? `${list.length} 个` : '';

  /* 空状态 */
  if (list.length === 0) {
    renderEmpty(dom.emptyState, emptyConfig());
  } else {
    dom.emptyState.innerHTML = '';
  }

  updateSubtitle();
  syncSegmented(dom.segmented);
}

function emptyConfig() {
  if (state.tab === 'fav') return {
    kind: 'fav',
    title: '还没有收藏任何游戏',
    desc: '把鼠标移到卡片上，点右上角的星标即可收藏。',
    actionText: '去看看全部游戏',
    onAction() { state.tab = 'all'; render(); },
  };
  if (state.tab === 'local') return {
    kind: 'local',
    title: '还没有本地游戏',
    desc: '在 games.json 里以 mode: "download" 添加 PC / 安卓游戏。',
    actionText: '看看网页游戏',
    onAction() { state.tab = 'web'; render(); },
  };
  if (state.query.trim()) return {
    kind: 'search',
    title: `没有找到「${state.query.trim()}」`,
    desc: '试试更短的关键词，或者换个说法。',
    actionText: '清除搜索',
    onAction() {
      state.query = '';
      dom.searchInput.value = '';
      dom.searchWrap.classList.remove('has-value');
      render();
    },
  };
  return {
    kind: 'default',
    title: '这个分类下暂时没有游戏',
    desc: '换个分类看看，或者回到全部游戏。',
    actionText: '查看全部',
    onAction() { state.category = null; state.tab = 'all'; render(); },
  };
}

function updateSubtitle() {
  const s = stats();
  dom.pageSub.textContent = [
    `${s.total} 个游戏`,
    `${s.web} 个网页`,
    s.local ? `${s.local} 个本地下载` : null,
    s.fav ? `${s.fav} 个收藏` : null,
  ].filter(Boolean).join(' · ');
}

function initTopbar() {
  const onScroll = () => dom.topbar.classList.toggle('is-scrolled', scrollY > 8);
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

/* ============================================================
   启动
   ============================================================ */
(async function init() {
  initTheme(dom.themeToggle);
  initPlayer();
  initDetail();
  initTopbar();

  initSearch({ input: dom.searchInput, wrap: dom.searchWrap, clearBtn: dom.searchClear, onChange: render });
  initSearchShortcut(dom.searchInput);
  initSegmented(dom.segmented, { onChange: render });

  dom.recentClear.addEventListener('click', () => {
    store.clearRecent();
    render();
    toast('已清空最近游玩');
  });

  showLoading(dom.grid);
  dom.pageSub.textContent = '正在加载…';

  const t0 = performance.now();
  const MIN_MS = 500;   // 最短显示时长：太快看不见加载动画
  const wait = ms => new Promise(r => setTimeout(r, ms));

  try {
    const data = await loadGames();
    normalize(data);
    const rest = MIN_MS - (performance.now() - t0);
    if (rest > 0) await wait(rest);
    render();
  } catch (err) {
    console.error('[GameHub]', err);
    dom.pageSub.textContent = '数据加载失败';
    dom.grid.innerHTML = '';
    renderEmpty(dom.grid, {
      title: '加载 games.json 失败',
      desc: `${err.message}｜本地预览请用 HTTP 服务打开（如 npx serve），file:// 会被浏览器拦截。`,
      actionText: '重试',
      onAction: () => location.reload(),
    });
  } finally {
    dom.loadbar.classList.add('is-done');   // 数据到位，隐藏顶部进度条
  }
})();

window.__gamehub = { state, render, openGame, closePlayer };
