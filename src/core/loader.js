/* ============================================================
   loader.js · 数据加载
   ============================================================ */

const DATA_URL = 'data/games.json';

/**
 * 拉取 games.json
 * 加时间戳避免 CDN 缓存导致的数据滞后
 */
export async function loadGames({ bust = false } = {}) {
  const url = bust ? `${DATA_URL}?t=${Date.now()}` : DATA_URL;
  const res = await fetch(url, { cache: 'no-cache' });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  if (!Array.isArray(data.games)) throw new Error('games.json 结构异常：缺少 games 数组');
  return data;
}
