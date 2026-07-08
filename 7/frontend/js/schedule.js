/**
 * schedule.js — Weekly schedule planner
 */

'use strict';

const Schedule = {
  blocks: [],
  currentWeekStart: null,
  _weekOffset: 0,

  _getMonday(offset = 0) {
    const d = new Date();
    d.setDate(d.getDate() - d.getDay() + 1 + offset * 7);
    return d.toISOString().slice(0, 10);
  },

  async load(weekStart = null) {
    this.currentWeekStart = weekStart || this._getMonday();
    const res = await API.get(`/schedule?week=${this.currentWeekStart}`);
    if (!res || !res.ok) return;
    this.blocks = res.data.data.blocks;
    this.renderWeek();
    this.renderTodayList();
  },

  renderWeek() {
    const grid = document.getElementById('weekGrid');
    if (!grid) return;

    const days = this._weekDays(this.currentWeekStart);
    const todayISO = new Date().toISOString().slice(0, 10);

    let headers = '<div class="day-header" style="grid-column:1;font-size:.7rem">Time</div>';
    days.forEach(({ label, iso }) => {
      headers += `<div class="day-header ${iso === todayISO ? 'today' : ''}" data-date="${iso}">${label}</div>`;
    });

    let rows = '';
    for (let h = 8; h <= 21; h++) {
      const timeLabel = `${String(h).padStart(2,'0')}:00`;
      rows += `<div style="font-size:.7rem;color:var(--clr-text-muted);padding:4px 6px;text-align:right;
                            border-bottom:1px solid var(--clr-border)">${timeLabel}</div>`;
      days.forEach(({ iso }) => {
        const cellBlocks = this.blocks.filter(b =>
          b.block_date === iso && b.start_time.slice(0, 2) === String(h).padStart(2, '0')
        );
        const blockHTML = cellBlocks.map(b => `
          <div class="schedule-block type-${b.block_type}"
               style="background:${b.color || 'var(--clr-primary)'}"
               onclick="Schedule.openModal(${b.id})"
               title="${UI.escape(b.title)}"
               role="button" tabindex="0"
               aria-label="Block: ${UI.escape(b.title)} at ${b.start_time}">
            <strong style="display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
              ${UI.escape(b.title)}
            </strong>
            <span style="font-size:10px;opacity:.85">${b.start_time}–${b.end_time}</span>
          </div>`).join('');

        rows += `<div data-date="${iso}" data-hour="${h}"
                      onclick="Schedule.openNewBlockAt('${iso}', '${timeLabel}')"
                      style="min-height:50px;border-bottom:1px solid var(--clr-border);
                             border-right:1px solid var(--clr-border);padding:2px;cursor:pointer;">
                   ${blockHTML}
                 </div>`;
      });
    }

    grid.innerHTML = headers + rows;
    grid.style.gridTemplateColumns = `60px repeat(7, 1fr)`;

    const label = document.getElementById('weekLabel');
    if (label) {
      const start = new Date(this.currentWeekStart);
      const end   = new Date(this.currentWeekStart);
      end.setDate(end.getDate() + 6);
      label.textContent = `${start.toLocaleDateString('en-GB', { day:'numeric', month:'short' })} – ${end.toLocaleDateString('en-GB', { day:'numeric', month:'short', year:'numeric' })}`;
    }
  },

  renderTodayList() {
    const todayISO = new Date().toISOString().slice(0, 10);
    const todayBlocks = this.blocks.filter(b => b.block_date === todayISO);
    const container = document.getElementById('todayBlockList');
    if (!container) return;

    if (!todayBlocks.length) {
      container.innerHTML = `
        <div style="text-align:center;padding:var(--space-5);color:var(--clr-text-muted)">
          <i class="fa-regular fa-calendar-xmark" style="font-size:2rem;margin-bottom:var(--space-3)"></i>
          <p style="font-size:.875rem">No blocks scheduled for today.</p>
        </div>`;
      return;
    }

    const typeIcon = { study: 'book', break: 'mug-hot', review: 'rotate-left', exam: 'file-pen' };

    container.innerHTML = todayBlocks.map(b => `
      <div class="task-item" style="border-left:4px solid ${b.color || 'var(--clr-primary)'}">
        <div style="display:flex;align-items:center;justify-content:center;width:36px;height:36px;
                    border-radius:50%;background:${b.color || 'var(--clr-primary)'}22;flex-shrink:0">
          <i class="fa-solid fa-${typeIcon[b.block_type] || 'book'}"
             style="color:${b.color || 'var(--clr-primary)'}" aria-hidden="true"></i>
        </div>
        <div class="task-body">
          <div class="task-title">${UI.escape(b.title)}</div>
          <div class="task-meta">
            <span><i class="fa-solid fa-clock" aria-hidden="true"></i> ${b.start_time} – ${b.end_time}</span>
            ${b.subject ? `<span><i class="fa-solid fa-book-open" aria-hidden="true"></i> ${UI.escape(b.subject)}</span>` : ''}
            <span class="tag">${b.block_type}</span>
          </div>
        </div>
        <div class="task-actions">
          <button class="btn btn-sm btn-secondary" onclick="Schedule.openModal(${b.id})" aria-label="Edit block">
            <i class="fa-solid fa-pen" aria-hidden="true"></i>
          </button>
          <button class="btn btn-sm btn-danger" onclick="Schedule.deleteBlock(${b.id})" aria-label="Delete block">
            <i class="fa-solid fa-trash" aria-hidden="true"></i>
          </button>
        </div>
      </div>`).join('');
  },

  prevWeek() { this._weekOffset--; this.load(this._getMonday(this._weekOffset)); },
  nextWeek() { this._weekOffset++; this.load(this._getMonday(this._weekOffset)); },
  thisWeek() { this._weekOffset = 0; this.load(this._getMonday(0)); },

  _weekDays(monday) {
    const names = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
    return names.map((name, i) => {
      const d = new Date(monday);
      d.setDate(d.getDate() + i);
      return { label: `${name} ${d.getDate()}`, iso: d.toISOString().slice(0, 10) };
    });
  },

  editingBlockId: null,

  openNewBlockAt(date, time) {
    this.editingBlockId = null;
    const form = document.getElementById('blockForm');
    form.reset();
    form.block_date.value = date;
    form.start_time.value = time;
    form.end_time.value   = `${String(parseInt(time) + 1).padStart(2,'0')}:00`;
    document.getElementById('blockModalTitle').innerHTML =
      '<i class="fa-solid fa-calendar-plus" style="margin-right:6px;color:var(--clr-primary)"></i>New Study Block';
    UI.openModal('blockModal');
  },

  async openModal(id = null) {
    this.editingBlockId = id;
    const form = document.getElementById('blockForm');
    form.reset();

    if (id) {
      const block = this.blocks.find(b => b.id === id);
      if (!block) return;
      form.title.value      = block.title;
      form.subject.value    = block.subject || '';
      form.block_date.value = block.block_date;
      form.start_time.value = block.start_time;
      form.end_time.value   = block.end_time;
      form.block_type.value = block.block_type;
      form.color.value      = block.color || '#4A90D9';
      form.notes.value      = block.notes || '';
      document.getElementById('blockModalTitle').innerHTML =
        '<i class="fa-solid fa-pen-to-square" style="margin-right:6px;color:var(--clr-primary)"></i>Edit Block';
    } else {
      document.getElementById('blockModalTitle').innerHTML =
        '<i class="fa-solid fa-calendar-plus" style="margin-right:6px;color:var(--clr-primary)"></i>New Study Block';
    }

    UI.openModal('blockModal');
  },

  async submitModal() {
    const form = document.getElementById('blockForm');
    const data = {
      title:      form.title.value.trim(),
      subject:    form.subject.value.trim(),
      block_date: form.block_date.value,
      start_time: form.start_time.value,
      end_time:   form.end_time.value,
      block_type: form.block_type.value,
      color:      form.color.value,
      notes:      form.notes.value.trim(),
    };

    if (!data.title) { UI.toast('Title is required.', 'error'); return; }

    UI.setButtonLoading('btnSaveBlock', true);
    const res = this.editingBlockId
      ? await API.put(`/schedule/${this.editingBlockId}`, data)
      : await API.post('/schedule', data);
    UI.setButtonLoading('btnSaveBlock', false);

    if (!res || !res.ok) { UI.toast(res?.data?.error || 'Failed to save block.', 'error'); return; }
    UI.toast('Block saved!', 'success');
    UI.closeModal('blockModal');
    await this.load(this.currentWeekStart);
  },

  async deleteBlock(id) {
    if (!confirm('Delete this schedule block?')) return;
    const res = await API.delete(`/schedule/${id}`);
    if (!res || !res.ok) { UI.toast('Failed to delete block.', 'error'); return; }
    UI.toast('Block deleted.', 'success');
    await this.load(this.currentWeekStart);
  },
};

document.getElementById('btnPrevWeek')?.addEventListener('click', () => Schedule.prevWeek());
document.getElementById('btnNextWeek')?.addEventListener('click', () => Schedule.nextWeek());
document.getElementById('btnThisWeek')?.addEventListener('click', () => Schedule.thisWeek());
document.getElementById('btnAddBlock')?.addEventListener('click', () => Schedule.openModal());
document.getElementById('btnSaveBlock')?.addEventListener('click', () => Schedule.submitModal());
