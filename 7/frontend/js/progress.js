/**
 * progress.js — Study session logging and goal tracking
 */

'use strict';

const Progress = {
  goals: [],

  async load() {
    await Promise.all([this.loadGoals(), this.loadLogs()]);
  },

  async logSession(data) {
    const res = await API.post('/progress/log', data);
    if (!res || !res.ok) { UI.toast(res?.data?.error || 'Failed to log session.', 'error'); return false; }
    UI.toast(`Logged ${data.minutes} minutes of study!`, 'success');
    await this.loadLogs();
    return true;
  },

  async loadLogs() {
    const res = await API.get('/progress/logs');
    if (!res || !res.ok) return;
    this.renderLogs(res.data.data.logs);
  },

  renderLogs(logs) {
    const container = document.getElementById('studyLogList');
    if (!container) return;

    if (!logs.length) {
      container.innerHTML = `
        <div class="empty-state">
          <i class="fa-solid fa-book-open" style="font-size:2.5rem;color:var(--clr-text-muted)"></i>
          <p style="margin-top:var(--space-3)">No study sessions logged yet.</p>
        </div>`;
      return;
    }

    container.innerHTML = logs.slice(0, 20).map(log => `
      <div class="task-item">
        <div style="display:flex;align-items:center;justify-content:center;width:38px;height:38px;
                    border-radius:50%;background:var(--clr-primary-light);flex-shrink:0">
          <i class="fa-solid fa-book" style="color:var(--clr-primary)" aria-hidden="true"></i>
        </div>
        <div class="task-body">
          <div class="task-title">${log.subject ? UI.escape(log.subject) : 'General Study'}</div>
          <div class="task-meta">
            <span><i class="fa-solid fa-clock" aria-hidden="true"></i> ${UI.minutesToHM(log.minutes)}</span>
            <span><i class="fa-solid fa-calendar-days" aria-hidden="true"></i> ${log.log_date}</span>
            ${log.note ? `<span><i class="fa-solid fa-note-sticky" aria-hidden="true"></i> ${UI.escape(log.note.slice(0,60))}</span>` : ''}
          </div>
        </div>
      </div>`).join('');
  },

  async loadGoals() {
    const res = await API.get('/goals');
    if (!res || !res.ok) return;
    this.goals = res.data.data.goals;
    this.renderGoals();
  },

  renderGoals() {
    const container = document.getElementById('goalList');
    if (!container) return;

    if (!this.goals.length) {
      container.innerHTML = `
        <div class="empty-state">
          <i class="fa-solid fa-bullseye" style="font-size:2.5rem;color:var(--clr-text-muted)"></i>
          <p style="margin-top:var(--space-3)">No goals set. Create your first academic goal!</p>
        </div>`;
      return;
    }

    container.innerHTML = this.goals.map(g => {
      const pct = Math.min(Math.round((g.current_value / g.target_value) * 100), 100);
      const barClass = pct >= 100 ? 'success' : pct > 50 ? '' : 'warning';
      return `
        <div class="goal-card">
          <div class="goal-header">
            <span class="goal-title">
              <i class="fa-solid fa-flag" style="margin-right:6px;color:var(--clr-primary)" aria-hidden="true"></i>
              ${UI.escape(g.title)}
            </span>
            <span class="goal-percent">${pct}%</span>
          </div>
          ${g.description
            ? `<p style="font-size:.8rem;color:var(--clr-text-muted);margin-bottom:var(--space-3)">${UI.escape(g.description)}</p>`
            : ''}
          <div class="progress-bar-wrap" role="progressbar"
               aria-valuenow="${pct}" aria-valuemin="0" aria-valuemax="100">
            <div class="progress-bar ${barClass}" style="width:${pct}%"></div>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:.75rem;color:var(--clr-text-muted);margin-top:var(--space-2)">
            <span>${g.current_value} / ${g.target_value} ${g.metric}</span>
            ${g.target_date
              ? `<span><i class="fa-solid fa-calendar" aria-hidden="true"></i> ${g.target_date}</span>`
              : ''}
          </div>
          <div style="display:flex;gap:var(--space-2);margin-top:var(--space-3)">
            <button class="btn btn-sm btn-secondary" onclick="Progress.openGoalModal(${g.id})">
              <i class="fa-solid fa-pen" aria-hidden="true"></i> Edit
            </button>
            <button class="btn btn-sm btn-primary" onclick="Progress.logGoalProgress(${g.id})">
              <i class="fa-solid fa-plus" aria-hidden="true"></i> Log Progress
            </button>
            <button class="btn btn-sm btn-danger" onclick="Progress.deleteGoal(${g.id})">
              <i class="fa-solid fa-trash" aria-hidden="true"></i>
            </button>
          </div>
        </div>`;
    }).join('');
  },

  editingGoalId: null,

  openGoalModal(id = null) {
    this.editingGoalId = id;
    const form = document.getElementById('goalForm');
    form.reset();

    if (id) {
      const g = this.goals.find(g => g.id === id);
      if (!g) return;
      form.title.value        = g.title;
      form.description.value  = g.description || '';
      form.target_date.value  = g.target_date || '';
      form.metric.value       = g.metric;
      form.target_value.value = g.target_value;
      document.getElementById('goalModalTitle').innerHTML =
        '<i class="fa-solid fa-pen-to-square" style="margin-right:6px;color:var(--clr-warning)"></i>Edit Goal';
    } else {
      document.getElementById('goalModalTitle').innerHTML =
        '<i class="fa-solid fa-trophy" style="margin-right:6px;color:var(--clr-warning)"></i>New Goal';
    }

    UI.openModal('goalModal');
  },

  async submitGoalModal() {
    const form = document.getElementById('goalForm');
    const data = {
      title:        form.title.value.trim(),
      description:  form.description.value.trim(),
      target_date:  form.target_date.value || null,
      metric:       form.metric.value,
      target_value: parseFloat(form.target_value.value) || 10,
    };

    if (!data.title) { UI.toast('Goal title is required.', 'error'); return; }

    UI.setButtonLoading('btnSaveGoal', true);
    let res;
    if (this.editingGoalId) {
      res = await API.put(`/goals/${this.editingGoalId}`, data);
    } else {
      res = await API.post('/goals', data);
    }
    UI.setButtonLoading('btnSaveGoal', false);

    if (!res || !res.ok) { UI.toast(res?.data?.error || 'Failed to save goal.', 'error'); return; }
    UI.toast('Goal saved!', 'success');
    UI.closeModal('goalModal');
    await this.loadGoals();
  },

  async logGoalProgress(id) {
    const value = parseFloat(prompt('Enter progress to add (e.g. 1 task, 2 hours):'));
    if (isNaN(value) || value <= 0) return;
    const goal = this.goals.find(g => g.id === id);
    if (!goal) return;
    const newVal = (goal.current_value || 0) + value;
    const status = newVal >= goal.target_value ? 'achieved' : 'active';
    const res = await API.put(`/goals/${id}`, { current_value: newVal, status });
    if (!res || !res.ok) { UI.toast('Failed to update goal.', 'error'); return; }
    if (status === 'achieved') UI.toast('Goal achieved! Congratulations!', 'success');
    else UI.toast('Progress logged!', 'success');
    await this.loadGoals();
  },

  async deleteGoal(id) {
    if (!confirm('Delete this goal?')) return;
    const res = await API.delete(`/goals/${id}`);
    if (!res || !res.ok) { UI.toast('Failed to delete goal.', 'error'); return; }
    UI.toast('Goal deleted.', 'success');
    await this.loadGoals();
  },
};

document.getElementById('logSessionForm')?.addEventListener('submit', async e => {
  e.preventDefault();
  const form = e.target;
  const data = {
    minutes: parseInt(form.minutes.value),
    subject: form.subject.value.trim(),
    note:    form.note.value.trim(),
  };
  if (await Progress.logSession(data)) form.reset();
});

document.getElementById('btnAddGoal')?.addEventListener('click', () => Progress.openGoalModal());
document.getElementById('btnSaveGoal')?.addEventListener('click', () => Progress.submitGoalModal());
