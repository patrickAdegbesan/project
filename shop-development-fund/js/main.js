// Shop Development Fund — small interactive helpers (no dependencies)

// Mobile navigation toggle
const navToggle = document.getElementById('navToggle');
const siteNav = document.getElementById('siteNav');

navToggle.addEventListener('click', () => {
  const open = siteNav.classList.toggle('open');
  navToggle.setAttribute('aria-expanded', String(open));
});

siteNav.addEventListener('click', (e) => {
  if (e.target.tagName === 'A') {
    siteNav.classList.remove('open');
    navToggle.setAttribute('aria-expanded', 'false');
  }
});

// Enquiry form — opens the visitor's email client with the message pre-filled
document.getElementById('enquiryForm').addEventListener('submit', (e) => {
  e.preventDefault();
  const form = e.target;
  if (!form.reportValidity()) return;

  const name = form.name.value.trim();
  const email = form.email.value.trim();
  const message = form.message.value.trim();

  const subject = encodeURIComponent('Shop Development Fund — Enquiry from ' + name);
  const body = encodeURIComponent(
    'Name: ' + name + '\nEmail: ' + email + '\n\n' + message
  );
  window.location.href = 'mailto:sale@301atech.com?subject=' + subject + '&body=' + body;
});

// Keep the footer year current
document.getElementById('year').textContent = new Date().getFullYear();
