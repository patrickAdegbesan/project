/**
 * app.js — Application bootstrap and global state
 * Student Study Planner | Nwachukwu Chibuzor Benjamin | 22/9799
 */

'use strict';

// ---------------------------------------------------------------------------
// Global configuration
// ---------------------------------------------------------------------------
const APP_CONFIG = {
  API_BASE: 'http://127.0.0.1:5000/api',
  TOKEN_KEY: 'study_planner_token',
  USER_KEY:  'study_planner_user',
  THEME_KEY: 'study_planner_theme',
};

// ---------------------------------------------------------------------------
// Global state object (single source of truth)
// ---------------------------------------------------------------------------
const State = {
  user:  null,
  token: null,
  currentPage: 'dashboard',
  reminderCount: 0,
};

// ---------------------------------------------------------------------------
// API helper
// ---------------------------------------------------------------------------
const API = {
  async request(method, endpoint, body = null) {
    const headers = { 'Content-Type': 'application/json' };
    if (State.token) headers['X-Auth-Token'] = State.token;

    const opts = { method, headers };
    if (body) opts.body = JSON.stringify(body);

    try {
      const res = await fetch(`${APP_CONFIG.API_BASE}${endpoint}`, opts);
      const data = await res.json();

      if (res.status === 401) {
        // Session expired — log out
        Auth.logout(true);
        return null;
      }

      return { ok: res.ok, status: res.status, data };
    } catch (err) {
      console.error(`API ${method} ${endpoint} failed:`, err);
      UI.toast('Network error. Please check your connection.', 'error');
      return null;
    }
  },

  get:    (ep)       => API.request('GET',    ep),
  post:   (ep, body) => API.request('POST',   ep, body),
  put:    (ep, body) => API.request('PUT',    ep, body),
  delete: (ep)       => API.request('DELETE', ep),
};

// ---------------------------------------------------------------------------
// Router — simple hash-based page switcher
// ---------------------------------------------------------------------------
const Router = {
  pages: ['dashboard', 'tasks', 'schedule', 'progress', 'analytics', 'adaptive', 'settings', 'reminders', 'admin'],

  navigate(page) {
    if (!this.pages.includes(page)) page = 'dashboard';
    State.currentPage = page;

    // Show/hide pages
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    const el = document.getElementById(`page-${page}`);
    if (el) el.classList.add('active');

    // Update sidebar active link
    document.querySelectorAll('.sidebar-nav a').forEach(a => {
      a.classList.toggle('active', a.dataset.page === page);
    });

    // Update topbar title
    const titles = {
      dashboard:  'Dashboard',
      tasks:      'My Tasks',
      schedule:   'Study Schedule',
      progress:   'Progress Tracker',
      analytics:  'Analytics',
      adaptive:   'Adaptive Recommendations',
      settings:   'Settings',
      reminders:  'Reminders',
      admin:      'Admin Panel',
    };
    const titleEl = document.getElementById('pageTitle');
    if (titleEl) titleEl.textContent = titles[page] || page;

    window.location.hash = page;

    // Trigger page-specific data load
    this._onNavigate(page);
  },

  _onNavigate(page) {
    switch (page) {
      case 'dashboard':  Dashboard.load(); break;
      case 'tasks':      Tasks.load();     break;
      case 'schedule':   Schedule.load();  break;
      case 'progress':   Progress.load();  break;
      case 'analytics':  Analytics.load(); break;
      case 'adaptive':   Adaptive.load();  break;
      case 'reminders':  Reminders.load(); break;
      case 'admin':      Admin.load();     break;
    }
  },

  init() {
    const hash = window.location.hash.replace('#', '');
    this.navigate(this.pages.includes(hash) ? hash : 'dashboard');
  },
};

// ---------------------------------------------------------------------------
// App init
// ---------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  // Restore session
  State.token = localStorage.getItem(APP_CONFIG.TOKEN_KEY);
  try {
    State.user = JSON.parse(localStorage.getItem(APP_CONFIG.USER_KEY));
  } catch { State.user = null; }

  // Apply persisted theme & neuro profile
  UI.applyTheme();
  if (State.user) UI.applyNeuroProfile(State.user);

  if (State.token && State.user) {
    showApp();
  } else {
    showAuth();
  }

  // Sidebar nav click
  document.querySelectorAll('.sidebar-nav a[data-page]').forEach(a => {
    a.addEventListener('click', e => {
      e.preventDefault();
      Router.navigate(a.dataset.page);
      // Close sidebar on mobile
      document.getElementById('sidebar').classList.remove('open');
      document.getElementById('sidebarOverlay')?.classList.remove('visible');
    });
  });

  // Mobile hamburger
  document.getElementById('btnMenu')?.addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('open');
    document.getElementById('sidebarOverlay')?.classList.toggle('visible');
  });

  // Sidebar overlay click
  document.getElementById('sidebarOverlay')?.addEventListener('click', () => {
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('sidebarOverlay').classList.remove('visible');
  });

  // Dark mode toggle
  document.getElementById('darkModeToggle')?.addEventListener('click', UI.toggleDarkMode);

  // Poll reminder count every 60 s
  setInterval(Reminders.refreshCount, 60_000);
});

function showApp() {
  document.getElementById('authWrapper').style.display = 'none';
  document.getElementById('appShell').style.display   = 'flex';
  updateUserUI();
  Router.init();
  Reminders.refreshCount();
}

function showAuth() {
  document.getElementById('authWrapper').style.display = 'flex';
  document.getElementById('appShell').style.display    = 'none';
}

function updateUserUI() {
  if (!State.user) return;
  const name = State.user.full_name || State.user.username;
  const initials = name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
  document.querySelectorAll('.user-avatar').forEach(el => el.textContent = initials);
  document.querySelectorAll('.user-display-name').forEach(el => el.textContent = name);
  document.querySelectorAll('.user-username').forEach(el => el.textContent = `@${State.user.username}`);

  // Show admin nav link only for admin users
  const adminLink = document.getElementById('adminNavLink');
  if (adminLink) {
    adminLink.style.display = State.user.is_admin ? '' : 'none';
  }
}
