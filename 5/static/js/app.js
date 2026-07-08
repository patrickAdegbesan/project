/* ── TaskMind frontend ─────────────────────────────────────────────────────── */

let allTasks = [];
let currentFilter = 'all';
let nlpModal, manualModal, editModal;

document.addEventListener('DOMContentLoaded', () => {
  if (typeof TASKS_DATA !== 'undefined') {
    allTasks = TASKS_DATA;
    renderTasks();
    initChart();
    initModals();
    initNLP();
    initFilters();
    initTooltips();
  }
});

// ── Chart ──────────────────────────────────────────────────────────────────
function initChart() {
  const ctx = document.getElementById('productivityChart');
  if (!ctx) return;
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: CHART_LABELS,
      datasets: [{
        label: 'Completed',
        data: CHART_DATA,
        backgroundColor: 'rgba(21,101,192,0.7)',
        borderRadius: 6,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, ticks: { stepSize: 1 }, grid: { color: 'rgba(0,0,0,0.05)' } },
        x: { grid: { display: false } }
      }
    }
  });
}

// ── Modals ─────────────────────────────────────────────────────────────────
function initModals() {
  nlpModal    = new bootstrap.Modal(document.getElementById('nlpModal'));
  manualModal = new bootstrap.Modal(document.getElementById('manualModal'));
  editModal   = new bootstrap.Modal(document.getElementById('editModal'));

  document.getElementById('modalCreateBtn').addEventListener('click', createFromNLP);
  document.getElementById('manualCreateBtn').addEventListener('click', createManual);
  document.getElementById('editSaveBtn').addEventListener('click', saveEdit);
}

function openManualModal() {
  document.getElementById('manualTitle').value = '';
  document.getElementById('manualDesc').value = '';
  document.getElementById('manualDate').value = '';
  document.getElementById('manualTime').value = '';
  document.getElementById('manualImportance').value = '2';
  document.getElementById('manualEffort').value = '30';
  manualModal.show();
}

// ── NLP ────────────────────────────────────────────────────────────────────
function initNLP() {
  const input = document.getElementById('nlpInput');
  const btn   = document.getElementById('nlpParseBtn');
  btn.addEventListener('click', () => triggerParse());
  input.addEventListener('keydown', e => { if (e.key === 'Enter') triggerParse(); });
}

async function triggerParse() {
  const text = document.getElementById('nlpInput').value.trim();
  if (!text) return;
  const status = document.getElementById('nlpStatus');
  status.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Parsing…';
  try {
    const res = await fetch('/api/parse', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const data = await res.json();
    status.innerHTML = '';
    populateNLPModal(data);
    nlpModal.show();
  } catch (e) {
    status.innerHTML = '<span class="text-danger">Parse error. Try again.</span>';
  }
}

function populateNLPModal(data) {
  document.getElementById('modalTitle').value    = data.title || '';
  document.getElementById('modalDate').value     = data.due_date || '';
  document.getElementById('modalTime').value     = data.due_time || '';
  document.getElementById('modalImportance').value = String(data.importance || 2);
  document.getElementById('modalEffort').value   = data.effort_minutes || 30;
  updateModalScore(data.priority_pct, data.priority_label);
}

function updateModalScore(pct, label) {
  document.getElementById('modalScore').textContent = pct + '%';
  const badge = document.getElementById('modalPriorityBadge');
  badge.textContent = label;
  badge.className = 'ms-2 badge badge-' + label;
  document.getElementById('modalScoreExpl').textContent =
    `Score: ${pct}% — ${label} priority based on importance, deadline proximity, and effort.`;
}

async function createFromNLP() {
  const payload = {
    title: document.getElementById('modalTitle').value.trim(),
    due_date: document.getElementById('modalDate').value,
    due_time: document.getElementById('modalTime').value,
    importance: document.getElementById('modalImportance').value,
    effort_minutes: document.getElementById('modalEffort').value,
  };
  if (!payload.title) { alert('Please enter a title.'); return; }
  await createTask(payload);
  nlpModal.hide();
  document.getElementById('nlpInput').value = '';
}

async function createManual() {
  const payload = {
    title: document.getElementById('manualTitle').value.trim(),
    description: document.getElementById('manualDesc').value.trim(),
    due_date: document.getElementById('manualDate').value,
    due_time: document.getElementById('manualTime').value,
    importance: document.getElementById('manualImportance').value,
    effort_minutes: document.getElementById('manualEffort').value,
  };
  if (!payload.title) { alert('Please enter a title.'); return; }
  await createTask(payload);
  manualModal.hide();
}

async function createTask(payload) {
  const res = await fetch('/api/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  if (data.success) {
    allTasks.unshift(data.task);
    renderTasks();
    showToast('Task created!', 'success');
    updateStatBadges();
  }
}

// ── Task rendering ─────────────────────────────────────────────────────────
function initFilters() {
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => {
        b.classList.remove('active', 'btn-primary', 'btn-outline-secondary',
          'btn-outline-success', 'btn-outline-danger');
      });
      btn.classList.add('active');
      currentFilter = btn.dataset.filter;
      renderTasks();
    });
  });
}

