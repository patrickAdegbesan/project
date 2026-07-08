<?php
define('PAGE_TITLE', 'Fee Statement');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();
requireRole(['admin','registrar']);

$studentId = (int)($_GET['student_id'] ?? 0);
$sessionId = (int)($_GET['session_id'] ?? 0);

$student = getStudentById($studentId);
if (!$student) {
    flashMessage('danger', 'Student not found.');
    redirect(BASE_URL . '/modules/fees/index.php');
}

if (!$sessionId) {
    $cur = getCurrentSession();
    $sessionId = $cur ? (int)$cur['id'] : 0;
}

$sessionInfo = db()->fetchOne('SELECT * FROM academic_sessions WHERE id = :id', [':id' => $sessionId]);

// Fee structures applicable
$structures = db()->fetchAll(
    'SELECT fs.* FROM fee_structures fs
     WHERE fs.session_id = :sess
       AND (fs.department_id IS NULL OR fs.department_id = :dept)
       AND (fs.level = "all" OR fs.level = :lvl)',
    [':sess' => $sessionId, ':dept' => $student['department_id'], ':lvl' => $student['level']]
);

// Payments made
$payments = db()->fetchAll(
    'SELECT fp.*, fs.fee_type, u.full_name AS received_by_name
     FROM fee_payments fp
     JOIN fee_structures fs ON fs.id = fp.fee_structure_id
     LEFT JOIN users u ON u.id = fp.received_by
     WHERE fp.student_id = :s AND fp.session_id = :sess
     ORDER BY fp.payment_date',
    [':s' => $studentId, ':sess' => $sessionId]
);

$totalDue  = array_sum(array_column($structures, 'amount'));
$totalPaid = array_sum(array_column($payments, 'amount_paid'));
$balance   = $totalDue - $totalPaid;

$breadcrumbs = [
    'Fee Management' => BASE_URL . '/modules/fees/index.php',
    'Statement' => null,
];
require_once __DIR__ . '/../../includes/header.php';
?>

<div class="d-flex justify-content-between align-items-center mb-3 no-print">
    <h4 class="page-title mb-0"><i class="bi bi-receipt me-2"></i>Fee Statement</h4>
    <button class="btn btn-outline-secondary btn-sm" onclick="window.print()">
        <i class="bi bi-printer me-1"></i>Print Statement
    </button>
</div>

<!-- Print header -->
<div class="transcript-header d-none d-print-block">
    <h4><?= INSTITUTION_NAME ?></h4>
    <h5>FEE STATEMENT</h5>
    <p><?= $sessionInfo ? sanitize($sessionInfo['session_name']) : '' ?></p>
</div>

<!-- Student info -->
<div class="card mb-3">
    <div class="card-body">
        <div class="row">
            <div class="col-md-6">
                <table class="table table-sm table-borderless mb-0">
                    <tr><th class="text-muted small" style="width:150px;">Student Name</th>
                        <td><strong><?= sanitize($student['first_name'] . ' ' . $student['last_name']) ?></strong></td></tr>
                    <tr><th class="text-muted small">Matric Number</th>
                        <td><?= sanitize($student['matric_number']) ?></td></tr>
                    <tr><th class="text-muted small">Department</th>
                        <td><?= sanitize($student['dept_name']) ?></td></tr>
                    <tr><th class="text-muted small">Level</th>
                        <td><?= sanitize($student['level']) ?>L</td></tr>
                </table>
            </div>
            <div class="col-md-6">
                <table class="table table-sm table-borderless mb-0">
                    <tr><th class="text-muted small" style="width:150px;">Session</th>
                        <td><?= $sessionInfo ? sanitize($sessionInfo['session_name']) : 'N/A' ?></td></tr>
                    <tr><th class="text-muted small">Semester</th>
                        <td><?= $sessionInfo ? ucfirst($sessionInfo['semester']) : 'N/A' ?></td></tr>
                    <tr><th class="text-muted small">Statement Date</th>
                        <td><?= date('d/m/Y') ?></td></tr>
                </table>
            </div>
        </div>
    </div>
</div>

<!-- Fee Schedule -->
<div class="card mb-3">
    <div class="card-header"><i class="bi bi-list-ul me-1"></i>Fee Schedule</div>
    <div class="card-body p-0">
        <table class="table table-sm mb-0">
            <thead><tr><th>Fee Type</th><th>Level</th><th class="text-end">Amount</th><th>Due Date</th></tr></thead>
            <tbody>
            <?php foreach ($structures as $fs): ?>
            <tr>
                <td><?= sanitize($fs['fee_type']) ?></td>
                <td><?= sanitize($fs['level'] === 'all' ? 'All' : $fs['level'] . 'L') ?></td>
                <td class="text-end"><?= formatCurrency((float)$fs['amount']) ?></td>
                <td><?= formatDate($fs['due_date']) ?></td>
            </tr>
            <?php endforeach; ?>
            <tr class="table-light fw-bold">
                <td colspan="2">Total Due</td>
                <td class="text-end"><?= formatCurrency($totalDue) ?></td>
                <td></td>
            </tr>
            </tbody>
        </table>
    </div>
</div>

<!-- Payments -->
<div class="card mb-3">
    <div class="card-header"><i class="bi bi-cash-stack me-1"></i>Payment History</div>
    <div class="card-body p-0">
        <?php if (empty($payments)): ?>
        <div class="p-3 text-muted">No payments recorded.</div>
        <?php else: ?>
        <table class="table table-sm mb-0">
            <thead><tr>
                <th>Receipt No.</th><th>Date</th><th>Fee Type</th>
                <th>Method</th><th class="text-end">Amount Paid</th><th>Received By</th>
            </tr></thead>
            <tbody>
            <?php foreach ($payments as $p): ?>
            <tr>
                <td><code><?= sanitize($p['receipt_number']) ?></code></td>
                <td><?= formatDate($p['payment_date']) ?></td>
                <td><?= sanitize($p['fee_type']) ?></td>
                <td><?= sanitize(ucwords(str_replace('_', ' ', $p['payment_method']))) ?></td>
                <td class="text-end text-success fw-bold"><?= formatCurrency((float)$p['amount_paid']) ?></td>
                <td><?= sanitize($p['received_by_name'] ?? 'N/A') ?></td>
            </tr>
            <?php endforeach; ?>
            <tr class="table-light fw-bold">
                <td colspan="4">Total Paid</td>
                <td class="text-end text-success"><?= formatCurrency($totalPaid) ?></td>
                <td></td>
            </tr>
            </tbody>
        </table>
        <?php endif; ?>
    </div>
</div>

<!-- Balance -->
<div class="card <?= $balance > 0 ? 'border-danger' : 'border-success' ?>">
    <div class="card-body d-flex justify-content-between align-items-center">
        <h5 class="mb-0 fw-bold">Outstanding Balance</h5>
        <h4 class="mb-0 <?= $balance > 0 ? 'balance-due' : 'balance-clear' ?>">
            <?= formatCurrency($balance) ?>
        </h4>
    </div>
</div>

<!-- Print signature block -->
<div class="print-signature-block mt-4 d-none d-print-flex">
    <div class="print-signature-line">Bursary Officer</div>
    <div class="print-signature-line">Registrar</div>
</div>

<?php require_once __DIR__ . '/../../includes/footer.php'; ?>
