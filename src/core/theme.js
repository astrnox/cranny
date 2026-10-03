/* ============================================================
   theme.js · 主题管理
   优先级：localStorage 手动设置 > 系统偏好
   ============================================================ */

import { store } from './storage.js';

const ICON_SUN = `
  <circle cx="12" cy="12" r="4.5"/>
  <path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4"/>`;

const ICON_MOON = `<path d="M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z"/>`;

const mq = window.matchMedia('(prefers-color-scheme: dark)');

function effective() {
  return store.getTheme() || (mq.matches ? 'dark' : 'light');
}

function apply(btn) {
  const saved = store.getTheme();
  if (saved) document.documentElement.setAttribute('data-theme', saved);
  else document.documentElement.removeAttribute('data-theme');

  // 同步浏览器地址栏配色
  const meta = document.querySelector('meta[name="theme-color"]:not([media])');
  if (meta) meta.setAttribute('content', effective() === 'dark' ? '#000000' : '#F2F2F7');

  if (btn) btn.innerHTML = effective() === 'dark' ? ICON_SUN : ICON_MOON;
}

export function initTheme(btn) {
  apply(btn);

  btn?.addEventListener('click', () => {
    store.setTheme(effective() === 'dark' ? 'light' : 'dark');
    apply(btn);
  });

  // 未手动设置时，跟随系统变化实时切换
  mq.addEventListener?.('change', () => { if (!store.getTheme()) apply(btn); });
}