function filteredTasks() {
  const today = new Date().toISOString().split('T')[0];
  switch (currentFilter) {
    case 'pending':   return allTasks.filter(t => !t.completed);
    case 'completed': return allTasks.filter(t => t.completed);
    case 'overdue':   return allTasks.filter(t => t.overdue);
    default:          return allTasks;
  }
}

function renderTasks() {
  const container = document.getElementById('taskList');
  const tasks = filteredTasks();
  if (!tasks.length) {
    container.innerHTML = '<div class="empty-state"><i class="fas fa-inbox fa-3x mb-3"></i><p>No tasks here.</p></div>';
    return;
  }
  container.innerHTML = tasks.map(taskHTML).join('');
  // Bind checkboxes
  container.querySelectorAll('.task-checkbox').forEach(cb => {
    cb.addEventListener('click', () => toggleComplete(parseInt(cb.dataset.id), cb.classList.contains('checked')));
  });
  initTooltips();
}

function taskHTML(t) {
  const overdueTag = t.overdue
    ? '<span class="badge overdue-badge text-white ms-2 small"><i class="fas fa-exclamation-circle me-1"></i>Overdue</span>' : '';
  const daysTag = (!t.completed && t.days_left !== null && !t.overdue)
    ? `<span class="badge bg-light text-dark ms-2 small">${t.days_left === 0 ? 'Due today' : `${t.days_left}d left`}</span>` : '';
  return `
  <div class="card task-item priority-${t.priority_label} ${t.completed ? 'completed-task' : ''}" id="task-${t.id}">
    <div class="card-body py-3 d-flex align-items-start gap-3">
      <div class="task-checkbox ${t.completed ? 'checked' : ''}" data-id="${t.id}" title="Mark complete"></div>
      <div class="flex-grow-1 min-width-0">
        <div class="d-flex align-items-center flex-wrap gap-1 mb-1">
          <span class="task-title fw-semibold">${escHtml(t.title)}</span>
          ${overdueTag}${daysTag}
        </div>
        <div class="text-muted small d-flex flex-wrap gap-3">
          ${t.due_date ? `<span><i class="fas fa-calendar-alt me-1"></i>${t.due_date_fmt}${t.due_time ? ' ' + t.due_time : ''}</span>` : ''}
          <span><i class="fas fa-stopwatch me-1"></i>${t.effort_fmt}</span>
          <span class="badge badge-${t.priority_label} rounded-pill"
            data-bs-toggle="tooltip"
            title="Priority score: ${t.priority_pct}% — ${t.priority_label} priority based on importance, deadline, and effort.">
            ${t.priority_label}
          </span>
        </div>
        <div class="text-muted small mt-1 fst-italic">
          <i class="fas fa-robot me-1 text-primary opacity-50"></i>Priority score: ${t.priority_pct}% — ${t.priority_label} due to ${priorityReason(t)}
        </div>
      </div>
      <div class="dropdown flex-shrink-0">
        <button class="btn btn-sm btn-light" data-bs-toggle="dropdown"><i class="fas fa-ellipsis-v"></i></button>
        <ul class="dropdown-menu dropdown-menu-end shadow-sm">
          <li><a class="dropdown-item" href="#" onclick="openEdit(${t.id})"><i class="fas fa-edit me-2 text-primary"></i>Edit</a></li>
          <li><a class="dropdown-item text-danger" href="#" onclick="deleteTask(${t.id})"><i class="fas fa-trash me-2"></i>Delete</a></li>
        </ul>
      </div>
    </div>
  </div>`;
}

function priorityReason(t) {
  const reasons = [];
  if (t.importance === 3) reasons.push('high importance');
  if (t.overdue || (t.days_left !== null && t.days_left <= 2)) reasons.push('urgent deadline');
  if (t.effort_minutes <= 30) reasons.push('quick task');
  return reasons.length ? reasons.join(' + ') : 'balanced factors';
}

// ── Do Next done button ────────────────────────────────────────────────────
async function completeDoNext(id) {
  const btn = document.querySelector('.do-next-done-btn');
  if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Marking done…'; }
  await toggleComplete(id, false);
  // Reload page so Do Next card refreshes to next task
  setTimeout(() => location.reload(), 800);
}

