/* ============================================================
   SRMS – Main JavaScript
   jQuery 3.7 + vanilla JS
   ============================================================ */

'use strict';

/* ---- Dark mode ---- */
(function initDarkMode() {
    const btn  = document.getElementById('darkModeToggle');
    const icon = document.getElementById('darkModeIcon');
    const body = document.body;

    const saved = localStorage.getItem('srms_dark_mode') === 'true';
    if (saved) {
        body.classList.add('dark-mode');
        if (icon) { icon.classList.replace('bi-moon-fill', 'bi-sun-fill'); }
    }

    if (btn) {
        btn.addEventListener('click', function () {
            const isDark = body.classList.toggle('dark-mode');
            localStorage.setItem('srms_dark_mode', isDark);
            if (icon) {
                icon.classList.toggle('bi-moon-fill', !isDark);
                icon.classList.toggle('bi-sun-fill', isDark);
            }
        });
    }
})();

/* ---- Sidebar toggle (mobile) ---- */
(function initSidebar() {
    const toggleBtn = document.getElementById('sidebarToggleBtn');
    const sidebar   = document.getElementById('sidebar');

    // Create overlay
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    overlay.id = 'sidebarOverlay';
    document.body.appendChild(overlay);

    function openSidebar() {
        sidebar && sidebar.classList.add('show');
        overlay.classList.add('show');
    }

    function closeSidebar() {
        sidebar && sidebar.classList.remove('show');
        overlay.classList.remove('show');
    }

    toggleBtn && toggleBtn.addEventListener('click', openSidebar);
    overlay.addEventListener('click', closeSidebar);
})();

/* ---- Grade auto-calculation ---- */
/**
 * Compute letter grade and grade points from total score.
 * @param {number} score
 * @returns {{letter: string, points: number}}
 */
function computeGrade(score) {
    score = parseFloat(score) || 0;
    if (score >= 70) return { letter: 'A', points: 4.0 };
    if (score >= 60) return { letter: 'B', points: 3.0 };
    if (score >= 50) return { letter: 'C', points: 2.0 };
    if (score >= 45) return { letter: 'D', points: 1.0 };
    return { letter: 'F', points: 0.0 };
}

function updateGradeRow(row) {
    const caInput   = row.querySelector('.ca-score');
    const examInput = row.querySelector('.exam-score');
    const totalSpan = row.querySelector('.total-score');
    const letterSpan= row.querySelector('.letter-grade');
    const pointsSpan= row.querySelector('.grade-points');

    if (!caInput || !examInput) return;

    const ca   = parseFloat(caInput.value)   || 0;
    const exam = parseFloat(examInput.value) || 0;
    const total = ca + exam;

    if (totalSpan)  totalSpan.textContent  = total.toFixed(2);

    const grade = computeGrade(total);
    if (letterSpan) {
        letterSpan.textContent = grade.letter;
        letterSpan.className = 'letter-grade badge bg-' + gradeBadgeColor(grade.letter);
    }
    if (pointsSpan) pointsSpan.textContent = grade.points.toFixed(1);
}

function gradeBadgeColor(letter) {
    const map = { A: 'success', B: 'primary', C: 'warning', D: 'secondary', F: 'danger' };
    return map[letter] || 'secondary';
}

// Attach listeners to all grade rows
$(document).on('input', '.ca-score, .exam-score', function () {
    updateGradeRow(this.closest('tr'));
});

// Trigger on page load for pre-filled values
$(function () {
    document.querySelectorAll('tr').forEach(function (row) {
        if (row.querySelector('.ca-score')) updateGradeRow(row);
    });
});

/* ---- AJAX student search with debounce ---- */
(function initStudentSearch() {
    const searchInput   = document.getElementById('studentSearchInput');
    const resultsDiv    = document.getElementById('studentSearchResults');
    if (!searchInput || !resultsDiv) return;

    let debounceTimer;

    searchInput.addEventListener('input', function () {
        clearTimeout(debounceTimer);
        const query = this.value.trim();

        if (query.length < 2) {
            resultsDiv.innerHTML = '';
            resultsDiv.style.display = 'none';
            return;
        }

        debounceTimer = setTimeout(function () {
            fetch('/srms/api/search_students.php?q=' + encodeURIComponent(query))
                .then(function (res) { return res.json(); })
                .then(function (data) {
                    if (!data.length) {
                        resultsDiv.innerHTML = '<div class="p-2 text-muted">No students found.</div>';
                    } else {
                        resultsDiv.innerHTML = data.map(function (s) {
                            return '<a href="/srms/modules/students/view.php?id=' + s.id + '" class="d-block p-2 search-result-item">' +
                                '<strong>' + s.matric_number + '</strong> – ' + s.full_name + ' (' + s.dept_code + ')</a>';
                        }).join('');
                    }
                    resultsDiv.style.display = 'block';
                })
                .catch(function () {
                    resultsDiv.innerHTML = '<div class="p-2 text-danger">Search failed.</div>';
                    resultsDiv.style.display = 'block';
                });
        }, 350);
    });

    // Hide results when clicking outside
    document.addEventListener('click', function (e) {
        if (!searchInput.contains(e.target) && !resultsDiv.contains(e.target)) {
            resultsDiv.style.display = 'none';
        }
    });
})();

/* ---- Confirm delete modal ---- */
$(document).on('click', '.btn-delete', function (e) {
    e.preventDefault();
    const href  = $(this).attr('href') || $(this).data('href');
    const label = $(this).data('label') || 'this record';

    $('#deleteConfirmLabel').text('Delete ' + label);
    $('#deleteConfirmBody').text('Are you sure you want to delete ' + label + '? This action cannot be undone.');
    $('#deleteConfirmBtn').attr('href', href);
    $('#deleteModal').modal('show');
});

/* ---- Auto-dismiss alerts ---- */
$(function () {
    setTimeout(function () {
        $('.alert-dismissible').alert('close');
    }, 6000);
});

/* ---- Tooltip initialisation ---- */
$(function () {
    const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipEls.forEach(function (el) {
        new bootstrap.Tooltip(el);
    });
});
