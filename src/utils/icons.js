/* ============================================================
   icons.js · 内联 SVG 图标（统一描边风格，替代 emoji）
   全部 24x24 viewBox、stroke=currentColor，跟随文字色
   ============================================================ */

const S = (inner, opts = '') =>
  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ` +
  `stroke-linecap="round" stroke-linejoin="round" ${opts} aria-hidden="true">${inner}</svg>`;

export const CAT_ICONS = {
  puzzle:   S('<path d="M4 7a2 2 0 1 1 2-2v1a2 2 0 1 0 2 2h1a2 2 0 1 1-2 2v1a2 2 0 1 0 2 2h1a2 2 0 1 1-2 2 2 2 0 1 1-2-2"/>'),
  casual:   S('<path d="M12 21c-4-3-7-6-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 11c0 4-3 7-7 10Z"/>', 'fill="currentColor" stroke="none"'),
  action:   S('<path d="M4 9l11-3 3 11L7 20z"/><path d="M20 15l-11 3-3-11 11-3z"/>'),
  arcade:   S('<path d="M9 8h6v3h3v6H6v-6h3z"/><path d="M9 4v2M12 4v3M15 4v2"/>'),
  strategy: S('<path d="M12 4a3 3 0 0 1 3 3v2h2v3a4 4 0 0 1-8 0V9h2V7a3 3 0 0 1 3-3Z"/>'),
  board:    S('<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M4 10h16M10 4v16"/>'),
  shooter:  S('<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="2.5" fill="currentColor" stroke="none"/>'),
  io:       S('<circle cx="12" cy="12" r="8"/><path d="M4 12h16M12 4c3 3 3 13 0 16M12 4c-3 3-3 13 0 16"/>'),
  sports:   S('<circle cx="12" cy="12" r="8"/><path d="M5 9l3 1 1 3-3 1zM19 9l-3 1-1 3 3 1z"/>'),
  retro:    S('<rect x="3" y="5" width="18" height="13" rx="2"/><path d="M8 21h8M12 18v3"/>'),
  word:     S('<path d="M5 8h9M5 8V6M14 8V6"/><path d="M5 16h9M5 16v-2M14 16v-2"/><path d="M17 5l2 14"/>'),
  geo:      S('<path d="M12 21c4-5 7-8 7-12a7 7 0 1 0-14 0c0 4 3 7 7 12Z"/><circle cx="12" cy="9" r="2.5"/>'),
};

export function catIcon(id) {
  return CAT_ICONS[id] || S('<circle cx="12" cy="12" r="7"/>');
}

/* 反馈类图标（toast / 降级面板），替代 emoji */
export const UI = {
  check: S('<path d="M20 6 9 17l-5-5" stroke-width="2.6"/>'),
  warn:  S('<path d="M12 3 2 20h20z"/><path d="M12 9v5" stroke-width="2.2"/><circle cx="12" cy="17" r="1.1" fill="currentColor" stroke="none"/>'),
  clock: S('<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3.5 2.5" stroke-width="2.2"/>'),
  wrench:S('<path d="M14.5 6a3.5 3.5 0 0 0-4.6 4.2L4 16.1 7.9 20l5.9-5.9A3.5 3.5 0 0 0 18 9.5l-2.5 2.5-2-2z"/>'),
  repo:  S('<path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4"/><circle cx="10" cy="13" r="1.4" fill="currentColor" stroke="none"/><circle cx="10" cy="17" r="1.4" fill="currentColor" stroke="none"/>'),
  dl:    S('<path d="M12 3v11m0 0 4-4m-4 4-4-4"/><path d="M5 19h14" stroke-width="2.2"/>'),
};
