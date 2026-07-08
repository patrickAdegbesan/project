/**
 * ui.js — Shared UI utilities
 */

'use strict';

const UI = {
  toast(message, type = 'default', duration = 3500) {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icon = { success: 'circle-check', error: 'circle-xmark', warning: 'triangle-exclamation' }[type] || 'circle-info';
    toast.innerHTML = `<i class="fa-solid fa-${icon}" style="margin-right:8px"></i>${message}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'polite');
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.animation = 'fadeOut .3s ease forwards';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  },

  openModal(id) {
    const overlay = document.getElementById(id);
    if (!overlay) return;
    overlay.classList.add('open');
    overlay.setAttribute('aria-hidden', 'false');
    const focusable = overlay.querySelector('input, select, textarea, button');
    if (focusable) setTimeout(() => focusable.focus(), 100);
    overlay._trapHandler = e => this._trapFocus(e, overlay);
    overlay.addEventListener('keydown', overlay._trapHandler);
    overlay._overlayClickHandler = e => { if (e.target === overlay) this.closeModal(id); };
    overlay.addEventListener('click', overlay._overlayClickHandler);
  },

  closeModal(id) {
    const overlay = document.getElementById(id);
    if (!overlay) return;
    overlay.classList.remove('open');
    overlay.setAttribute('aria-hidden', 'true');
    if (overlay._trapHandler)        overlay.removeEventListener('keydown', overlay._trapHandler);
    if (overlay._overlayClickHandler) overlay.removeEventListener('click', overlay._overlayClickHandler);
  },

  _trapFocus(e, modal) {
    if (e.key !== 'Tab') return;
    const focusable = modal.querySelectorAll(
      'a, button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    if (!focusable.length) return;
    const first = focusable[0], last = focusable[focusable.length - 1];
    if (e.shiftKey) {
      if (document.activeElement === first) { last.focus(); e.preventDefault(); }
    } else {
      if (document.activeElement === last) { first.focus(); e.preventDefault(); }
    }
  },

  setButtonLoading(id, loading) {
    const btn = document.getElementById(id);
    if (!btn) return;
    btn.disabled = loading;
    if (loading) {
      btn.dataset.originalText = btn.innerHTML;
      btn.innerHTML = '<span class="spinner" style="width:16px;height:16px;border-width:2px;display:inline-block"></span>';
    } else {
      btn.innerHTML = btn.dataset.originalText || btn.innerHTML;
    }
  },

  showFormError(id, message) {
    const el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = `<i class="fa-solid fa-circle-xmark" style="margin-right:6px"></i>${message}`;
    el.classList.add('visible');
    el.setAttribute('role', 'alert');
  },

  hideFormError(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = '';
    el.classList.remove('visible');
  },

  toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem(APP_CONFIG.THEME_KEY, isDark ? 'dark' : 'light');
  },

  applyTheme() {
    const saved = localStorage.getItem(APP_CONFIG.THEME_KEY);
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (saved === 'dark' || (!saved && prefersDark)) {
      document.body.classList.add('dark-mode');
    }
  },

  applyNeuroProfile(user) {
    document.body.classList.remove('font-small', 'font-medium', 'font-large');
    if (user.font_size && user.font_size !== 'medium') {
      document.body.classList.add(`font-${user.font_size}`);
    }
    document.body.classList.toggle('high-contrast', !!user.high_contrast);
    document.body.classList.toggle('simplified', !!user.simplified_view);
  },

  escape(str) {
    const div = document.createElement('div');
    div.textContent = str ?? '';
    return div.innerHTML;
  },

  minutesToHM(minutes) {
    const m = parseInt(minutes) || 0;
    const h = Math.floor(m / 60);
    const rem = m % 60;
    if (h && rem) return `${h}h ${rem}m`;
    if (h) return `${h}h`;
    return `${rem}m`;
  },

  initModalCloseButtons() {
    document.querySelectorAll('.modal-close').forEach(btn => {
      btn.addEventListener('click', () => {
        const modal = btn.closest('.modal-overlay');
        if (modal) this.closeModal(modal.id);
      });
    });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.open').forEach(m => this.closeModal(m.id));
      }
    });
  },
};

// ---------------------------------------------------------------------------
// Settings
// ---------------------------------------------------------------------------
const Settings = {
  load() {
    if (!State.user) return;
    const u = State.user;
    const set   = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };
    const check = (id, val) => { const el = document.getElementById(id); if (el) el.checked = !!val; };
    set('settingFullName',   u.full_name  || '');
    set('settingNeuroMode',  u.neuro_mode || 'standard');
    set('settingFontSize',   u.font_size  || 'medium');
    check('settingHighContrast',   u.high_contrast);
    check('settingSimplifiedView', u.simplified_view);
  },
};

document.getElementById('settingsForm')?.addEventListener('submit', async e => {
  e.preventDefault();
  const form = e.target;
  const data = {
    full_name:       form.full_name.value.trim(),
    neuro_mode:      form.neuro_mode.value,
    font_size:       form.font_size.value,
    high_contrast:   form.high_contrast.checked ? 1 : 0,
    simplified_view: form.simplified_view.checked ? 1 : 0,
  };
  UI.setButtonLoading('btnSaveSettings', true);
  await Auth.updateProfile(data);
  UI.setButtonLoading('btnSaveSettings', false);
});

// ---------------------------------------------------------------------------
// Reminders
// ---------------------------------------------------------------------------
const Reminders = {
  async load() {
    const res = await API.get('/reminders');
    if (!res || !res.ok) return;
    this.render(res.data.data.reminders);
  },

  render(reminders) {
    const container = document.getElementById('remindersList');
    if (!container) return;

    if (!reminders.length) {
      container.innerHTML = `
        <div class="empty-state">
          <i class="fa-regular fa-bell" style="font-size:3rem;color:var(--clr-text-muted)"></i>
          <p style="margin-top:var(--space-4)">No reminders at the moment.</p>
        </div>`;
      return;
    }

    const unreadIds = reminders.filter(r => !r.is_read).map(r => r.id);
    if (unreadIds.length) API.post('/reminders/read', { ids: unreadIds });

    container.innerHTML = reminders.map(r => `
      <div class="reminder-item ${r.is_read ? '' : 'unread'}" role="listitem">
        <div class="reminder-icon">
          <i class="fa-solid fa-${r.type === 'overdue' ? 'triangle-exclamation' : 'bell'}"
             style="font-size:1.3rem;color:${r.type === 'overdue' ? 'var(--clr-danger)' : 'var(--clr-warning)'}"
             aria-hidden="true"></i>
        </div>
        <div>
          <div class="reminder-text">${UI.escape(r.message)}</div>
          <div class="reminder-time">
            <i class="fa-regular fa-clock" aria-hidden="true"></i>
            ${new Date(r.created_at).toLocaleString('en-GB')}
          </div>
        </div>
      </div>`).join('');
  },

  async refreshCount() {
    if (!State.token) return;
    const res = await API.get('/reminders/count');
    if (!res || !res.ok) return;
    const count = res.data.data.unread_count;
    State.reminderCount = count;
    document.querySelectorAll('.reminder-badge-count').forEach(el => {
      el.textContent = count;
      el.parentElement.style.display = count > 0 ? '' : 'none';
    });
    const badge = document.getElementById('notifBadge');
    if (badge) badge.style.display = count > 0 ? 'block' : 'none';
  },
};

document.addEventListener('DOMContentLoaded', () => {
  UI.initModalCloseButtons();
  Search.init();
});
