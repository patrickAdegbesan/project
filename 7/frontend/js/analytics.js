/**
 * analytics.js — Dashboard charts and summary cards
 */

'use strict';

const Charts = {};

const Analytics = {
  async load() {
    const res = await API.get('/analytics/dashboard');
    if (!res || !res.ok) return;
    const stats = res.data.data.stats;
    this.renderStatCards(stats.task_summary, stats.total_minutes_7d);
    this.renderTaskStatusChart(stats.task_summary);
    this.renderPriorityChart(stats.priority_breakdown);
    this.renderStudyHoursChart(stats.study_hours_week);
    this.renderSubjectChart(stats.subject_distribution);
    this.renderCompletionTrendChart(stats.completion_trend);
    this.renderGoals(stats.goals_summary);
    this.renderRecentCompleted(stats.recent_completed);
  },

  renderStatCards(summary, minutes7d) {
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    set('statTotal',     summary.total);
    set('statCompleted', summary.completed);
    set('statOverdue',   summary.overdue);
    set('statHours7d',   UI.minutesToHM(minutes7d));
    set('statRate',      summary.completion_rate + '%');
  },

  renderTaskStatusChart(summary) {
    const ctx = document.getElementById('taskStatusChart');
    if (!ctx) return;
    Charts.taskStatus?.destroy();
    Charts.taskStatus = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Completed', 'In Progress', 'Pending', 'Overdue'],
        datasets: [{
          data: [summary.completed, summary.in_progress, summary.pending, summary.overdue],
          backgroundColor: ['#27ae60', '#4A90D9', '#f39c12', '#e74c3c'],
          borderWidth: 2,
          borderColor: getComputedStyle(document.body).getPropertyValue('--clr-surface').trim() || '#fff',
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom' } },
        cutout: '65%',
      },
    });
  },

  renderPriorityChart(priority) {
    const ctx = document.getElementById('priorityChart');
    if (!ctx) return;
    Charts.priority?.destroy();
    Charts.priority = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Low', 'Medium', 'High', 'Urgent'],
        datasets: [{
          label: 'Tasks by Priority',
          data: [priority.low, priority.medium, priority.high, priority.urgent],
          backgroundColor: ['#27ae60', '#f39c12', '#e67e22', '#e74c3c'],
          borderRadius: 6,
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, ticks: { stepSize: 1 } },
          x: { grid: { display: false } },
        },
      },
    });
  },

  renderStudyHoursChart(weekData) {
    const ctx = document.getElementById('studyHoursChart');
    if (!ctx) return;
    Charts.studyHours?.destroy();
    Charts.studyHours = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: weekData.map(d => {
          const dt = new Date(d.date);
          return dt.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric' });
        }),
        datasets: [{
          label: 'Study Hours',
          data: weekData.map(d => d.hours),
          backgroundColor: 'rgba(74,144,217,0.7)',
          borderColor: '#4A90D9',
          borderWidth: 2,
          borderRadius: 6,
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, title: { display: true, text: 'Hours' } },
          x: { grid: { display: false } },
        },
      },
    });
  },

  renderSubjectChart(subjects) {
    const ctx = document.getElementById('subjectChart');
    if (!ctx || !subjects.length) return;
    Charts.subject?.destroy();
    const COLORS = ['#4A90D9','#6C63FF','#27ae60','#f39c12','#e74c3c','#2980b9','#8e44ad','#16a085'];
    Charts.subject = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: subjects.map(s => s.subject),
        datasets: [{
          data: subjects.map(s => s.count),
          backgroundColor: subjects.map((_, i) => COLORS[i % COLORS.length]),
          borderWidth: 2,
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { position: 'right' } },
      },
    });
  },

  renderCompletionTrendChart(trend) {
    const ctx = document.getElementById('trendChart');
    if (!ctx) return;
    const recent = trend.slice(-14);
    Charts.trend?.destroy();
    Charts.trend = new Chart(ctx, {
      type: 'line',
      data: {
        labels: recent.map(d => {
          const dt = new Date(d.date);
          return dt.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
        }),
        datasets: [{
          label: 'Tasks Completed',
          data: recent.map(d => d.completed),
          borderColor: '#27ae60',
          backgroundColor: 'rgba(39,174,96,0.1)',
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointHoverRadius: 6,
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, ticks: { stepSize: 1 } },
          x: { grid: { display: false } },
        },
      },
    });
  },

  renderGoals(goals) {
    const container = document.getElementById('analyticsGoals');
    if (!container) return;
    if (!goals.length) {
      container.innerHTML = '<p class="text-muted">No active goals.</p>';
      return;
    }
    container.innerHTML = goals.map(g => `
      <div style="margin-bottom:var(--space-4)">
        <div style="display:flex;justify-content:space-between;font-size:.875rem;margin-bottom:4px">
          <span><i class="fa-solid fa-flag" style="color:var(--clr-primary);margin-right:4px"></i>${UI.escape(g.title)}</span>
          <strong>${g.percent}%</strong>
        </div>
        <div class="progress-bar-wrap" role="progressbar"
             aria-valuenow="${g.percent}" aria-valuemin="0" aria-valuemax="100">
          <div class="progress-bar ${g.percent >= 100 ? 'success' : ''}" style="width:${g.percent}%"></div>
        </div>
      </div>`).join('');
  },

  renderRecentCompleted(tasks) {
    const container = document.getElementById('recentCompleted');
    if (!container) return;
    if (!tasks.length) {
      container.innerHTML = '<p class="text-muted">No completed tasks yet.</p>';
      return;
    }
    container.innerHTML = tasks.map(t => `
      <div style="display:flex;align-items:center;gap:var(--space-3);padding:var(--space-3) 0;border-bottom:1px solid var(--clr-border)">
        <i class="fa-solid fa-circle-check" style="color:var(--clr-success);font-size:1.2rem" aria-hidden="true"></i>
        <div>
          <div style="font-size:.875rem;font-weight:600">${UI.escape(t.title)}</div>
          <div style="font-size:.75rem;color:var(--clr-text-muted)">
            <i class="fa-regular fa-calendar" aria-hidden="true"></i>
            ${t.completed_at ? new Date(t.completed_at).toLocaleDateString('en-GB') : ''}
          </div>
        </div>
      </div>`).join('');
  },
};

