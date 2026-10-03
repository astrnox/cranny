/* ============================================================
   state.js · 应用状态
   ============================================================ */

export const state = {
  games: [],
  categories: [],
  loaded: false,
  tab: 'all',      // all | web | local | fav
  category: null,
  query: '',
};

export function normalize(raw) {
  state.categories = raw.categories || [];
  state.games = (raw.games || []).filter(g => g && g.id && g.status !== 'hidden');
  state.loaded = true;
}

function passTab(g) {
  if (state.tab === 'all')   return true;
  if (state.tab === 'web')   return g.platform.includes('web');
  if (state.tab === 'local') return g.mode === 'download';
  if (state.tab === 'fav')   return favSet().has(g.id);
  return true;
}
const passCat = g => !state.category || (g.category || []).includes(state.category);
const passQuery = g => {
  const q = state.query.trim().toLowerCase();
  if (!q) return true;
  return [g.title, g.desc, ...(g.alias || []), ...(g.tags || [])]
    .join(' ').toLowerCase().includes(q);
};

let _favCache = null;
function favSet() {
  if (!_favCache) _favCache = new Set(JSON.parse(localStorage.getItem('ghub:fav') || '[]'));
  return _favCache;
}
export function invalidateFavCache() { _favCache = null; }

export function visibleGames() {
  return state.games.filter(g => passTab(g) && passCat(g) && passQuery(g));
}
export function poolForPills() { return state.games.filter(passTab); }
export function stats() {
  const g = state.games;
  return {
    total: g.length,
    web:   g.filter(x => x.platform.includes('web')).length,
    local: g.filter(x => x.mode === 'download').length,
    fav:   favSet().size,
  };
}
