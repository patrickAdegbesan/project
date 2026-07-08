<?php
// ============================================================
// SRMS – Dashboard
// ============================================================
define('PAGE_TITLE', 'Dashboard');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();

$currentSession = getCurrentSession();
$sessionId      = $currentSession ? (int)$currentSession['id'] : 0;

// ---- Stats ----
$totalStudents = (int)db()->fetchOne('SELECT COUNT(*) AS c FROM students WHERE status = "active"')['c'];
$totalCourses  = (int)db()->fetchOne('SELECT COUNT(*) AS c FROM courses WHERE status = "active"')['c'];
$totalUsers    = (int)db()->fetchOne('SELECT COUNT(*) AS c FROM users WHERE status = "active"')['c'];

$feesCollected = (float)(db()->fetchOne(
    'SELECT COALESCE(SUM(amount_paid),0) AS total FROM fee_payments WHERE session_id = :s',
    [':s' => $sessionId]
)['total'] ?? 0);

// Total fees due in current session (all students * applicable structures)
$feesDue = (float)(db()->fetchOne(
    'SELECT COALESCE(SUM(amount),0) AS total FROM fee_structures WHERE session_id = :s',
    [':s' => $sessionId]
)['total'] ?? 0);
$pendingFees = max(0, $feesDue - $feesCollected);

// ---- Recent enrollments ----
$recentEnrollments = db()->fetchAll(
    'SELECT s.matric_number, s.first_name, s.last_name, d.name AS dept_name,
            s.level, s.admission_date, s.status
     FROM students s
     JOIN departments d ON d.id = s.department_id
     ORDER BY s.created_at DESC LIMIT 8'
);

// ---- Recent audit logs ----
$recentAudit = db()->fetchAll(
    'SELECT a.*, u.full_name FROM audit_logs a
     LEFT JOIN users u ON u.id = a.user_id
     ORDER BY a.created_at DESC LIMIT 6'
);

// ---- Students per department (for chart) ----
$deptStats = db()->fetchAll(
    'SELECT d.name, d.code, COUNT(s.id) AS student_count
     FROM departments d
     LEFT JOIN students s ON s.department_id = d.id AND s.status = "active"
     GROUP BY d.id ORDER BY d.name'
);

// ---- Grade distribution (for chart) ----
$gradeDist = db()->fetchAll(
    'SELECT letter_grade, COUNT(*) AS cnt FROM grades GROUP BY letter_grade ORDER BY letter_grade'
);

require_once __DIR__ . '/../../includes/header.php';
?>

<div class="d-flex justify-content-between align-items-center mb-3">
    <h4 class="page-title mb-0"><i class="bi bi-speedometer2 me-2"></i>Dashboard</h4>
    <div>
        <span class="badge bg-primary fs-6">
            <i class="bi bi-calendar me-1"></i>
            <?= $currentSession ? sanitize($currentSession['session_name'] . ' – ' . ucfirst($currentSession['semester']) . ' Semester') : 'No Active Session' ?>
        </span>
    </div>
</div>

<!-- STAT CARDS -->
<div class="row g-3 mb-4">
    <div class="col-sm-6 col-xl-3">
        <div class="card stat-card card-gradient-blue p-3">
            <div class="stat-label">Active Students</div>
            <div class="stat-value"><?= number_format($totalStudents) ?></div>
            <i class="bi bi-people-fill stat-icon"></i>
            <small class="opacity-75 mt-1 d-block">Enrolled this session</small>
        </div>
    </div>
    <div class="col-sm-6 col-xl-3">
        <div class="card stat-card card-gradient-green p-3">
            <div class="stat-label">Active Courses</div>
            <div class="stat-value"><?= number_format($totalCourses) ?></div>
            <i class="bi bi-book-fill stat-icon"></i>
            <small class="opacity-75 mt-1 d-block">Offered this semester</small>
        </div>
    </div>
    <div class="col-sm-6 col-xl-3">
        <div class="card stat-card card-gradient-teal p-3">
            <div class="stat-label">Fees Collected</div>
            <div class="stat-value" style="font-size:1.5rem"><?= formatCurrency($feesCollected) ?></div>
            <i class="bi bi-cash-stack stat-icon"></i>
            <small class="opacity-75 mt-1 d-block">Current session</small>
        </div>
    </div>
    <div class="col-sm-6 col-xl-3">
        <div class="card stat-card card-gradient-orange p-3">
            <div class="stat-label">Outstanding Fees</div>
            <div class="stat-value" style="font-size:1.5rem"><?= formatCurrency($pendingFees) ?></div>
            <i class="bi bi-exclamation-circle-fill stat-icon"></i>
            <small class="opacity-75 mt-1 d-block">Pending collection</small>
        </div>
    </div>
</div>

