/* ComplaintDesk — shared interactive behaviours */

/* ── Sidebar toggle (mobile) ── */
function toggleSidebar() {
  const sb = document.getElementById('sidebar');
  const ov = document.getElementById('sidebarOverlay');
  if (!sb) return;
  sb.classList.toggle('open');
  ov && ov.classList.toggle('show');
}
document.addEventListener('DOMContentLoaded', () => {
  const ov = document.getElementById('sidebarOverlay');
  if (ov) ov.addEventListener('click', toggleSidebar);

  /* Modal helpers */
  document.querySelectorAll('[data-modal-open]').forEach(btn => {
    btn.addEventListener('click', () => {
      const m = document.getElementById(btn.dataset.modalOpen);
      if (m) m.style.display = 'flex';
    });
  });
  document.querySelectorAll('[data-modal-close]').forEach(btn => {
    btn.addEventListener('click', () => {
      const m = btn.closest('.modal-backdrop');
      if (m) m.style.display = 'none';
    });
  });
  document.querySelectorAll('.modal-backdrop').forEach(bd => {
    bd.addEventListener('click', e => {
      if (e.target === bd) bd.style.display = 'none';
    });
  });

  /* Role card selection */
  document.querySelectorAll('.role-card').forEach(card => {
    card.addEventListener('click', () => {
      card.closest('.role-grid').querySelectorAll('.role-card').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
    });
  });

  /* Priority radio label */
  document.querySelectorAll('.priority-radio input').forEach(inp => {
    inp.addEventListener('change', () => {
      document.querySelectorAll('.priority-radio input').forEach(i => i.parentElement.querySelector('.priority-label').style.fontWeight = '');
    });
  });

  /* Tab switching */
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const parent = btn.closest('.tab-container') || document;
      parent.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const target = btn.dataset.tab;
      if (target) {
        parent.querySelectorAll('.tab-pane').forEach(p => p.style.display = 'none');
        const pane = parent.querySelector(`#${target}`);
        if (pane) pane.style.display = 'block';
      }
    });
  });

  /* Dark mode toggle */
  const dmBtn = document.getElementById('darkModeToggle');
  if (dmBtn) {
    dmBtn.addEventListener('click', () => {
      document.documentElement.toggleAttribute('data-theme');
      const isDark = document.documentElement.hasAttribute('data-theme');
      document.documentElement.dataset.theme = isDark ? '' : 'dark';
      if (document.documentElement.dataset.theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
      } else {
        document.documentElement.removeAttribute('data-theme');
      }
    });
  }

  /* Animate stat numbers on load */
  document.querySelectorAll('.stat-number[data-target]').forEach(el => {
    const target = parseInt(el.dataset.target);
    let current = 0;
    const step = Math.ceil(target / 30);
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = current.toLocaleString();
      if (current >= target) clearInterval(timer);
    }, 30);
  });
});
