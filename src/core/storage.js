/* ============================================================
   storage.js · 本地持久化
   键名前缀统一 ghub:
   该模块是「存储适配层」——未来接入 Supabase 时只换实现，
   上层业务代码（app/store）无需改动。
   ============================================================ */

const PREFIX = 'ghub:';

function read(key, fallback) {
  try {
    const raw = localStorage.getItem(PREFIX + key);
    return raw === null ? fallback : JSON.parse(raw);
  } catch {
    return fallback;
  }
}

function write(key, value) {
  try {
    localStorage.setItem(PREFIX + key, JSON.stringify(value));
  } catch {
    /* 隐私模式 / 配额满 —— 静默降级，不阻断使用 */
  }
}

export const store = {
  /* ---------- 最近游玩 ---------- */
  getRecent()          { return read('recent', []); },
  pushRecent(id) {
    const list = read('recent', []).filter(x => x !== id);
    list.unshift(id);
    write('recent', list.slice(0, 12));
  },
  clearRecent()        { write('recent', []); },

  /* ---------- 收藏 ---------- */
  getFavs()            { return read('fav', []); },
  isFav(id)            { return read('fav', []).includes(id); },
  toggleFav(id) {
    const list = read('fav', []);
    const i = list.indexOf(id);
    if (i >= 0) list.splice(i, 1); else list.unshift(id);
    write('fav', list);
    return list.includes(id);
  },

  /* ---------- 游玩次数 ---------- */
  getPlays()           { return read('plays', {}); },
  bumpPlay(id) {
    const plays = read('plays', {});
    plays[id] = (plays[id] || 0) + 1;
    write('plays', plays);
  },

  /* ---------- 主题 ---------- */
  getTheme()           { return read('theme', null); },   // null = 跟随系统
  setTheme(v)          { write('theme', v); },

  /* ---------- 内嵌可用性探测缓存 ---------- */
  getEmbedCache()      { return read('embedCache', {}); },
  setEmbedResult(id, result) {
    const cache = read('embedCache', {});
    cache[id] = { result, at: Date.now() };
    write('embedCache', cache);
  },
  /** 同一次会话内不重复探测已被判定为阻断的游戏 */
  isKnownBlocked(id) {
    const c = read('embedCache', {})[id];
    return c?.result === 'blocked';
  },
};
