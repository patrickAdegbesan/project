/**
 * auth.js — Registration, login, logout
 */

'use strict';

const Auth = {
  // -------------------------------------------------------------------------
  // Register
  // -------------------------------------------------------------------------
  async register(formData) {
    const res = await API.post('/auth/register', formData);
    if (!res) return;

    if (!res.ok) {
      UI.showFormError('registerError', res.data.error || 'Registration failed.');
      return;
    }

    State.token = res.data.data.token;
    State.user  = res.data.data.user;
    localStorage.setItem(APP_CONFIG.TOKEN_KEY, State.token);
    localStorage.setItem(APP_CONFIG.USER_KEY,  JSON.stringify(State.user));

    UI.applyNeuroProfile(State.user);
    showApp();
    UI.toast('Welcome to Study Planner! 🎓', 'success');
  },

  // -------------------------------------------------------------------------
  // Login
  // -------------------------------------------------------------------------
  async login(email, password) {
    const res = await API.post('/auth/login', { email, password });
    if (!res) return;

    if (!res.ok) {
      UI.showFormError('loginError', res.data.error || 'Login failed.');
      return;
    }

    State.token = res.data.data.token;
    State.user  = res.data.data.user;
    localStorage.setItem(APP_CONFIG.TOKEN_KEY, State.token);
    localStorage.setItem(APP_CONFIG.USER_KEY,  JSON.stringify(State.user));

    UI.applyNeuroProfile(State.user);
    showApp();
    UI.toast(`Welcome back, ${State.user.full_name || State.user.username}!`, 'success');
  },

  // -------------------------------------------------------------------------
  // Logout
  // -------------------------------------------------------------------------
  async logout(silent = false) {
    await API.post('/auth/logout');
    State.token = null;
    State.user  = null;
    localStorage.removeItem(APP_CONFIG.TOKEN_KEY);
    localStorage.removeItem(APP_CONFIG.USER_KEY);
    showAuth();
    if (!silent) UI.toast('Logged out successfully.', 'success');
  },

  // -------------------------------------------------------------------------
  // Update profile
  // -------------------------------------------------------------------------
  async updateProfile(profileData) {
    const res = await API.put('/auth/profile', profileData);
    if (!res || !res.ok) {
      UI.toast(res?.data?.error || 'Failed to update profile.', 'error');
      return false;
    }
    State.user = res.data.data.user;
    localStorage.setItem(APP_CONFIG.USER_KEY, JSON.stringify(State.user));
    UI.applyNeuroProfile(State.user);
    updateUserUI();
    UI.toast('Profile updated.', 'success');
    return true;
  },
};

// ---------------------------------------------------------------------------
// Login form submit
// ---------------------------------------------------------------------------
document.getElementById('loginForm')?.addEventListener('submit', async e => {
  e.preventDefault();
  const email    = document.getElementById('loginEmail').value.trim();
  const password = document.getElementById('loginPassword').value;
  UI.hideFormError('loginError');
  UI.setButtonLoading('btnLogin', true);
  await Auth.login(email, password);
  UI.setButtonLoading('btnLogin', false);
});

// ---------------------------------------------------------------------------
// Register form submit
// ---------------------------------------------------------------------------
document.getElementById('registerForm')?.addEventListener('submit', async e => {
  e.preventDefault();
  const username  = document.getElementById('regUsername').value.trim();
  const email     = document.getElementById('regEmail').value.trim();
  const password  = document.getElementById('regPassword').value;
  const full_name = document.getElementById('regFullName').value.trim();
  const confirm   = document.getElementById('regConfirm').value;

  UI.hideFormError('registerError');

  if (password !== confirm) {
    UI.showFormError('registerError', 'Passwords do not match.');
    return;
  }

  UI.setButtonLoading('btnRegister', true);
  await Auth.register({ username, email, password, full_name });
  UI.setButtonLoading('btnRegister', false);
});

// ---------------------------------------------------------------------------
// Switch between login / register tabs
// ---------------------------------------------------------------------------
document.getElementById('showRegister')?.addEventListener('click', e => {
  e.preventDefault();
  document.getElementById('loginPane').classList.add('hidden');
  document.getElementById('registerPane').classList.remove('hidden');
});

document.getElementById('showLogin')?.addEventListener('click', e => {
  e.preventDefault();
  document.getElementById('registerPane').classList.add('hidden');
  document.getElementById('loginPane').classList.remove('hidden');
});

// Logout button
document.getElementById('btnLogout')?.addEventListener('click', () => Auth.logout());