// ── Complete toggle ────────────────────────────────────────────────────────
async function toggleComplete(id, wasChecked) {
  const newCompleted = !wasChecked;
  const res = await fetch(`/api/tasks/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ completed: newCompleted })
  });
  const data = await res.json();
  if (data.success) {
    const idx = allTasks.findIndex(t => t.id === id);
    if (idx !== -1) allTasks[idx] = data.task;
    renderTasks();
    updateStatBadges();
    if (newCompleted && data.reschedule_suggestions && data.reschedule_suggestions.length) {
      showRescheduleSuggestion(data.reschedule_suggestions[0]);
    } else if (newCompleted) {
      showToast('Task completed! 🎉', 'success');
    }
  }
}

// ── Edit ───────────────────────────────────────────────────────────────────
function openEdit(id) {
  const t = allTasks.find(t => t.id === id);
  if (!t) return;
  document.getElementById('editTaskId').value = id;
  document.getElementById('editTitle').value  = t.title;
  document.getElementById('editDesc').value   = t.description || '';
  document.getElementById('editDate').value   = t.due_date || '';
  document.getElementById('editTime').value   = t.due_time || '';
  document.getElementById('editImportance').value = String(t.importance);
  document.getElementById('editEffort').value = t.effort_minutes;
  editModal.show();
}

async function saveEdit() {
  const id = document.getElementById('editTaskId').value;
  const payload = {
    title: document.getElementById('editTitle').value.trim(),
    description: document.getElementById('editDesc').value.trim(),
    due_date: document.getElementById('editDate').value,
    due_time: document.getElementById('editTime').value,
    importance: document.getElementById('editImportance').value,
    effort_minutes: document.getElementById('editEffort').value,
  };
  const res = await fetch(`/api/tasks/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  if (data.success) {
    const idx = allTasks.findIndex(t => t.id === parseInt(id));
    if (idx !== -1) allTasks[idx] = data.task;
    renderTasks();
    editModal.hide();
    showToast('Task updated!', 'success');
  }
}

// ── Delete ─────────────────────────────────────────────────────────────────
async function deleteTask(id) {
  if (!confirm('Delete this task?')) return;
  const res = await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
  const data = await res.json();
  if (data.success) {
    allTasks = allTasks.filter(t => t.id !== id);
    renderTasks();
    updateStatBadges();
    showToast('Task deleted.', 'info');
  }
}

// ── Reschedule toast ───────────────────────────────────────────────────────
function showRescheduleSuggestion(s) {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const newDate = tomorrow.toISOString().split('T')[0];
  const id = `toast-${Date.now()}`;
  const html = `
    <div id="${id}" class="toast show align-items-center" role="alert">
      <div class="toast-body p-3">
        <strong class="d-block mb-1"><i class="fas fa-calendar-alt me-2 text-warning"></i>Reschedule Suggestion</strong>
        <p class="mb-2 small">"${escHtml(s.title)}" is overdue. Move to tomorrow?</p>
        <div class="d-flex gap-2">
          <button class="btn btn-sm btn-warning text-white" onclick="acceptReschedule(${s.id},'${newDate}','${id}')">
            <i class="fas fa-check me-1"></i>Accept
          </button>
          <button class="btn btn-sm btn-outline-secondary" onclick="dismissToast('${id}')">
            <i class="fas fa-times me-1"></i>Dismiss
          </button>
        </div>
      </div>
    </div>`;
  document.getElementById('toast-container').insertAdjacentHTML('beforeend', html);
}

async function acceptReschedule(taskId, newDate, toastId) {
  const res = await fetch(`/api/tasks/${taskId}/reschedule`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ new_date: newDate })
  });
  const data = await res.json();
  if (data.success) {
    const idx = allTasks.findIndex(t => t.id === taskId);
    if (idx !== -1) allTasks[idx] = data.task;
    renderTasks();
    dismissToast(toastId);
    showToast('Task rescheduled to tomorrow!', 'success');
  }
}

function dismissToast(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

// ── Stat badges (live update) ──────────────────────────────────────────────
function updateStatBadges() {
  const today = new Date().toISOString().split('T')[0];
  const total     = allTasks.length;
  const completed = allTasks.filter(t => t.completed).length;
  const pending   = allTasks.filter(t => !t.completed).length;
  const overdue   = allTasks.filter(t => t.overdue).length;
  const nums = document.querySelectorAll('.stat-number');
  if (nums[0]) nums[0].textContent = total;
  if (nums[1]) nums[1].textContent = completed;
  if (nums[2]) nums[2].textContent = pending;
  if (nums[3]) nums[3].textContent = overdue;
}

// ── Utilities ──────────────────────────────────────────────────────────────
function showToast(msg, type = 'info') {
  const colors = { success: '#4CAF50', danger: '#F44336', info: '#1565C0', warning: '#FF9800' };
  const id = `toast-${Date.now()}`;
  const html = `
    <div id="${id}" class="toast show" role="alert" style="border-left: 4px solid ${colors[type] || colors.info};">
      <div class="toast-body d-flex align-items-center gap-2">
        <span>${msg}</span>
        <button type="button" class="btn-close ms-auto btn-close-sm" onclick="dismissToast('${id}')"></button>
      </div>
    </div>`;
  document.getElementById('toast-container').insertAdjacentHTML('beforeend', html);
  setTimeout(() => dismissToast(id), 4000);
}

function escHtml(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function initTooltips() {
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
    if (!el._bsTooltip) {
      el._bsTooltip = new bootstrap.Tooltip(el, { trigger: 'hover' });
    }
  });
}
