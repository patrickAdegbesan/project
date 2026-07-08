/**
 * adaptive.js — Adaptive learning engine UI
 */

'use strict';

const Adaptive = {
  async load() {
    const res = await API.get('/analytics/recommendations');
    if (!res || !res.ok) return;
    const r = res.data.data.recommendations;
    this.renderOverview(r);
    this.renderTips(r.tips, r.reminder_mode);
    this.renderPomodoro(r.pomodoro);
    this.renderUrgent(r.urgent_tasks);
    this.renderSubtasks(r.subtask_suggestions);
    this.renderSubjectBreakdown(r.subject_breakdown);
  },

  renderOverview(r) {
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    set('recCompletionRate', Math.round((r.completion_rate || 0) * 100) + '%');
    set('recWeeklyHours',    UI.minutesToHM(r.weekly_study_minutes || 0));
    set('recPeakHours',      r.peak_hours?.length
      ? r.peak_hours.map(h => `${String(h).padStart(2,'0')}:00`).join(', ')
      : 'Not enough data yet');
  },

  renderTips(tips = [], reminderMode = 'normal') {
    const container = document.getElementById('adaptiveTips');
    if (!container) return;

    if (!tips.length) {
      container.innerHTML = `
        <div style="text-align:center;padding:var(--space-6);color:var(--clr-text-muted)">
          <i class="fa-solid fa-lightbulb" style="font-size:2rem;margin-bottom:var(--space-3)"></i>
          <p>Complete more tasks to get personalised tips.</p>
        </div>`;
      return;
    }

    container.innerHTML = tips.map(tip => {
      const isAdhd = tip.toLowerCase().includes('adhd');
      const isAsd  = tip.toLowerCase().includes('asd');
      const cls    = isAdhd ? 'adhd-tip' : isAsd ? 'asd-tip' : '';
      const icon   = isAdhd ? 'bolt' : isAsd ? 'sitemap' : 'lightbulb';
      return `
        <div class="tip-card ${cls}" role="note">
          <i class="fa-solid fa-${icon}" style="margin-right:8px;opacity:.7" aria-hidden="true"></i>
          ${UI.escape(tip)}
        </div>`;
    }).join('');
  },

  renderPomodoro(p) {
    const el = document.getElementById('pomodoroPanel');
    if (!el || !p) return;
    el.innerHTML = `
      <div class="stat-cards" style="grid-template-columns:repeat(3,1fr)">
        <div class="stat-card">
          <div class="stat-icon"><i class="fa-solid fa-brain" aria-hidden="true"></i></div>
          <div class="stat-value">${p.work_minutes}m</div>
          <div class="stat-label">Focus interval</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon success"><i class="fa-solid fa-mug-hot" aria-hidden="true"></i></div>
          <div class="stat-value">${p.break_minutes}m</div>
          <div class="stat-label">Short break</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon info"><i class="fa-solid fa-tree" aria-hidden="true"></i></div>
          <div class="stat-value">${p.long_break}m</div>
          <div class="stat-label">Long break</div>
        </div>
      </div>
      <div class="tip-card mt-4">
        <i class="fa-solid fa-circle-info" style="margin-right:8px" aria-hidden="true"></i>
        These intervals are personalised for your neuro profile.
        Change your profile in <strong>Settings</strong> to adjust them.
      </div>`;
  },

  renderUrgent(tasks = []) {
    const container = document.getElementById('urgentTasksPanel');
    if (!container) return;

    if (!tasks.length) {
      container.innerHTML = `
        <div style="text-align:center;padding:var(--space-5);color:var(--clr-success)">
          <i class="fa-solid fa-circle-check" style="font-size:2rem;margin-bottom:var(--space-3)"></i>
          <p style="font-size:.875rem">No urgent tasks in the next 48 hours.</p>
        </div>`;
      return;
    }

    container.innerHTML = `
      <p class="text-danger" style="font-weight:600;margin-bottom:var(--space-3)">
        <i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i>
        ${tasks.length} task(s) due in the next 48 hours:
      </p>
      ${tasks.map(t => `
        <div class="task-item priority-${t.priority}">
          <i class="fa-solid fa-circle-exclamation" style="color:var(--clr-danger);margin-top:2px" aria-hidden="true"></i>
          <div class="task-body">
            <div class="task-title">${UI.escape(t.title)}</div>
            <div class="task-meta">
              <span class="priority-badge ${t.priority}">${t.priority}</span>
              ${t.due_date
                ? `<span><i class="fa-solid fa-calendar-days" aria-hidden="true"></i>
                   ${new Date(t.due_date).toLocaleString('en-GB')}</span>`
                : ''}
            </div>
          </div>
        </div>`).join('')}`;
  },

  renderSubtasks(suggestions = []) {
    const container = document.getElementById('subtaskPanel');
    if (!container) return;

    if (!suggestions.length) {
      container.innerHTML = `
        <div style="text-align:center;padding:var(--space-5);color:var(--clr-text-muted)">
          <i class="fa-solid fa-sitemap" style="font-size:1.8rem;margin-bottom:var(--space-3)"></i>
          <p style="font-size:.875rem">No complex tasks found to break down.</p>
        </div>`;
      return;
    }

    container.innerHTML = suggestions.map(s => `
      <div class="card mb-4">
        <div class="card-header">
          <h3 style="font-size:.9rem">
            <i class="fa-solid fa-map-pin" style="color:var(--clr-primary);margin-right:6px" aria-hidden="true"></i>
            ${UI.escape(s.title)}
          </h3>
        </div>
        <div class="card-body">
          <p style="font-size:.8rem;color:var(--clr-text-muted);margin-bottom:var(--space-3)">Suggested breakdown:</p>
          <ol style="padding-left:1.2rem">
            ${s.subtasks.map(sub => `
              <li style="font-size:.875rem;margin-bottom:6px">
                <i class="fa-regular fa-circle-dot" style="color:var(--clr-primary);margin-right:6px" aria-hidden="true"></i>
                ${UI.escape(sub)}
              </li>`).join('')}
          </ol>
        </div>
      </div>`).join('');
  },

  renderSubjectBreakdown(subjects = {}) {
    const container = document.getElementById('subjectBreakdownPanel');
    if (!container) return;

    const entries = Object.entries(subjects);
    if (!entries.length) {
      container.innerHTML = '<p class="text-muted">No subject data yet.</p>';
      return;
    }

    container.innerHTML = entries.map(([sub, data]) => {
      const pct = Math.round(data.rate * 100);
      const barClass = pct >= 75 ? 'success' : pct >= 50 ? '' : 'warning';
      return `
        <div style="margin-bottom:var(--space-4)">
          <div style="display:flex;justify-content:space-between;font-size:.875rem;margin-bottom:4px">
            <span>
              <i class="fa-solid fa-book-open" style="color:var(--clr-primary);margin-right:4px" aria-hidden="true"></i>
              <strong>${UI.escape(sub)}</strong> — ${data.done}/${data.total} tasks
            </span>
            <span>${pct}%</span>
          </div>
          <div class="progress-bar-wrap" role="progressbar"
               aria-valuenow="${pct}" aria-valuemin="0" aria-valuemax="100">
            <div class="progress-bar ${barClass}" style="width:${pct}%"></div>
          </div>
        </div>`;
    }).join('');
  },
};