<!-- CHARTS ROW -->
<div class="row g-3 mb-4">
    <div class="col-lg-7">
        <div class="card h-100">
            <div class="card-header d-flex justify-content-between align-items-center">
                <span><i class="bi bi-bar-chart-fill me-1 text-primary"></i>Students per Department</span>
            </div>
            <div class="card-body">
                <div class="chart-container">
                    <canvas id="deptChart"></canvas>
                </div>
            </div>
        </div>
    </div>
    <div class="col-lg-5">
        <div class="card h-100">
            <div class="card-header">
                <i class="bi bi-pie-chart-fill me-1 text-success"></i>Grade Distribution
            </div>
            <div class="card-body">
                <div class="chart-container">
                    <canvas id="gradeChart"></canvas>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- RECENT ENROLLMENTS + AUDIT LOG -->
<div class="row g-3">
    <div class="col-lg-7">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <span><i class="bi bi-person-check me-1"></i>Recent Student Records</span>
                <a href="<?= BASE_URL ?>/modules/students/index.php" class="btn btn-sm btn-outline-primary">
                    View All
                </a>
            </div>
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-hover table-sm mb-0">
                        <thead>
                        <tr>
                            <th>Matric No.</th>
                            <th>Name</th>
                            <th>Department</th>
                            <th>Level</th>
                            <th>Status</th>
                        </tr>
                        </thead>
                        <tbody>
                        <?php foreach ($recentEnrollments as $s): ?>
                        <tr>
                            <td><a href="<?= BASE_URL ?>/modules/students/view.php?id=<?= /* we need id */ '' ?>"
                                   class="text-decoration-none fw-semibold"><?= sanitize($s['matric_number']) ?></a></td>
                            <td><?= sanitize($s['first_name'] . ' ' . $s['last_name']) ?></td>
                            <td><?= sanitize($s['dept_name']) ?></td>
                            <td><?= sanitize($s['level']) ?></td>
                            <td><?= statusBadge($s['status']) ?></td>
                        </tr>
                        <?php endforeach; ?>
                        <?php if (empty($recentEnrollments)): ?>
                        <tr><td colspan="5" class="text-center text-muted py-3">No student records found.</td></tr>
                        <?php endif; ?>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <div class="col-lg-5">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <span><i class="bi bi-shield-check me-1"></i>Recent Activity</span>
                <?php if ($_SESSION['user_role'] === 'admin'): ?>
                <a href="<?= BASE_URL ?>/modules/audit/index.php" class="btn btn-sm btn-outline-secondary">
                    Full Log
                </a>
                <?php endif; ?>
            </div>
            <div class="card-body p-0">
                <ul class="list-group list-group-flush">
                    <?php foreach ($recentAudit as $log): ?>
                    <li class="list-group-item d-flex gap-2 py-2 px-3">
                        <div class="flex-shrink-0">
                            <span class="badge bg-secondary"><?= sanitize($log['module']) ?></span>
                        </div>
                        <div class="flex-grow-1 small">
                            <div class="fw-semibold"><?= sanitize($log['action']) ?></div>
                            <div class="text-muted"><?= sanitize($log['full_name'] ?? 'System') ?></div>
                            <div class="text-muted" style="font-size:0.7rem">
                                <?= sanitize(date('d/m/Y H:i', strtotime($log['created_at']))) ?>
                            </div>
                        </div>
                    </li>
                    <?php endforeach; ?>
                    <?php if (empty($recentAudit)): ?>
                    <li class="list-group-item text-center text-muted py-3">No activity recorded.</li>
                    <?php endif; ?>
                </ul>
            </div>
        </div>
    </div>
</div>

<!-- Delete confirm modal (global) -->
<div class="modal fade" id="deleteModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="deleteConfirmLabel">Confirm Delete</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body" id="deleteConfirmBody">Are you sure?</div>
            <div class="modal-footer">
                <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <a href="#" class="btn btn-danger" id="deleteConfirmBtn">Delete</a>
            </div>
        </div>
    </div>
</div>

<?php
// Build chart data for inline JS
$deptLabels  = json_encode(array_column($deptStats, 'name'));
$deptCounts  = json_encode(array_column($deptStats, 'student_count'));
$gradeLabels = json_encode(array_column($gradeDist, 'letter_grade'));
$gradeCounts = json_encode(array_column($gradeDist, 'cnt'));

$extraJs = <<<SCRIPT
<script>
// Bar chart – Students per dept
const deptCtx = document.getElementById('deptChart').getContext('2d');
new Chart(deptCtx, {
    type: 'bar',
    data: {
        labels: {$deptLabels},
        datasets: [{
            label: 'Students',
            data: {$deptCounts},
            backgroundColor: ['#1a237e','#1b5e20','#e65100','#4a148c','#01579b'],
            borderRadius: 6,
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
    }
});

// Pie chart – Grade distribution
const gradeCtx = document.getElementById('gradeChart').getContext('2d');
new Chart(gradeCtx, {
    type: 'pie',
    data: {
        labels: {$gradeLabels},
        datasets: [{
            data: {$gradeCounts},
            backgroundColor: ['#2e7d32','#1a237e','#f57f17','#616161','#c62828'],
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom' } }
    }
});
</script>
SCRIPT;

require_once __DIR__ . '/../../includes/footer.php';
?>
