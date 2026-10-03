/* ============================================================
   toast.js · 轻提示
   ============================================================ */

import { el } from '../utils/dom.js';

let host = null;

function ensureHost() {
  if (!host) {
    host = el('div', { className: 'toast-host', attrs: { 'aria-live': 'polite' } });
    document.body.appendChild(host);
  }
  return host;
}

/**
 * @param {string} msg
 * @param {string} icon  可选，emoji 图标
 * @param {number} ms    展示时长
 */
export function toast(msg, icon = '', ms = 2200) {
  const node = el('div', { className: 'toast' });
  node.innerHTML = icon
    ? `<span class="toast__icon">${icon}</span><span>${msg}</span>`
    : `<span>${msg}</span>`;

  ensureHost().appendChild(node);
  requestAnimationFrame(() => node.classList.add('is-open'));

  setTimeout(() => {
    node.classList.remove('is-open');
    setTimeout(() => node.remove(), 320);
  }, ms);
}
