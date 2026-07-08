<?php
define('PAGE_TITLE', 'Fee Management');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();
requireRole(['admin','registrar']);

$sessions       = getAllSessions();
$departments    = getAllDepartments();
$currentSession = getCurrentSession();
$filterSession  = (int)($_GET['session_id'] ?? ($currentSession['id'] ?? 0));
$filterDept     = (int)($_GET['dept'] ?? 0);

// Fee structures for session
$structures = db()->fetchAll(
    'SELECT fs.*, d.name AS dept_name, sess.session_name
     FROM fee_structures fs
     JOIN academic_sessions sess ON sess.id = fs.session_id
     LEFT JOIN departments d ON d.id = fs.department_id
     WHERE fs.session_id = :s
     ORDER BY fs.fee_type',
    [':s' => $filterSession]
);

// Per-student payment status
$where  = ['s.status = "active"'];
$params = [];
if ($filterDept) {
    $where[]         = 's.department_id = :dept';
    $params[':dept'] = $filterDept;
}

$studentFees = db()->fetchAll(
    'SELECT s.id, s.matric_number, s.first_name, s.last_name, s.level,
            d.name AS dept_name,
            COALESCE(SUM(CASE WHEN fs.department_id IS NULL OR fs.department_id = s.department_id
                              THEN fs.amount ELSE 0 END), 0) AS total_due,
            COALESCE(SUM(fp.amount_paid), 0) AS total_paid
     FROM students s
     JOIN departments d ON d.id = s.department_id
     LEFT JOIN fee_structures fs ON fs.session_id = :sess1
         AND (fs.department_id IS NULL OR fs.department_id = s.department_id)
         AND (fs.level = "all" OR fs.level = s.level)
     LEFT JOIN fee_payments fp ON fp.student_id = s.id AND fp.session_id = :sess2
     WHERE ' . implode(' AND ', $where) . '
     GROUP BY s.id
     ORDER BY s.last_name',
    array_merge([':sess1' => $filterSession, ':sess2' => $filterSession], $params)
);

// Summary totals
$totalDue       = array_sum(array_column($studentFees, 'total_due'));
$totalCollected = array_sum(array_column($studentFees, 'total_paid'));
$totalBalance   = $totalDue - $totalCollected;

$breadcrumbs = ['Fee Management' => null];
require_once __DIR__ . '/../../includes/header.php';
?>

<div class="d-flex justify-content-between align-items-center mb-3">
    <h4 class="page-title mb-0"><i class="bi bi-cash-coin me-2"></i>Fee Management</h4>
    <a href="<?= BASE_URL ?>/modules/fees/add_payment.php" class="btn btn-primary btn-sm">
        <i class="bi bi-plus-circle me-1"></i>Record Payment
    </a>
</div>

<!-- Summary cards -->
<div class="row g-3 mb-3">
    <div class="col-sm-4">
        <div class="card stat-card card-gradient-blue p-3 text-center">
            <div class="stat-label">Total Due</div>
            <div class="fw-bold fs-4"><?= formatCurrency($totalDue) ?></div>
        </div>
    </div>
    <div class="col-sm-4">
        <div class="card stat-card card-gradient-green p-3 text-center">
            <div class="stat-label">Collected</div>
            <div class="fw-bold fs-4"><?= formatCurrency($totalCollected) ?></div>
        </div>
    </div>
    <div class="col-sm-4">
        <div class="card stat-card card-gradient-red p-3 text-center">
            <div class="stat-label">Outstanding</div>
            <div class="fw-bold fs-4"><?= formatCurrency($totalBalance) ?></div>
        </div>
    </div>
</div>

