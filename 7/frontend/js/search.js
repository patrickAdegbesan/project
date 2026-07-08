/**
 * search.js — Semantic search UI
 */

'use strict';

const Search = {
  debounceTimer: null,

  init() {
    const input = document.getElementById('globalSearch');
    if (!input) return;

    input.addEventListener('input', () => {
      clearTimeout(this.debounceTimer);
      const q = input.value.trim();
      if (!q) { this.clearResults(); return; }
      this.debounceTimer = setTimeout(() => this.run(q), 400);
    });

    input.addEventListener('keydown', e => {
      if (e.key === 'Escape') { input.value = ''; this.clearResults(); }
    });
  },

  async run(query) {
    const res = await API.get(`/tasks/search?q=${encodeURIComponent(query)}&limit=8`);
    if (!res || !res.ok) return;
    this.renderResults(res.data.data.results, query);
  },

  renderResults(results, query) {
    const container = document.getElementById('searchResults');
    if (!container) return;
    container.style.display = 'block';

    if (!results.length) {
      container.innerHTML = `
        <div style="padding:var(--space-4);font-size:.875rem;color:var(--clr-text-muted);text-align:center">
          <i class="fa-solid fa-magnifying-glass" style="margin-right:6px"></i>
          No tasks found for "${UI.escape(query)}"
        </div>`;
      return;
    }

    const statusIcon = { pending: 'clock', in_progress: 'spinner', completed: 'circle-check', cancelled: 'circle-xmark' };

    container.innerHTML = results.map(r => `
      <div class="search-result-item" role="option"
           onclick="Search.goToTask(${r.task_id})"
           tabindex="0"
           style="display:flex;align-items:center;gap:var(--space-3);padding:var(--space-3) var(--space-4);
                  cursor:pointer;transition:background .15s"
           onmouseenter="this.style.background='var(--clr-bg)'"
           onmouseleave="this.style.background=''">
        <i class="fa-solid fa-${statusIcon[r.status] || 'list-check'}"
           style="color:var(--clr-primary);font-size:1rem;width:18px;text-align:center"
           aria-hidden="true"></i>
        <div>
          <div style="font-size:.875rem;font-weight:600">${UI.escape(r.title)}</div>
          <div style="font-size:.75rem;color:var(--clr-text-muted)">
            ${r.subject ? r.subject + ' &middot; ' : ''}${r.status} &middot; match: ${Math.round(r.score * 100)}%
          </div>
        </div>
      </div>`).join('');
  },

  clearResults() {
    const container = document.getElementById('searchResults');
    if (container) { container.style.display = 'none'; container.innerHTML = ''; }
  },

  goToTask(taskId) {
    this.clearResults();
    document.getElementById('globalSearch').value = '';
    Router.navigate('tasks');
    setTimeout(() => {
      const el = document.querySelector(`.task-checkbox[data-id="${taskId}"]`);
      if (el) {
        el.closest('.task-item')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        el.closest('.task-item')?.classList.add('highlight');
        setTimeout(() => el.closest('.task-item')?.classList.remove('highlight'), 2000);
      }
    }, 500);
  },
};

document.addEventListener('click', e => {
  if (!e.target.closest('.search-wrapper')) Search.clearResults();
});

document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    document.getElementById('globalSearch')?.focus();
  }
});
