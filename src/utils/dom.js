/* ============================================================
   dom.js · DOM 小工具
   ============================================================ */

export const $  = (sel, root = document) => root.querySelector(sel);
export const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

/**
 * 创建元素
 * @param {string} tag
 * @param {object} props   { className, text, html, dataset, attrs, style, on }
 * @param {Array}  children
 */
export function el(tag, props = {}, children = []) {
  const node = document.createElement(tag);
  const { className, text, html, dataset, attrs, style, on } = props;

  if (className) node.className = className;
  if (text != null) node.textContent = text;
  if (html != null) node.innerHTML = html;

  if (dataset) Object.entries(dataset).forEach(([k, v]) => { node.dataset[k] = v; });
  if (attrs)   Object.entries(attrs).forEach(([k, v]) => node.setAttribute(k, v));
  if (style)   Object.entries(style).forEach(([k, v]) => node.style.setProperty(k, v));
  if (on)      Object.entries(on).forEach(([evt, fn]) => node.addEventListener(evt, fn));

  children.forEach(c => c && node.appendChild(c));
  return node;
}

export function clear(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
}

/** 转义 HTML，防止标题/描述注入 */
export function escapeHtml(str) {
  return String(str ?? '').replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[c]));
}

/** 防抖 */
export function debounce(fn, wait = 150) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), wait);
  };
}

export function raf(fn) {
  return requestAnimationFrame(() => requestAnimationFrame(fn));
}