<!-- Filters -->
<div class="card mb-3">
    <div class="card-body py-2">
        <form method="GET" class="row g-2 align-items-end">
            <div class="col-sm-4">
                <label class="form-label small mb-1">Session</label>
                <select name="session_id" class="form-select form-select-sm">
                    <?php foreach ($sessions as $s): ?>
                    <option value="<?= $s['id'] ?>" <?= $filterSession == $s['id'] ? 'selected' : '' ?>>
                        <?= sanitize($s['session_name']) ?>
                    </option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-sm-4">
                <label class="form-label small mb-1">Department</label>
                <select name="dept" class="form-select form-select-sm">
                    <option value="">All Departments</option>
                    <?php foreach ($departments as $d): ?>
                    <option value="<?= $d['id'] ?>" <?= $filterDept == $d['id'] ? 'selected' : '' ?>>
                        <?= sanitize($d['name']) ?>
                    </option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-auto">
                <button type="submit" class="btn btn-sm btn-primary">Filter</button>
            </div>
        </form>
    </div>
</div>

<!-- Fee Structures -->
<div class="card mb-3">
    <div class="card-header"><i class="bi bi-list-ul me-1"></i>Fee Structures – Current Session</div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-sm mb-0">
                <thead>
                <tr>
                    <th>Fee Type</th><th>Department</th><th>Level</th>
                    <th>Amount</th><th>Due Date</th>
                </tr>
                </thead>
                <tbody>
                <?php foreach ($structures as $fs): ?>
                <tr>
                    <td><?= sanitize($fs['fee_type']) ?></td>
                    <td><?= $fs['dept_name'] ? sanitize($fs['dept_name']) : '<em class="text-muted">All Departments</em>' ?></td>
                    <td><?= sanitize($fs['level'] === 'all' ? 'All Levels' : $fs['level'] . 'L') ?></td>
                    <td><strong><?= formatCurrency((float)$fs['amount']) ?></strong></td>
                    <td><?= formatDate($fs['due_date']) ?></td>
                </tr>
                <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- Per-student Fee Status -->
<div class="card">
    <div class="card-header"><i class="bi bi-people me-1"></i>Student Payment Status</div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-hover table-sm mb-0">
                <thead>
                <tr>
                    <th>Matric No.</th><th>Student Name</th><th>Dept</th><th>Level</th>
                    <th>Total Due</th><th>Paid</th><th>Balance</th><th>Status</th><th>Action</th>
                </tr>
                </thead>
                <tbody>
                <?php foreach ($studentFees as $sf): ?>
                <?php
                $due  = (float)$sf['total_due'];
                $paid = (float)$sf['total_paid'];
                $bal  = $due - $paid;
                $pct  = $due > 0 ? min(100, round(($paid / $due) * 100)) : 100;
                ?>
                <tr>
                    <td><?= sanitize($sf['matric_number']) ?></td>
                    <td>
                        <a href="<?= BASE_URL ?>/modules/students/view.php?id=<?= $sf['id'] ?>">
                            <?= sanitize($sf['last_name'] . ', ' . $sf['first_name']) ?>
                        </a>
                    </td>
                    <td><?= sanitize($sf['dept_name']) ?></td>
                    <td><?= sanitize($sf['level']) ?>L</td>
                    <td><?= formatCurrency($due) ?></td>
                    <td><?= formatCurrency($paid) ?></td>
                    <td class="<?= $bal > 0 ? 'balance-due' : 'balance-clear' ?>">
                        <?= formatCurrency($bal) ?>
                    </td>
                    <td>
                        <div class="d-flex align-items-center gap-1">
                            <div class="progress flex-grow-1" style="height:6px;min-width:50px;">
                                <div class="progress-bar <?= $pct >= 100 ? 'bg-success' : ($pct >= 50 ? 'bg-warning' : 'bg-danger') ?>"
                                     style="width:<?= $pct ?>%"></div>
                            </div>
                            <small><?= $pct ?>%</small>
                        </div>
                    </td>
                    <td>
                        <a href="<?= BASE_URL ?>/modules/fees/add_payment.php?student_id=<?= $sf['id'] ?>"
                           class="btn btn-sm btn-outline-success">
                            <i class="bi bi-plus-circle"></i>
                        </a>
                        <a href="<?= BASE_URL ?>/modules/fees/statement.php?student_id=<?= $sf['id'] ?>&session_id=<?= $filterSession ?>"
                           class="btn btn-sm btn-outline-info">
                            <i class="bi bi-receipt"></i>
                        </a>
                    </td>
                </tr>
                <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>

<?php require_once __DIR__ . '/../../includes/footer.php'; ?>
