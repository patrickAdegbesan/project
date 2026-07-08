/**
 * tasks.js — Task management (CRUD, filters, display)
 */

'use strict';

const Tasks = {
  items: [],
  activeFilter: 'all',
  activeSort: 'due_date',

  async load(filters = {}) {
    const params = new URLSearchParams(filters).toString();
    const res = await API.get(`/tasks${params ? '?' + params : ''}`);
    if (!res || !res.ok) return;
    this.items = res.data.data.tasks;
    this.render();
  },

  render(items = null) {
    const list = items ?? this._applyLocalFilter(this.items);
    const container = document.getElementById('taskList');
    if (!container) return;

    if (!list.length) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">
            <i class="fa-regular fa-clipboard" style="font-size:3rem;color:var(--clr-text-muted)"></i>
          </div>
          <p>No tasks found. Add your first task to get started!</p>
          <button class="btn btn-primary" onclick="Tasks.openModal()">
            <i class="fa-solid fa-plus"></i> Add Task
          </button>
        </div>`;
      return;
    }

    container.innerHTML = list.map(t => this._taskHTML(t)).join('');

    container.querySelectorAll('.task-checkbox').forEach(cb => {
      cb.addEventListener('change', async () => {
        const id = parseInt(cb.dataset.id);
        const newStatus = cb.checked ? 'completed' : 'pending';
        await Tasks.updateStatus(id, newStatus);
      });
    });
  },

  _applyLocalFilter(items) {
    let out = [...items];
    if (this.activeFilter !== 'all') {
      if (['pending','in_progress','completed','overdue'].includes(this.activeFilter)) {
        if (this.activeFilter === 'overdue') {
          const now = new Date().toISOString();
          out = out.filter(t => t.due_date && t.due_date < now && t.status !== 'completed');
        } else {
          out = out.filter(t => t.status === this.activeFilter);
        }
      } else {
        out = out.filter(t => t.priority === this.activeFilter);
      }
    }
    if (this.activeSort === 'due_date') {
      out.sort((a, b) => (a.due_date || '9') < (b.due_date || '9') ? -1 : 1);
    } else if (this.activeSort === 'priority') {
      const order = { urgent: 0, high: 1, medium: 2, low: 3 };
      out.sort((a, b) => (order[a.priority] ?? 2) - (order[b.priority] ?? 2));
    } else if (this.activeSort === 'created') {
      out.sort((a, b) => b.created_at.localeCompare(a.created_at));
    }
    return out;
  },

  _taskHTML(t) {
    const due = t.due_date
      ? new Date(t.due_date).toLocaleDateString('en-GB', { day:'numeric', month:'short', year:'numeric' })
      : '';
    const overdue = t.due_date && t.due_date < new Date().toISOString() && t.status !== 'completed';
    const tags = t.tags
      ? t.tags.split(',').filter(Boolean)
          .map(tag => `<span class="tag">${UI.escape(tag.trim())}</span>`).join('')
      : '';

    return `
      <div class="task-item priority-${t.priority} ${t.status === 'completed' ? 'completed' : ''}"
           role="article" aria-label="Task: ${UI.escape(t.title)}">
        <input type="checkbox" class="task-checkbox" data-id="${t.id}"
               ${t.status === 'completed' ? 'checked' : ''}
               aria-label="Mark '${UI.escape(t.title)}' as completed">
        <div class="task-body">
          <div class="task-title">${UI.escape(t.title)}</div>
          ${t.description
            ? `<div class="text-muted" style="font-size:.8rem;margin-top:2px">
                 ${UI.escape(t.description.slice(0,120))}${t.description.length > 120 ? '…' : ''}
               </div>`
            : ''}
          <div class="task-meta">
            <span class="priority-badge ${t.priority}">${t.priority}</span>
            ${t.subject
              ? `<span><i class="fa-solid fa-book-open" aria-hidden="true"></i> ${UI.escape(t.subject)}</span>`
              : ''}
            ${due
              ? `<span style="color:${overdue ? 'var(--clr-danger)' : 'inherit'}">
                   <i class="fa-solid fa-${overdue ? 'triangle-exclamation' : 'calendar-days'}" aria-hidden="true"></i>
                   ${overdue ? 'Overdue: ' : ''}${due}
                 </span>`
              : ''}
            ${t.estimated_minutes
              ? `<span><i class="fa-solid fa-clock" aria-hidden="true"></i> ${UI.minutesToHM(t.estimated_minutes)}</span>`
              : ''}
            <div class="tag-list flex gap-2">${tags}</div>
          </div>
        </div>
        <div class="task-actions">
          <button class="btn btn-sm btn-secondary" onclick="Tasks.openModal(${t.id})"
                  aria-label="Edit task">
            <i class="fa-solid fa-pen" aria-hidden="true"></i>
          </button>
          <button class="btn btn-sm btn-danger" onclick="Tasks.delete(${t.id})"
                  aria-label="Delete task">
            <i class="fa-solid fa-trash" aria-hidden="true"></i>
          </button>
        </div>
      </div>`;
  },

  async create(data) {
    const res = await API.post('/tasks', data);
    if (!res || !res.ok) { UI.toast(res?.data?.error || 'Failed to create task.', 'error'); return false; }
    UI.toast('Task created!', 'success');
    await this.load();
    return true;
  },

  async update(id, data) {
    const res = await API.put(`/tasks/${id}`, data);
    if (!res || !res.ok) { UI.toast(res?.data?.error || 'Failed to update task.', 'error'); return false; }
    UI.toast('Task updated.', 'success');
    await this.load();
    return true;
  },

  async updateStatus(id, status) {
    await API.put(`/tasks/${id}`, { status });
    await this.load();
    if (status === 'completed') UI.toast('Task completed!', 'success');
  },

  async delete(id) {
    if (!confirm('Delete this task?')) return;
    const res = await API.delete(`/tasks/${id}`);
    if (!res || !res.ok) { UI.toast('Failed to delete task.', 'error'); return; }
    UI.toast('Task deleted.', 'success');
    await this.load();
  },

  editingId: null,

  async openModal(id = null) {
    this.editingId = id;
    const form = document.getElementById('taskForm');
    form.reset();

    if (id) {
      const res = await API.get(`/tasks/${id}`);
      if (!res || !res.ok) return;
      const t = res.data.data.task;
      form.title.value             = t.title;
      form.description.value       = t.description || '';
      form.subject.value           = t.subject || '';
      form.priority.value          = t.priority;
      form.status.value            = t.status;
      form.due_date.value          = t.due_date ? t.due_date.slice(0, 16) : '';
      form.estimated_minutes.value = t.estimated_minutes;
      form.tags.value              = t.tags || '';
      document.getElementById('taskModalTitle').innerHTML =
        '<i class="fa-solid fa-pen-to-square" style="margin-right:6px;color:var(--clr-primary)"></i>Edit Task';
    } else {
      document.getElementById('taskModalTitle').innerHTML =
        '<i class="fa-solid fa-list-check" style="margin-right:6px;color:var(--clr-primary)"></i>New Task';
    }

    UI.openModal('taskModal');
  },

  async submitModal() {
    const form = document.getElementById('taskForm');
    const data = {
      title:             form.title.value.trim(),
      description:       form.description.value.trim(),
      subject:           form.subject.value.trim(),
      priority:          form.priority.value,
      status:            form.status.value,
      due_date:          form.due_date.value || null,
      estimated_minutes: parseInt(form.estimated_minutes.value) || 60,
      tags:              form.tags.value.trim(),
    };

    if (!data.title) { UI.toast('Title is required.', 'error'); return; }

    UI.setButtonLoading('btnSaveTask', true);
    const ok = this.editingId
      ? await this.update(this.editingId, data)
      : await this.create(data);
    UI.setButtonLoading('btnSaveTask', false);

    if (ok) UI.closeModal('taskModal');
  },

  setFilter(filter) {
    this.activeFilter = filter;
    document.querySelectorAll('.task-filter-chip').forEach(c => {
      c.classList.toggle('active', c.dataset.filter === filter);
    });
    this.render();
  },
};

// Wire up
document.querySelectorAll('.task-filter-chip').forEach(c => {
  c.addEventListener('click', () => Tasks.setFilter(c.dataset.filter));
});
document.getElementById('taskSort')?.addEventListener('change', e => {
  Tasks.activeSort = e.target.value;
  Tasks.render();
});
document.getElementById('btnAddTask')?.addEventListener('click', () => Tasks.openModal());
document.getElementById('btnSaveTask')?.addEventListener('click', () => Tasks.submitModal());
