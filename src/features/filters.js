/* ============================================================
   filters.js · 分段控件与分类筛选
   ============================================================ */

import { el, clear } from '../utils/dom.js';
import { state, poolForPills } from '../core/state.js';
import { catIcon } from '../utils/icons.js';

export function renderPills(container, { onChange } = {}) {
  const pool = poolForPills();
  const usable = state.categories.filter(
    c => pool.some(g => (g.category || []).includes(c.id))
  );
  if (state.category && !usable.some(c => c.id === state.category)) {
    state.category = null;
  }

  clear(container);
  const frag = document.createDocumentFragment();

  const allBtn = el('button', {
    className: 'pill',
    text: `全部 ${pool.length}`,
    attrs: { type: 'button', role: 'tab', 'aria-selected': String(state.category === null) },
  });
  allBtn.addEventListener('click', () => { state.category = null; onChange?.(); });
  frag.appendChild(allBtn);

  usable.forEach(c => {
    const btn = el('button', {
      className: 'pill',
      attrs: { type: 'button', role: 'tab', 'aria-selected': String(state.category === c.id) },
    });
    const ic = el('span', { className: 'pill__icon', html: catIcon(c.id) });
    btn.appendChild(ic);
    btn.appendChild(el('span', { text: c.name }));
    btn.addEventListener('click', () => {
      state.category = state.category === c.id ? null : c.id;
      onChange?.();
    });
    frag.appendChild(btn);
  });

  container.appendChild(frag);
  container.querySelector('[aria-selected="true"]')
    ?.scrollIntoView({ block: 'nearest', inline: 'center', behavior: 'smooth' });
}

export function syncSegmented(nodes) {
  nodes.forEach(n => n.setAttribute('aria-selected', String(n.dataset.tab === state.tab)));
}

export function initSegmented(nodes, { onChange } = {}) {
  nodes.forEach(btn => btn.addEventListener('click', () => {
    state.tab = btn.dataset.tab;
    state.category = null;
    syncSegmented(nodes);
    onChange?.();
  }));
}
