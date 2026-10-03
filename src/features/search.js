/* ============================================================
   search.js · 搜索
   ============================================================ */

import { debounce } from '../utils/dom.js';
import { state } from '../core/state.js';

/**
 * @param {object} opts { input, wrap, clearBtn, onChange }
 */
export function initSearch({ input, wrap, clearBtn, onChange }) {
  const emit = debounce(() => onChange?.(), 150);

  input.addEventListener('input', () => {
    wrap.classList.toggle('has-value', input.value.length > 0);
    state.query = input.value;
    emit();
  });

  input.addEventListener('keydown', e => {
    if (e.key === 'Escape') reset();
  });

  clearBtn.addEventListener('click', reset);

  function reset() {
    input.value = '';
    state.query = '';
    wrap.classList.remove('has-value');
    onChange?.();
    input.focus();
  }

  return { reset };
}

/** 全局快捷键：/ 聚焦搜索框 */
export function initSearchShortcut(input) {
  document.addEventListener('keydown', e => {
    const tag = document.activeElement?.tagName;
    if (e.key === '/' && tag !== 'INPUT' && tag !== 'TEXTAREA') {
      e.preventDefault();
      input.focus();
      input.select?.();
    }
  });
}
