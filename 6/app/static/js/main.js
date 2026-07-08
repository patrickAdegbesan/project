/* Lush Hair NG — Global JS utilities */

// ── Sidebar toggle (mobile) ──────────────────────────────────────
const sidebarToggle = document.getElementById('sidebarToggle');
if (sidebarToggle) {
  sidebarToggle.addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('open');
  });
}

// Close sidebar when clicking outside on mobile
document.addEventListener('click', e => {
  const sidebar = document.getElementById('sidebar');
  const toggle = document.getElementById('sidebarToggle');
  if (sidebar && window.innerWidth < 992) {
    if (!sidebar.contains(e.target) && e.target !== toggle) {
      sidebar.classList.remove('open');
    }
  }
});

// ── Toast notifications ──────────────────────────────────────────
function showToast(message, type = 'info') {
  const colorMap = {
    success: 'bg-success text-white',
    danger:  'bg-danger text-white',
    warning: 'bg-warning text-dark',
    info:    'bg-info text-dark',
  };
  const iconMap = {
    success: 'bi-check-circle-fill',
    danger:  'bi-x-circle-fill',
    warning: 'bi-exclamation-triangle-fill',
    info:    'bi-info-circle-fill',
  };

  const container = document.getElementById('toastContainer');
  if (!container) return;

  const id = 'toast_' + Date.now();
  const html = `
    <div id="${id}" class="toast align-items-center ${colorMap[type] || ''} border-0" role="alert">
      <div class="d-flex">
        <div class="toast-body d-flex align-items-center gap-2">
          <i class="bi ${iconMap[type] || 'bi-info-circle'}"></i>
          ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    </div>`;
  container.insertAdjacentHTML('beforeend', html);
  const el = document.getElementById(id);
  const toast = new bootstrap.Toast(el, { delay: 4000 });
  toast.show();
  el.addEventListener('hidden.bs.toast', () => el.remove());
}

// ── Format number helpers ────────────────────────────────────────
function fmtPct(v) { return (v ?? 0).toFixed(1) + '%'; }
function fmtKm(v)  { return v != null ? v.toFixed(1) + ' km' : '—'; }

// ── Active nav link highlight ────────────────────────────────────
document.querySelectorAll('.nav-item').forEach(link => {
  if (link.href && window.location.pathname.startsWith(new URL(link.href).pathname) &&
      new URL(link.href).pathname !== '/') {
    link.classList.add('active');
  } else if (new URL(link.href).pathname === '/' && window.location.pathname === '/') {
    link.classList.add('active');
  }
});
