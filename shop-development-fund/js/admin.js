// Rehoboth-Winners Shopping Mall — admin page logic (no dependencies)
//
// Storage model (all in this browser's localStorage):
//   rwm-admin-state   — slots + stages being edited
//   rwm-payments      — the payment register (never published)
//   rwm-preview-data  — copy of the public data used by index.html preview

(function () {
  'use strict';

  var STATE_KEY = 'rwm-admin-state';
  var PAYMENTS_KEY = 'rwm-payments';
  var PREVIEW_KEY = 'rwm-preview-data';
  var NAIRA = '₦';

  function clone(obj) { return JSON.parse(JSON.stringify(obj)); }

  function seedState() {
    if (window.SITE_DATA) return clone(window.SITE_DATA);
    return { updatedAt: '', slots: [], stages: [] };
  }

  function loadState() {
    try {
      var raw = localStorage.getItem(STATE_KEY);
      if (raw) return JSON.parse(raw);
    } catch (e) { /* fall through */ }
    return seedState();
  }

  function loadPayments() {
    try {
      var raw = localStorage.getItem(PAYMENTS_KEY);
      if (raw) return JSON.parse(raw);
    } catch (e) { /* fall through */ }
    return [];
  }

  var state = loadState();
  var payments = loadPayments();

  function persist() {
    localStorage.setItem(STATE_KEY, JSON.stringify(state));
    localStorage.setItem(PAYMENTS_KEY, JSON.stringify(payments));
  }

  function fmtAmount(n) {
    var num = Number(n) || 0;
    return NAIRA + num.toLocaleString('en-NG');
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /* ---------------- Slots ---------------- */
  var CYCLE = { available: 'reserved', reserved: 'sold', sold: 'available' };
  var slotGrid = document.getElementById('adminSlotGrid');

  function renderSlots() {
    slotGrid.innerHTML = '';
    state.slots.forEach(function (slot) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'slot-card ' + slot.status;
      btn.innerHTML =
        '<span class="slot-name">Slot ' + slot.id + '</span>' +
        '<span class="shop-pair"><i>Shop up</i><i>Shop down</i></span>' +
        '<span class="slot-status">' + slot.status.charAt(0).toUpperCase() + slot.status.slice(1) + '</span>';
      btn.addEventListener('click', function () {
        slot.status = CYCLE[slot.status] || 'available';
        renderSlots();
        renderSlotSelect();
      });
      slotGrid.appendChild(btn);
    });
  }

  var slotSelect = document.getElementById('slotSelect');
  function renderSlotSelect() {
    var current = slotSelect.value;
    slotSelect.innerHTML = '<option value="">— none —</option>';
    state.slots.forEach(function (slot) {
      var opt = document.createElement('option');
      opt.value = slot.id;
      opt.textContent = 'Slot ' + slot.id + ' (' + slot.status + ')';
      slotSelect.appendChild(opt);
    });
    slotSelect.value = current;
  }

  /* ---------------- Payments ---------------- */
  var paymentForm = document.getElementById('paymentForm');
  var paymentsBody = document.querySelector('#paymentsTable tbody');
  var paymentsTotal = document.getElementById('paymentsTotal');

  function renderPayments() {
    paymentsBody.innerHTML = '';
    var total = 0;
    payments.forEach(function (p, i) {
      total += Number(p.amount) || 0;
      var tr = document.createElement('tr');
      tr.innerHTML =
        '<td>' + esc(p.date) + '</td>' +
        '<td>' + esc(p.name) + '</td>' +
        '<td>' + esc(p.email) + '</td>' +
        '<td>' + esc(p.phone) + '</td>' +
        '<td>' + fmtAmount(p.amount) + '</td>' +
        '<td>' + esc(p.ref) + '</td>' +
        '<td>' + (p.slot ? 'Slot ' + esc(p.slot) : '—') + '</td>' +
        '<td>' + esc(p.note) + '</td>' +
        '<td><button type="button" class="row-delete" data-i="' + i + '" aria-label="Delete record">&times;</button></td>';
      paymentsBody.appendChild(tr);
    });
    paymentsTotal.textContent = fmtAmount(total);
  }

  paymentsBody.addEventListener('click', function (e) {
    var btn = e.target.closest('.row-delete');
    if (!btn) return;
    var i = Number(btn.dataset.i);
    if (confirm('Delete this payment record? This cannot be undone.')) {
      payments.splice(i, 1);
      persist();
      renderPayments();
    }
  });

  paymentForm.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!paymentForm.reportValidity()) return;
    var f = paymentForm;
    var record = {
      date: f.date.value,
      name: f.name.value.trim(),
      email: f.email.value.trim(),
      phone: f.phone.value.trim(),
      amount: f.amount.value,
      ref: f.ref.value.trim(),
      slot: f.slot.value,
      note: f.note.value.trim()
    };
    payments.push(record);

    if (f.markSold.checked && record.slot) {
      var slot = state.slots.find(function (s) { return String(s.id) === String(record.slot); });
      if (slot) slot.status = 'sold';
    }

    persist();
    renderPayments();
    renderSlots();
    renderSlotSelect();
    f.reset();
  });

  /* ---------------- Stages ---------------- */
  var stageEditors = document.getElementById('stageEditors');

  function renderStages() {
    stageEditors.innerHTML = '';
    state.stages.forEach(function (s) {
      var card = document.createElement('div');
      card.className = 'stage-editor';
      card.innerHTML =
        '<h3>Stage ' + s.id + ' — ' + esc(s.title) + '</h3>' +
        '<div class="se-row">' +
          '<label>Status ' +
            '<select data-field="status">' +
              '<option value="upcoming">Upcoming</option>' +
              '<option value="in-progress">In progress</option>' +
              '<option value="completed">Completed</option>' +
            '</select>' +
          '</label>' +
          '<label>Progress <output>' + (s.progress || 0) + '%</output>' +
            '<input type="range" min="0" max="100" step="5" data-field="progress" value="' + (s.progress || 0) + '">' +
          '</label>' +
        '</div>' +
        '<label class="se-note">Public note (optional)' +
          '<input type="text" data-field="note" value="' + esc(s.note) + '" placeholder="e.g. Survey completed, deed in processing">' +
        '</label>';

      card.querySelector('[data-field="status"]').value = s.status;

      card.addEventListener('input', function (e) {
        var field = e.target.dataset.field;
        if (!field) return;
        if (field === 'progress') {
          s.progress = Number(e.target.value);
          card.querySelector('output').textContent = s.progress + '%';
          if (s.progress >= 100 && s.status !== 'completed') {
            s.status = 'completed';
            card.querySelector('[data-field="status"]').value = 'completed';
          }
        } else if (field === 'status') {
          s.status = e.target.value;
          if (s.status === 'completed') {
            s.progress = 100;
            card.querySelector('[data-field="progress"]').value = 100;
            card.querySelector('output').textContent = '100%';
          }
        } else {
          s[field] = e.target.value;
        }
      });

      stageEditors.appendChild(card);
    });
  }

  /* ---------------- Publish actions ---------------- */
  function publicData() {
    return {
      updatedAt: new Date().toISOString().slice(0, 10),
      slots: state.slots.map(function (s) { return { id: s.id, status: s.status }; }),
      stages: state.stages.map(function (s) {
        return {
          id: s.id, title: s.title, status: s.status,
          progress: Number(s.progress) || 0, note: s.note || '',
          items: s.items || []
        };
      })
    };
  }

  function download(filename, text, mime) {
    var blob = new Blob([text], { type: mime || 'text/plain;charset=utf-8' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(a.href);
  }

  var saveStatus = document.getElementById('saveStatus');
  function flash(msg) {
    saveStatus.textContent = msg;
    setTimeout(function () { saveStatus.textContent = ''; }, 5000);
  }

  document.getElementById('btnSave').addEventListener('click', function () {
    persist();
    localStorage.setItem(PREVIEW_KEY, JSON.stringify(publicData()));
    flash('Saved. Open the public site in this browser to preview — remember it is not published until you upload site-data.js.');
  });

  document.getElementById('btnDownload').addEventListener('click', function () {
    persist();
    var header =
      '/* Rehoboth-Winners Shopping Mall — published site data.\n' +
      '   Generated by admin.html on ' + new Date().toISOString() + '.\n' +
      '   Contains no personal data — slot statuses and stage progress only. */\n\n';
    download('site-data.js',
      header + 'window.SITE_DATA = ' + JSON.stringify(publicData(), null, 2) + ';\n',
      'text/javascript;charset=utf-8');
    flash('site-data.js downloaded. Upload it to the website\'s data/ folder to publish.');
  });

  document.getElementById('btnCsv').addEventListener('click', function () {
    var rows = [['Date', 'Name', 'Email', 'Phone', 'Amount (NGN)', 'Paystack Reference', 'Slot', 'Note']];
    payments.forEach(function (p) {
      rows.push([p.date, p.name, p.email, p.phone, p.amount, p.ref, p.slot, p.note]);
    });
    var csv = rows.map(function (row) {
      return row.map(function (cell) {
        var v = String(cell == null ? '' : cell);
        return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v;
      }).join(',');
    }).join('\r\n');
    download('rwm-payments-' + new Date().toISOString().slice(0, 10) + '.csv', csv, 'text/csv;charset=utf-8');
  });

  document.getElementById('btnReset').addEventListener('click', function () {
    if (!confirm('Discard local slot/stage changes and reload from the published site-data.js? Payment records are kept.')) return;
    localStorage.removeItem(STATE_KEY);
    localStorage.removeItem(PREVIEW_KEY);
    state = seedState();
    renderSlots();
    renderSlotSelect();
    renderStages();
    flash('Local changes discarded — showing the published data.');
  });

  /* ---------------- Init ---------------- */
  renderSlots();
  renderSlotSelect();
  renderStages();
  renderPayments();
})();