// Dashboard summary (lighter version for the dashboard page)
const Dashboard = {
  async load() {
    const [tasksRes, statsRes] = await Promise.all([
      API.get('/tasks?status=pending'),
      API.get('/analytics/dashboard'),
    ]);

    if (statsRes?.ok) {
      const stats = statsRes.data.data.stats;
      Analytics.renderStatCards(stats.task_summary, stats.total_minutes_7d);
      Analytics.renderTaskStatusChart(stats.task_summary);
    }

    if (tasksRes?.ok) {
      const tasks = tasksRes.data.data.tasks;
      const now = new Date().toISOString();
      const upcoming = tasks
        .filter(t => t.due_date && t.due_date >= now)
        .sort((a, b) => a.due_date.localeCompare(b.due_date))
        .slice(0, 5);

      const list = document.getElementById('dashboardUpcoming');
      if (list) {
        if (!upcoming.length) {
          list.innerHTML = `
            <div style="text-align:center;padding:var(--space-6);color:var(--clr-text-muted)">
              <i class="fa-solid fa-circle-check" style="font-size:2rem;margin-bottom:var(--space-3)"></i>
              <p style="font-size:.875rem">No upcoming deadlines.</p>
            </div>`;
        } else {
          list.innerHTML = upcoming.map(t => {
            const dueDate = new Date(t.due_date);
            const diff = Math.ceil((dueDate - new Date()) / (1000 * 60 * 60 * 24));
            const urgency = diff <= 1 ? 'var(--clr-danger)' : diff <= 3 ? 'var(--clr-warning)' : 'var(--clr-text-muted)';
            return `
              <div style="display:flex;justify-content:space-between;align-items:center;
                          padding:var(--space-3) 0;border-bottom:1px solid var(--clr-border)">
                <div style="display:flex;align-items:center;gap:var(--space-2)">
                  <i class="fa-solid fa-circle" style="font-size:.5rem;color:var(--clr-${t.priority === 'urgent' ? 'danger' : t.priority === 'high' ? 'warning' : 'primary'})" aria-hidden="true"></i>
                  <span style="font-size:.875rem;font-weight:500">${UI.escape(t.title)}</span>
                </div>
                <span style="font-size:.75rem;color:${urgency};white-space:nowrap;margin-left:var(--space-3)">
                  <i class="fa-solid fa-clock" aria-hidden="true"></i>
                  ${diff === 0 ? 'Today' : diff === 1 ? 'Tomorrow' : `${diff}d`}
                </span>
              </div>`;
          }).join('');
        }
      }
    }
  },
};
