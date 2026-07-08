/**
 * ComplaintDesk — API client
 * All pages import this for fetch() calls to the Flask backend.
 */

const API = {
  base: '',   // same origin — Flask serves both the HTML and the API

  async request(method, path, body) {
    const opts = {
      method,
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    };
    if (body !== undefined) opts.body = JSON.stringify(body);
    const res  = await fetch(this.base + path, opts);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw Object.assign(new Error(data.error || 'Request failed'), { status: res.status, data });
    return data;
  },

  get:    (path)        => API.request('GET',    path),
  post:   (path, body)  => API.request('POST',   path, body),
  put:    (path, body)  => API.request('PUT',    path, body),
  delete: (path)        => API.request('DELETE', path),

  // Auth
  login:          (email, password, role) => API.post('/api/auth/login', { email, password, role }),
  logout:         ()                      => API.post('/api/auth/logout'),
  register:       (d)                     => API.post('/api/auth/register', d),
  me:             ()                      => API.get('/api/auth/me'),
  changePassword: (d)                     => API.post('/api/auth/change-password', d),
  updateProfile:  (d)                     => API.post('/api/auth/update-profile', d),

  // Complaints
  myComplaints:   (params = {})       => API.get('/api/complaints?' + new URLSearchParams(params)),
  submitComplaint:(d)                 => API.post('/api/complaints', d),
  getComplaint:   (id)                => API.get(`/api/complaints/${id}`),
  addResponse:    (id, message, internal=false) => API.post(`/api/complaints/${id}/respond`, { message, internal }),
  userStats:      ()                  => API.get('/api/user/stats'),

  // Admin — complaints
  adminComplaints:(params = {})       => API.get('/api/admin/complaints?' + new URLSearchParams(params)),
  adminUpdateComplaint: (id, d)       => API.put(`/api/admin/complaints/${id}`, d),

  // Admin — stats
  adminStats:     ()                  => API.get('/api/admin/stats'),
  adminReports:   (period = 30)       => API.get(`/api/admin/reports?period=${period}`),

  // Admin — users
  adminUsers:     (params = {})       => API.get('/api/admin/users?' + new URLSearchParams(params)),
  adminGetUser:   (id)                => API.get(`/api/admin/users/${id}`),
  adminUpdateUser:(id, d)             => API.put(`/api/admin/users/${id}`, d),
  adminCreateUser:(d)                 => API.post('/api/admin/users', d),

  // Announcements
  announcements:  ()                  => API.get('/api/announcements'),
  adminAnnouncements: ()              => API.get('/api/admin/announcements'),
  adminCreateAnn: (d)                 => API.post('/api/admin/announcements', d),
  adminUpdateAnn: (id, d)             => API.put(`/api/admin/announcements/${id}`, d),
  adminDeleteAnn: (id)                => API.delete(`/api/admin/announcements/${id}`),

  // Categories
  categories:     ()                  => API.get('/api/categories'),

  // Settings
  getSettings:    ()                  => API.get('/api/admin/settings'),
  saveSettings:   (d)                 => API.post('/api/admin/settings', d),
};

/** Guard: redirect to login if session expired (401) */
async function requireAuth(expectedRole) {
  try {
    const user = await API.me();
    if (expectedRole && user.role !== expectedRole) {
      window.location.href = '01-login.html';
    }
    return user;
  } catch (e) {
    if (e.status === 401) window.location.href = '01-login.html';
    throw e;
  }
}

/** Render a status badge */
function statusBadge(status) {
  const map = {
    open:        ['badge-open',        'Open'],
    in_progress: ['badge-in-progress', 'In Progress'],
    resolved:    ['badge-resolved',    'Resolved'],
    closed:      ['badge-resolved',    'Closed'],
    rejected:    ['badge-rejected',    'Rejected'],
  };
  const [cls, label] = map[status] || ['badge-open', status];
  return `<span class="complaint-badge ${cls}">${label}</span>`;
}

/** Render a priority badge */
function priorityBadge(p) {
  const map = {
    low:    ['badge-low',    'Low'],
    medium: ['badge-medium', 'Medium'],
    high:   ['badge-high',   'High'],
    urgent: ['badge-urgent', 'Urgent'],
  };
  const [cls, label] = map[p] || ['badge-medium', p];
  return `<span class="priority-badge ${cls}">${label}</span>`;
}

/** Format a date string */
function fmtDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-GB', { day:'2-digit', month:'short', year:'numeric' });
}

function fmtDateTime(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('en-GB', { day:'2-digit', month:'short', year:'numeric', hour:'2-digit', minute:'2-digit' });
}

/** Wire all Sign Out links on the page to call the logout API */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('a[href="01-login.html"]').forEach(link => {
    const text = link.textContent.trim();
    if (text.toLowerCase().includes('sign out') || text.toLowerCase().includes('log out')) {
      link.addEventListener('click', async (e) => {
        e.preventDefault();
        try { await API.logout(); } catch(_) {}
        window.location.href = '01-login.html';
      });
    }
  });
});

/** Show a toast notification */
function showToast(message, type = 'success') {
  let t = document.getElementById('_globalToast');
  if (!t) {
    t = document.createElement('div');
    t.id = '_globalToast';
    t.style.cssText = 'position:fixed;bottom:24px;right:24px;padding:14px 20px;border-radius:10px;font-size:14px;font-weight:600;z-index:9999;box-shadow:0 4px 20px rgba(0,0,0,0.2);transition:opacity .3s;display:none;';
    document.body.appendChild(t);
  }
  t.textContent = message;
  t.style.background = type === 'error' ? '#dc2626' : '#34a853';
  t.style.color = '#fff';
  t.style.display = 'block';
  t.style.opacity = '1';
  clearTimeout(t._timer);
  t._timer = setTimeout(() => { t.style.opacity = '0'; setTimeout(() => t.style.display='none', 300); }, 3000);
}
