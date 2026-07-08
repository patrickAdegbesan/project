/**
 * admin.js — Admin dashboard logic
 */

'use strict';

const Admin = {
  charts: {},

  async load() {
    // Only admins should ever reach this page, but guard client-side too
    if (!State.user?.is_admin) {
      document.getElementById('adminAccessDenied').classList.remove('hidden');
      document.getElementById('adminContent').classList.add('hidden');
      return;
    }
    document.getElementById('adminAccessDenied').classList.add('hidden');
    document.getElementById('adminContent').classList.remove('hidden');

    await Promise.all([
      this.loadStats(),
      this.loadUsers(),
      this.loadActivity(),
      this.loadSubjects(),
      this.loadCharts(),
    ]);
  },

  // -------------------------------------------------------------------------
  // System stats cards
  // -------------------------------------------------------------------------
  async loadStats() {
    const res = await API.get('/admin/stats');
    if (!res || !res.ok) return;
    const s = res.data.data.stats;

    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    set('adminStatUsers',      s.total_users);
    set('adminStatNewUsers',   s.new_users_7d);
    set('adminStatActiveToday',s.active_today);
    set('adminStatTasks',      s.total_tasks);
    set('adminStatCompleted',  s.completed_tasks);
    set('adminStatOverdue',    s.overdue_tasks);
    set('adminStatRate',       s.completion_rate + '%');
    set('adminStatHours',      UI.minutesToHM(s.total_minutes));
    set('adminStatGoals',      s.total_goals);
    set('adminStatAchieved',   s.achieved_goals);
  },

  // -------------------------------------------------------------------------
  // User table
  // -------------------------------------------------------------------------
  async loadUsers(search = '') {
    const res = await API.get(`/admin/users${search ? '?search=' + encodeURIComponent(search) : ''}`);
    if (!res || !res.ok) return;
    this.renderUserTable(res.data.data.users);
  },

  renderUserTable(users) {
    const tbody = document.getElementById('adminUserTableBody');
    if (!tbody) return;

    if (!users.length) {
      tbody.innerHTML = `
        <tr><td colspan="7" style="text-align:center;padding:var(--space-8);color:var(--clr-text-muted)">
          <i class="fa-solid fa-users-slash" style="font-size:1.5rem;display:block;margin-bottom:8px"></i>
          No users found.
        </td></tr>`;
      return;
    }

    tbody.innerHTML = users.map(u => {
      const rate = u.task_count
        ? Math.round(u.completed_count / u.task_count * 100)
        : 0;
      const joined = u.created_at ? new Date(u.created_at).toLocaleDateString('en-GB') : '—';
      const lastLogin = u.last_login ? new Date(u.last_login).toLocaleDateString('en-GB') : 'Never';

      return `
        <tr>
          <td>
            <div style="display:flex;align-items:center;gap:10px">
              <div class="avatar" style="width:32px;height:32px;font-size:.75rem;flex-shrink:0">
                ${(u.full_name || u.username).slice(0,2).toUpperCase()}
              </div>
              <div>
                <div style="font-weight:600;font-size:.875rem">${UI.escape(u.full_name || u.username)}</div>
                <div style="font-size:.75rem;color:var(--clr-text-muted)">@${UI.escape(u.username)}</div>
              </div>
            </div>
          </td>
          <td style="font-size:.8rem">${UI.escape(u.email)}</td>
          <td style="text-align:center">
            <span style="font-weight:600">${u.task_count}</span>
            <span style="font-size:.75rem;color:var(--clr-text-muted)"> / ${u.completed_count} done</span>
          </td>
          <td style="text-align:center;font-size:.875rem">
            <span style="color:${rate >= 70 ? 'var(--clr-success)' : rate >= 40 ? 'var(--clr-warning)' : 'var(--clr-danger)'}">
              ${rate}%
            </span>
          </td>
          <td style="text-align:center;font-size:.8rem">${UI.minutesToHM(u.total_minutes)}</td>
          <td style="text-align:center;font-size:.8rem">${joined}</td>
          <td>
            <div style="display:flex;gap:6px;justify-content:center">
              <button class="btn btn-sm btn-secondary" onclick="Admin.viewUser(${u.id})"
                      title="View details" aria-label="View user ${UI.escape(u.username)}">
                <i class="fa-solid fa-eye" aria-hidden="true"></i>
              </button>
              <button class="btn btn-sm ${u.is_admin ? 'btn-warning' : 'btn-secondary'}"
                      onclick="Admin.toggleAdmin(${u.id}, '${UI.escape(u.username)}')"
                      title="${u.is_admin ? 'Revoke admin' : 'Grant admin'}"
                      aria-label="${u.is_admin ? 'Revoke' : 'Grant'} admin for ${UI.escape(u.username)}"
                      style="${u.is_admin ? 'background:var(--clr-warning);color:#000' : ''}">
                <i class="fa-solid fa-${u.is_admin ? 'shield-halved' : 'shield'}" aria-hidden="true"></i>
              </button>
              <button class="btn btn-sm btn-danger" onclick="Admin.deleteUser(${u.id}, '${UI.escape(u.username)}')"
                      title="Delete user" aria-label="Delete user ${UI.escape(u.username)}">
                <i class="fa-solid fa-trash" aria-hidden="true"></i>
              </button>
            </div>
          </td>
        </tr>`;
    }).join('');
  },

  // -------------------------------------------------------------------------
  // User detail modal
  // -------------------------------------------------------------------------
  async viewUser(userId) {
    const res = await API.get(`/admin/users/${userId}`);
    if (!res || !res.ok) { UI.toast('Failed to load user details.', 'error'); return; }

    const { user, tasks, logs, subjects } = res.data.data;

    const totalMinutes = logs.reduce((s, l) => s + l.total_minutes, 0);

    document.getElementById('adminUserModalName').textContent =
      user.full_name || user.username;
    document.getElementById('adminUserModalEmail').textContent = user.email;
    document.getElementById('adminUserModalJoined').textContent =
      user.created_at ? new Date(user.created_at).toLocaleDateString('en-GB') : '—';
    document.getElementById('adminUserModalHours').textContent =
      UI.minutesToHM(totalMinutes);

    // Recent tasks
    const taskList = document.getElementById('adminUserTaskList');
    if (taskList) {
      if (!tasks.length) {
        taskList.innerHTML = '<p class="text-muted" style="font-size:.875rem">No tasks.</p>';
      } else {
        taskList.innerHTML = tasks.slice(0, 10).map(t => `
          <div style="display:flex;justify-content:space-between;align-items:center;
                      padding:var(--space-2) 0;border-bottom:1px solid var(--clr-border)">
            <span style="font-size:.8rem;flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
              <i class="fa-solid fa-${t.status === 'completed' ? 'circle-check' : 'clock'}"
                 style="color:${t.status === 'completed' ? 'var(--clr-success)' : 'var(--clr-text-muted)'};
                        margin-right:6px" aria-hidden="true"></i>
              ${UI.escape(t.title)}
            </span>
            <span class="priority-badge ${t.priority}" style="flex-shrink:0;margin-left:8px">${t.priority}</span>
          </div>`).join('');
      }
    }

    // Subject breakdown
    const subList = document.getElementById('adminUserSubjects');
    if (subList) {
      if (!subjects.length) {
        subList.innerHTML = '<p class="text-muted" style="font-size:.875rem">No subject data.</p>';
      } else {
        subList.innerHTML = subjects.slice(0, 6).map(s => {
          const pct = s.total ? Math.round(s.done / s.total * 100) : 0;
          return `
            <div style="margin-bottom:10px">
              <div style="display:flex;justify-content:space-between;font-size:.8rem;margin-bottom:3px">
                <span>${UI.escape(s.subject)}</span>
                <span>${s.done}/${s.total} (${pct}%)</span>
              </div>
              <div class="progress-bar-wrap">
                <div class="progress-bar ${pct >= 70 ? 'success' : pct >= 40 ? '' : 'warning'}"
                     style="width:${pct}%"></div>
              </div>
            </div>`;
        }).join('');
      }
    }

    UI.openModal('adminUserModal');
  },

  // -------------------------------------------------------------------------
  // Admin toggle
  // -------------------------------------------------------------------------
  async toggleAdmin(userId, username) {
    if (!confirm(`Toggle admin status for @${username}?`)) return;
    const res = await API.put(`/admin/users/${userId}/toggle-admin`, {});
    if (!res || !res.ok) { UI.toast(res?.data?.error || 'Failed.', 'error'); return; }
    UI.toast(res.data.data.message, 'success');
    await this.loadUsers();
  },

  // -------------------------------------------------------------------------
  // Delete user
  // -------------------------------------------------------------------------
  async deleteUser(userId, username) {
    if (!confirm(`Permanently delete user @${username} and ALL their data?\n\nThis cannot be undone.`)) return;
    const res = await API.delete(`/admin/users/${userId}`);
    if (!res || !res.ok) { UI.toast(res?.data?.error || 'Failed to delete user.', 'error'); return; }
    UI.toast(`User @${username} deleted.`, 'success');
    await this.loadUsers();
  },

  // -------------------------------------------------------------------------
  // Activity feed
  // -------------------------------------------------------------------------
  async loadActivity() {
    const res = await API.get('/admin/activity?limit=20');
    if (!res || !res.ok) return;
    this.renderActivity(res.data.data.activity);
  },

  renderActivity(feed) {
    const container = document.getElementById('adminActivityFeed');
    if (!container) return;

    if (!feed.length) {
      container.innerHTML = '<p class="text-muted" style="font-size:.875rem">No recent activity.</p>';
      return;
    }

    container.innerHTML = feed.map(item => {
      const isCompletion = item.type === 'task_completed';
      const icon  = isCompletion ? 'circle-check' : 'user-plus';
      const color = isCompletion ? 'var(--clr-success)' : 'var(--clr-primary)';
      const time  = item.time ? new Date(item.time).toLocaleString('en-GB', {
        day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit'
      }) : '';

      return `
        <div style="display:flex;align-items:flex-start;gap:10px;
                    padding:var(--space-3) 0;border-bottom:1px solid var(--clr-border)">
          <div style="width:32px;height:32px;border-radius:50%;
                      background:${color}22;display:flex;align-items:center;
                      justify-content:center;flex-shrink:0;margin-top:2px">
            <i class="fa-solid fa-${icon}" style="color:${color};font-size:.85rem" aria-hidden="true"></i>
          </div>
          <div style="flex:1;min-width:0">
            <div style="font-size:.8rem;font-weight:600">
              ${UI.escape(item.full_name || item.username)}
              <span style="font-weight:400;color:var(--clr-text-muted)">@${UI.escape(item.username)}</span>
            </div>
            <div style="font-size:.8rem;color:var(--clr-text-secondary);
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
              ${UI.escape(item.detail)}
            </div>
            <div style="font-size:.7rem;color:var(--clr-text-muted);margin-top:2px">
              <i class="fa-regular fa-clock" aria-hidden="true"></i> ${time}
            </div>
          </div>
        </div>`;
    }).join('');
  },

  // -------------------------------------------------------------------------
  // Popular subjects table
  // -------------------------------------------------------------------------
  async loadSubjects() {
    const res = await API.get('/admin/subjects');
    if (!res || !res.ok) return;
    const container = document.getElementById('adminSubjectsTable');
    if (!container) return;

    const subjects = res.data.data.subjects;
    if (!subjects.length) {
      container.innerHTML = '<p class="text-muted">No subject data yet.</p>';
      return;
    }

    container.innerHTML = `
      <table style="width:100%;border-collapse:collapse;font-size:.85rem">
        <thead>
          <tr style="border-bottom:2px solid var(--clr-border)">
            <th style="text-align:left;padding:var(--space-2) var(--space-3)">Subject</th>
            <th style="text-align:center;padding:var(--space-2)">Tasks</th>
            <th style="text-align:center;padding:var(--space-2)">Users</th>
            <th style="text-align:left;padding:var(--space-2) var(--space-3);min-width:120px">Completion</th>
          </tr>
        </thead>
        <tbody>
          ${subjects.map(s => `
            <tr style="border-bottom:1px solid var(--clr-border)">
              <td style="padding:var(--space-2) var(--space-3);font-weight:500">${UI.escape(s.subject)}</td>
              <td style="text-align:center;padding:var(--space-2)">${s.total_tasks}</td>
              <td style="text-align:center;padding:var(--space-2)">${s.user_count}</td>
              <td style="padding:var(--space-2) var(--space-3)">
                <div style="display:flex;align-items:center;gap:8px">
                  <div class="progress-bar-wrap" style="flex:1">
                    <div class="progress-bar ${s.completion_rate >= 70 ? 'success' : s.completion_rate >= 40 ? '' : 'warning'}"
                         style="width:${s.completion_rate}%"></div>
                  </div>
                  <span style="font-size:.75rem;color:var(--clr-text-muted);width:36px;text-align:right">
                    ${s.completion_rate}%
                  </span>
                </div>
              </td>
            </tr>`).join('')}
        </tbody>
      </table>`;
  },

  // -------------------------------------------------------------------------
  // Charts
  // -------------------------------------------------------------------------
  async loadCharts() {
    const [signupsRes, tasksRes] = await Promise.all([
      API.get('/admin/chart/signups'),
      API.get('/admin/chart/tasks'),
    ]);

    if (signupsRes?.ok) this.renderSignupsChart(signupsRes.data.data.trend);
    if (tasksRes?.ok)   this.renderTasksChart(tasksRes.data.data.trend);
  },

  renderSignupsChart(trend) {
    const ctx = document.getElementById('adminSignupsChart');
    if (!ctx) return;
    this.charts.signups?.destroy();
    this.charts.signups = new Chart(ctx, {
      type: 'line',
      data: {
        labels: trend.map(d => {
          const dt = new Date(d.date);
          return dt.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
        }),
        datasets: [{
          label: 'New Users',
          data: trend.map(d => d.count),
          borderColor: '#6C63FF',
          backgroundColor: 'rgba(108,99,255,0.1)',
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          pointHoverRadius: 5,
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, ticks: { stepSize: 1 } },
          x: {
            grid: { display: false },
            ticks: { maxTicksLimit: 8 },
          },
        },
      },
    });
  },

  renderTasksChart(trend) {
    const ctx = document.getElementById('adminTasksChart');
    if (!ctx) return;
    this.charts.tasks?.destroy();
    this.charts.tasks = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: trend.map(d => {
          const dt = new Date(d.date);
          return dt.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
        }),
        datasets: [{
          label: 'Tasks Completed',
          data: trend.map(d => d.count),
          backgroundColor: 'rgba(39,174,96,0.7)',
          borderColor: '#27ae60',
          borderWidth: 1,
          borderRadius: 4,
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, ticks: { stepSize: 1 } },
          x: {
            grid: { display: false },
            ticks: { maxTicksLimit: 8 },
          },
        },
      },
    });
  },
};

// User search
document.getElementById('adminUserSearch')?.addEventListener('input', e => {
  clearTimeout(Admin._searchTimer);
  Admin._searchTimer = setTimeout(() => Admin.loadUsers(e.target.value.trim()), 300);
});
