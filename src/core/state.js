/* ============================================================
   state.js · 应用状态与筛选
   ============================================================ */

export const state = {
  games: [],
  categories: [],
  licenses: [],       // 许可证说明表（来自 games.json）
  loaded: false,
  tab: 'all',         // all | web | local | fav
  category: null,
  query: '',
  license: null,      // 许可证 id，'free' 表示宽松许可，'none' 表示无许可证
  embed: null,        // true=站内直接玩  false=只能外链  null=不限
};

/** 宽松许可证：可商用、改后不必开源 —— 对只想拿来玩/改的人最友好 */
const PERMISSIVE = new Set(['MIT', 'Apache-2.0', 'BSD', 'zlib']);

export function normalize(raw) {
  state.categories = raw.categories || [];
  state.licenses = raw.licenses || [];
  state.games = (raw.games || []).filter(g => g && g.id && g.status !== 'hidden');
  state.loaded = true;
}

function passTab(g) {
  if (state.tab === 'all')   return true;
  if (state.tab === 'web')   return g.kind === 'web';
  if (state.tab === 'local') return g.kind === 'download';
  if (state.tab === 'fav')   return favSet().has(g.id);
  return true;
}

/** 许可证筛选：具体 id / 'free'（宽松）/ 'none'（未声明） */
function passLicense(g) {
  if (!state.license) return true;
  if (state.license === 'none') return !g.license;
  if (state.license === 'free')  return PERMISSIVE.has(g.license);
  return g.license === state.license;
}

/** 内嵌筛选：只看能在站内 iframe 直接玩的 */
function passEmbed(g) {
  if (state.embed === null) return true;
  if (state.embed === true)  return g.mode === 'embed';
  return g.embeddable === false;
}

const passCat = g => !state.category || (g.category || []).includes(state.category);

const passQuery = g => {
  const q = state.query.trim().toLowerCase();
  if (!q) return true;
  return [g.title, g.desc, ...(g.alias || []), ...(g.tags || []),
          g.license || '', g.note || '']
    .join(' ').toLowerCase().includes(q);
};

let _favCache = null;
function favSet() {
  if (!_favCache) _favCache = new Set(JSON.parse(localStorage.getItem('ghub:fav') || '[]'));
  return _favCache;
}
export function invalidateFavCache() { _favCache = null; }

export function hasFacets() {
  return Boolean(state.category) || Boolean(state.license) || state.embed !== null;
}

export function clearFacets() {
  state.category = null;
  state.license = null;
  state.embed = null;
}

export function visibleGames() {
  return state.games.filter(g =>
    passTab(g) && passCat(g) && passQuery(g) && passLicense(g) && passEmbed(g));
}

/** 分类药丸的计数口径：受当前许可证/内嵌筛选影响，但不看分类本身 */
export function poolForPills() {
  return state.games.filter(g =>
    passTab(g) && passQuery(g) && passLicense(g) && passEmbed(g));
}

export function stats() {
  const g = state.games;
  return {
    total: g.length,
    web:   g.filter(x => x.kind === 'web').length,
    local: g.filter(x => x.kind === 'download').length,
    fav:   favSet().size,
    /* 站内可直接玩：mode 为 embed，即已实测通过内嵌检测 */
    embed: g.filter(x => x.mode === 'embed').length,
    /* 已归档上游：仍收录，但提醒用户谨慎 */
    archived: g.filter(x => x.archived).length,
  };
}
