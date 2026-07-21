// Rehoboth-Winners Shopping Mall — public site behaviour (no dependencies)

(function () {
  'use strict';

  var PAY_URL = 'https://paystack.shop/pay/shop-development-fund';

  /* ------------------------------------------------------------------
     Site data: the published data/site-data.js file drives slot
     availability and stage progress. If the admin page has saved a
     preview in this browser, the preview takes precedence so the team
     can check changes before publishing.
     ------------------------------------------------------------------ */
  var DATA = (function () {
    try {
      var preview = localStorage.getItem('rwm-preview-data');
      if (preview) return JSON.parse(preview);
    } catch (e) { /* ignore corrupt preview */ }
    return window.SITE_DATA || null;
  })();

  /* ---------------- Mobile navigation ---------------- */
  var navToggle = document.getElementById('navToggle');
  var siteNav = document.getElementById('siteNav');
  if (navToggle && siteNav) {
    navToggle.addEventListener('click', function () {
      var open = siteNav.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', String(open));
    });
    siteNav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        siteNav.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* ---------------- Enquiry form (mailto) ---------------- */
  var form = document.getElementById('enquiryForm');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var name = form.name.value.trim();
      var email = form.email.value.trim();
      var message = form.message.value.trim();
      var subject = encodeURIComponent('Rehoboth-Winners Mall — Enquiry from ' + name);
      var body = encodeURIComponent('Name: ' + name + '\nEmail: ' + email + '\n\n' + message);
      window.location.href = 'mailto:sale@301atech.com?subject=' + subject + '&body=' + body;
    });
  }

  /* ---------------- Footer year ---------------- */
  var yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  /* ---------------- Fly-through video overlay ---------------- */
  var vid = document.getElementById('mallVideo');
  var playBtn = document.getElementById('videoPlay');
  if (vid && playBtn) {
    playBtn.addEventListener('click', function () { vid.play(); });
    vid.addEventListener('play', function () { playBtn.classList.add('hidden'); });
    vid.addEventListener('pause', function () {
      if (!vid.ended) playBtn.classList.remove('hidden');
    });
  }

  /* ---------------- Render gallery: show only images that exist ----------------
     Each image whose file is missing removes its tile; if none of the render
     photos have been added yet, the whole gallery hides itself so nothing
     appears broken. Add the photos to /assets to make it appear. */
  var gallery = document.getElementById('renderGallery');
  if (gallery) {
    var imgs = Array.prototype.slice.call(gallery.querySelectorAll('img'));
    var pending = imgs.length;
    var settle = function () {
      if (--pending === 0 && gallery.querySelectorAll('li').length === 0) {
        gallery.remove();
      }
    };
    imgs.forEach(function (img) {
      var done = false;
      var ok = function () { if (!done) { done = true; settle(); } };
      var fail = function () {
        if (done) return;
        done = true;
        var li = img.closest('li');
        if (li) li.remove();
        settle();
      };
      if (img.complete) { img.naturalWidth > 0 ? ok() : fail(); }
      else { img.addEventListener('load', ok); img.addEventListener('error', fail); }
    });
  }

  if (!DATA) return; // static fallback content stays as written in the HTML

  /* ---------------- Slot availability ---------------- */
  var slots = DATA.slots || [];
  var total = slots.length || 8;
  var available = slots.filter(function (s) { return s.status === 'available'; }).length;

  var notice = document.getElementById('slotsNotice');
  if (notice) {
    if (available === 0) {
      notice.textContent = 'All slots sold';
    } else if (available < total) {
      notice.textContent = 'Only ' + available + (available === 1 ? ' slot' : ' slots') + ' remaining';
    } else {
      notice.textContent = 'Now selling — ' + total + ' slots available';
    }
  }

  var summaryCell = document.getElementById('slotsSummary');
  if (summaryCell) summaryCell.textContent = available + ' of ' + total;
  var tableCell = document.getElementById('slotsTableCell');
  if (tableCell) tableCell.textContent = available + ' of ' + total;

  var grid = document.getElementById('slotGrid');
  if (grid) {
    grid.innerHTML = '';
    slots.forEach(function (slot) {
      var isAvailable = slot.status === 'available';
      var el = document.createElement(isAvailable ? 'a' : 'div');
      el.className = 'slot-card ' + slot.status;
      if (isAvailable) {
        el.href = PAY_URL;
        el.target = '_blank';
        el.rel = 'noopener';
        el.setAttribute('aria-label', 'Slot ' + slot.id + ' available — open payment page');
      }
      el.innerHTML =
        '<span class="slot-name">Slot ' + slot.id + '</span>' +
        '<span class="shop-pair"><i>Shop up</i><i>Shop down</i></span>' +
        '<span class="slot-status">' +
          (isAvailable ? 'Available' : slot.status === 'reserved' ? 'Reserved' : 'Sold') +
        '</span>';
      grid.appendChild(el);
    });
  }

  /* ---------------- Project roadmap ---------------- */
  var stages = DATA.stages || [];
  var NODE_POS = [
    { x: '5%', y: '62%' },
    { x: '29%', y: '25%' },
    { x: '53%', y: '62%' },
    { x: '77%', y: '25%' }
  ];
  var END_POS = { x: '94.5%', y: '58%' };

  var currentIndex = (function () {
    for (var i = 0; i < stages.length; i++) {
      if (stages[i].status === 'in-progress') return i;
    }
    for (var j = stages.length - 1; j >= 0; j--) {
      if (stages[j].status === 'completed') return j;
    }
    return 0;
  })();

  var nodesEl = document.getElementById('mapNodes');
  var detailEl = document.getElementById('stageDetail');

  function statusLabel(status) {
    return status === 'completed' ? 'Completed'
      : status === 'in-progress' ? 'In progress'
      : 'Upcoming';
  }

  function renderDetail(i) {
    if (!detailEl || !stages[i]) return;
    var s = stages[i];
    var pct = Math.max(0, Math.min(100, Number(s.progress) || 0));
    if (s.status === 'completed') pct = 100;

    var html =
      '<div class="detail-head">' +
        '<h3>Stage ' + s.id + ' — ' + s.title + '</h3>' +
        '<span class="badge badge-' + s.status + '">' + statusLabel(s.status) + '</span>' +
      '</div>' +
      '<div class="bar" role="progressbar" aria-valuenow="' + pct + '" aria-valuemin="0" aria-valuemax="100">' +
        '<div class="bar-fill" style="width:' + pct + '%"></div>' +
      '</div>' +
      '<p class="bar-pct">' + pct + '% complete</p>';

    if (s.items && s.items.length) {
      html += '<ul class="detail-items">';
      s.items.forEach(function (item) { html += '<li>' + item + '</li>'; });
      html += '</ul>';
    }
    if (s.note) html += '<p class="detail-note">' + s.note + '</p>';

    detailEl.innerHTML = html;

    if (nodesEl) {
      var buttons = nodesEl.querySelectorAll('.map-node');
      buttons.forEach(function (btn, k) {
        btn.classList.toggle('selected', k === i);
        btn.setAttribute('aria-pressed', String(k === i));
      });
    }
  }

  if (nodesEl && stages.length) {
    nodesEl.innerHTML = '';
    stages.forEach(function (s, i) {
      var li = document.createElement('li');
      li.style.left = NODE_POS[i].x;
      li.style.top = NODE_POS[i].y;

      var cls = s.status === 'completed' ? 'done'
        : s.status === 'in-progress' ? 'current'
        : 'todo';

      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'map-node ' + cls;
      btn.innerHTML = s.status === 'completed'
        ? '<span class="node-check">&#10003;</span>'
        : '<span class="node-num">0' + s.id + '</span>';
      btn.setAttribute('aria-label', 'Stage ' + s.id + ' — ' + s.title + ' (' + statusLabel(s.status) + ')');
      btn.addEventListener('click', function () { renderDetail(i); });

      var label = document.createElement('span');
      label.className = 'node-label';
      label.innerHTML = s.title + '<em>' + statusLabel(s.status) + '</em>';

      li.appendChild(btn);
      li.appendChild(label);
      nodesEl.appendChild(li);
    });

    var end = document.createElement('li');
    end.className = 'map-end';
    end.style.left = END_POS.x;
    end.style.top = END_POS.y;
    end.innerHTML = '<span class="map-x" aria-hidden="true">&#10761;</span>' +
      '<span class="node-label">Mall opens<em>The goal</em></span>';
    nodesEl.appendChild(end);

    renderDetail(currentIndex);
  }

  var updated = document.getElementById('mapUpdated');
  if (updated && DATA.updatedAt) {
    updated.textContent = 'Progress last updated ' + DATA.updatedAt;
  }

  var stageSummary = document.getElementById('stageSummary');
  if (stageSummary && stages[currentIndex]) {
    var cs = stages[currentIndex];
    stageSummary.textContent = 'Stage ' + cs.id + ' — ' + cs.title +
      (cs.status === 'completed' ? ' (completed)' : '');
  }
})();
