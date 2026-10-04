/* ============================================================
   filters.js · 分段控件、分类药丸与细筛（许可证 / 运行方式）
   ============================================================ */

import { el, clear } from '../utils/dom.js';
import { state, poolForPills, clearFacets, hasFacets } from '../core/state.js';
import { catIcon } from '../utils/icons.js';

/* 宽松许可：可商用、改后不必开源 */
const PERMISSIVE = ['MIT', 'Apache-2.0', 'BSD', 'zlib'];

/* 常见的 GPL 系列在 UI 上合并成一行，省得列出七八个选项 */
const LICENSE_GROUPS = [
  { id: 'free',  name: '宽松',      ids: PERMISSIVE,
    hint: '可商用，改了也不用开源' },
  { id: 'gpl',   name: 'GPL 系列',  ids: ['GPL-2.0', 'GPL-3.0'],
    hint: '改作必须同样开源' },
  { id: 'agpl',  name: 'AGPL',      ids: ['AGPL-3.0'],
    hint: '联网提供服务也要开源' },
  { id: 'mpl',   name: 'MPL / LGPL', ids: ['MPL-2.0', 'LGPL-2.1'],
    hint: '只传染改动的文件' },
  { id: 'cc',    name: 'CC 内容协议', ids: ['CC-BY-SA-3.0', 'CC-BY-SA-4.0'],
    hint: '常用于美术与内容' },
  { id: 'other', name: '其他',      ids: ['NetHack-PL', 'OSL-3.0', 'CC0-1.0'],
    hint: '各有条款' },
  { id: 'none',  name: '未声明',    ids: [],
    hint: '仓库里没有许可证，法律上默认保留所有权利' },
];

function licenseGroupOf(id) {
  if (!id) return 'none';
  for (const g of LICENSE_GROUPS) if (g.ids.includes(id)) return g.id;
  return 'other';
}

/** 某分组下的游戏数（受 tab 与其他筛选影响） */
function countIn(groupId, pool) {
  return pool.filter(g => {
    if (groupId === 'none') return !g.license;
    const grp = LICENSE_GROUPS.find(g => g.id === groupId);
    return grp && grp.ids.includes(g.license);
  }).length;
}

/* ============================================================
   分类药丸
   ============================================================ */
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
    const n = pool.filter(g => (g.category || []).includes(c.id)).length;
    const btn = el('button', {
      className: 'pill',
      attrs: {
        type: 'button', role: 'tab',
        'aria-selected': String(state.category === c.id),
        title: `${c.name} · ${n} 个`,
      },
    });
    btn.appendChild(el('span', { className: 'pill__icon', html: catIcon(c.id) }));
    btn.appendChild(el('span', { text: c.name }));
    btn.appendChild(el('span', { className: 'pill__num', text: String(n) }));
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

/* ============================================================
   细筛：运行方式 + 许可证
   ============================================================ */

/** state.license 存的是分组 id，落回具体许可证时用它判断命中 */
function groupSelected(groupId) {
  if (!state.license) return false;
  const grp = LICENSE_GROUPS.find(g => g.id === groupId);
  if (!grp) return state.license === groupId;
  return state.license === groupId || grp.ids.includes(state.license);
}

export function renderFacets(dom, { onChange } = {}) {
  const pool = poolForPills();

  /* --- 运行方式 --- */
  clear(dom.embedOpts);
  const embeds = [
    { v: true,  name: '站内直接玩', hint: '点开就在这个页面里玩，不用跳出去' },
    { v: false, name: '只能外链',   hint: '官方站禁止内嵌，会开新窗口' },
  ];
  embeds.forEach(o => {
    const n = pool.filter(g => (o.v ? g.mode === 'embed' : g.embeddable === false)).length;
    const b = el('button', {
      className: `opt${state.embed === o.v ? ' is-on' : ''}`,
      attrs: {
        type: 'button',
        'aria-pressed': String(state.embed === o.v),
        title: o.hint,
        disabled: n ? null : '',
      },
    }, [
      el('span', { text: o.name }),
      el('span', { className: 'opt__num', text: String(n) }),
    ]);
    b.addEventListener('click', () => {
      state.embed = state.embed === o.v ? null : o.v;
      onChange?.();
    });
    dom.embedOpts.appendChild(b);
  });

  /* --- 许可证 --- */
  clear(dom.licenseOpts);
  LICENSE_GROUPS.forEach(g => {
    const n = countIn(g.id, pool);
    const b = el('button', {
      className: `opt${groupSelected(g.id) ? ' is-on' : ''}`,
      attrs: {
        type: 'button',
        'aria-pressed': String(groupSelected(g.id)),
        title: g.hint,
        disabled: n ? null : '',
      },
    }, [
      el('span', { text: g.name }),
      el('span', { className: 'opt__num', text: String(n) }),
    ]);
    b.addEventListener('click', () => {
      const hit = groupSelected(g.id);
      // 宽松组点一下就只看宽松，再点取消；其他组记住具体许可证
      state.license = hit ? null
        : (g.ids.length === 1 ? g.ids[0] : g.id);
      onChange?.();
    });
    dom.licenseOpts.appendChild(b);
  });

  /* --- 角标与重置 --- */
  const active = (state.license ? 1 : 0) + (state.embed !== null ? 1 : 0);
  dom.badge.hidden = active === 0;
  dom.badge.textContent = String(active);
  dom.reset.hidden = active === 0;
}

export function initFacets(dom, { onChange } = {}) {
  dom.toggle.addEventListener('click', () => {
    const open = dom.body.hidden;
    dom.body.hidden = !open;
    dom.toggle.setAttribute('aria-expanded', String(open));
  });
  dom.reset.addEventListener('click', () => {
    state.license = null;
    state.embed = null;
    onChange?.();
  });
}

/* ============================================================
   分段控件
   ============================================================ */
export function syncSegmented(nodes) {
  nodes.forEach(n => n.setAttribute('aria-selected', String(n.dataset.tab === state.tab)));
}

export function initSegmented(nodes, { onChange } = {}) {
  nodes.forEach(btn => btn.addEventListener('click', () => {
    state.tab = btn.dataset.tab;
    state.category = null;
    if (state.tab === 'local') state.embed = null;   // 需下载与「站内直接玩」互斥
    syncSegmented(nodes);
    onChange?.();
  }));
}

/* 切 tab / 切分类时是否要顺带清掉不再适用的细筛 */
export function reconcileFacets() {
  if (state.tab === 'local' && state.embed !== null) state.embed = null;
  if (state.license === 'none' && !poolForPills().some(g => !g.license)) {
    state.license = null;
  }
}

export { hasFacets, clearFacets, licenseGroupOf, LICENSE_GROUPS };
