<?php
define('PAGE_TITLE', 'Record Fee Payment');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();
requireRole(['admin','registrar']);

$sessions       = getAllSessions();
$currentSession = getCurrentSession();
$preloadStudent = (int)($_GET['student_id'] ?? 0);

// Get all active students for select
$students = db()->fetchAll(
    'SELECT id, matric_number, first_name, last_name FROM students WHERE status = "active" ORDER BY last_name'
);

$errors   = [];
$formData = [
    'student_id'       => $preloadStudent,
    'session_id'       => $currentSession['id'] ?? 0,
    'payment_date'     => date('Y-m-d'),
    'payment_method'   => 'bank_transfer',
    'receipt_number'   => generateReceiptNumber(),
    'amount_paid'      => '',
    'fee_structure_id' => '',
    'remarks'          => '',
];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verifyCsrf();

    $fields = ['student_id','session_id','fee_structure_id','amount_paid','payment_date','payment_method','receipt_number','remarks'];
    foreach ($fields as $f) $formData[$f] = trim($_POST[$f] ?? '');

    if (empty($formData['student_id']))       $errors[] = 'Student is required.';
    if (empty($formData['fee_structure_id'])) $errors[] = 'Fee type is required.';
    if (!is_numeric($formData['amount_paid']) || (float)$formData['amount_paid'] <= 0)
        $errors[] = 'Valid payment amount is required.';
    if (empty($formData['payment_date']))     $errors[] = 'Payment date is required.';
    if (empty($formData['receipt_number']))   $errors[] = 'Receipt number is required.';

    // Check receipt number uniqueness
    $dupReceipt = db()->fetchOne(
        'SELECT id FROM fee_payments WHERE receipt_number = :r',
        [':r' => $formData['receipt_number']]
    );
    if ($dupReceipt) $errors[] = 'Receipt number already exists. A new one has been generated.';

    if (empty($errors)) {
        try {
            db()->execute(
                'INSERT INTO fee_payments
                 (student_id, session_id, fee_structure_id, amount_paid, payment_date,
                  payment_method, receipt_number, remarks, received_by)
                 VALUES (:sid, :sess, :fid, :amt, :pdate, :method, :rcpt, :remarks, :by)',
                [
                    ':sid'     => (int)$formData['student_id'],
                    ':sess'    => (int)$formData['session_id'],
                    ':fid'     => (int)$formData['fee_structure_id'],
                    ':amt'     => (float)$formData['amount_paid'],
                    ':pdate'   => $formData['payment_date'],
                    ':method'  => $formData['payment_method'],
                    ':rcpt'    => $formData['receipt_number'],
                    ':remarks' => $formData['remarks'] ?: null,
                    ':by'      => $_SESSION['user_id'],
                ]
            );
            $payId = (int)db()->lastInsertId();
            logAudit($_SESSION['user_id'], 'ADD_PAYMENT', 'fees',
                "Recorded payment {$formData['receipt_number']} for student ID {$formData['student_id']}");
            flashMessage('success', "Payment recorded. Receipt: {$formData['receipt_number']}");
            redirect(BASE_URL . '/modules/fees/statement.php?student_id=' . $formData['student_id'] . '&session_id=' . $formData['session_id']);
        } catch (PDOException $e) {
            $errors[] = 'Database error: ' . $e->getMessage();
        }
    } else {
        // Regenerate receipt number on error
        $formData['receipt_number'] = generateReceiptNumber();
    }
}

$breadcrumbs = ['Fee Management' => BASE_URL . '/modules/fees/index.php', 'Record Payment' => null];
require_once __DIR__ . '/../../includes/header.php';
?>

<h4 class="page-title"><i class="bi bi-receipt me-2"></i>Record Fee Payment</h4>

<?php if (!empty($errors)): ?>
<div class="alert alert-danger"><ul class="mb-0">
    <?php foreach ($errors as $e): ?><li><?= sanitize($e) ?></li><?php endforeach; ?>
</ul></div>
<?php endif; ?>

<div class="card" style="max-width:750px;">
    <div class="card-body">
        <form method="POST" novalidate>
            <input type="hidden" name="csrf_token" value="<?= htmlspecialchars($_SESSION['csrf_token']) ?>">
            <div class="row g-3">
                <div class="col-md-6">
                    <label class="form-label">Student <span class="text-danger">*</span></label>
                    <select name="student_id" class="form-select" id="studentSelect" required>
                        <option value="">Select Student</option>
                        <?php foreach ($students as $s): ?>
                        <option value="<?= $s['id'] ?>"
                            <?= $formData['student_id'] == $s['id'] ? 'selected' : '' ?>>
                            <?= sanitize($s['matric_number'] . ' – ' . $s['last_name'] . ', ' . $s['first_name']) ?>
                        </option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Academic Session <span class="text-danger">*</span></label>
                    <select name="session_id" class="form-select" id="sessionSelect">
                        <?php foreach ($sessions as $sess): ?>
                        <option value="<?= $sess['id'] ?>"
                            <?= $formData['session_id'] == $sess['id'] ? 'selected' : '' ?>>
                            <?= sanitize($sess['session_name']) ?>
                        </option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Fee Type <span class="text-danger">*</span></label>
                    <select name="fee_structure_id" class="form-select" required>
                        <option value="">Select Fee Type</option>
                        <?php
                        $allStructures = db()->fetchAll(
                            'SELECT fs.*, d.name AS dept_name FROM fee_structures fs
                             LEFT JOIN departments d ON d.id = fs.department_id
                             ORDER BY fs.session_id DESC, fs.fee_type'
                        );
                        foreach ($allStructures as $fs):
                        ?>
                        <option value="<?= $fs['id'] ?>"
                            <?= $formData['fee_structure_id'] == $fs['id'] ? 'selected' : '' ?>>
                            <?= sanitize($fs['fee_type'] . ' – ' . formatCurrency((float)$fs['amount']))
                                . ($fs['dept_name'] ? ' (' . $fs['dept_name'] . ')' : ' (All Depts)') ?>
                        </option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Amount Paid (₦) <span class="text-danger">*</span></label>
                    <div class="input-group">
                        <span class="input-group-text">₦</span>
                        <input type="number" name="amount_paid" class="form-control"
                               min="0.01" step="0.01"
                               value="<?= sanitize($formData['amount_paid']) ?>"
                               placeholder="0.00" required>
                    </div>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Payment Date <span class="text-danger">*</span></label>
                    <input type="date" name="payment_date" class="form-control"
                           value="<?= sanitize($formData['payment_date']) ?>" required>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Payment Method</label>
                    <select name="payment_method" class="form-select">
                        <?php foreach (['bank_transfer'=>'Bank Transfer','cash'=>'Cash','online'=>'Online'] as $v=>$l): ?>
                        <option value="<?= $v ?>" <?= $formData['payment_method'] === $v ? 'selected' : '' ?>>
                            <?= $l ?>
                        </option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Receipt Number</label>
                    <div class="input-group">
                        <input type="text" name="receipt_number" class="form-control"
                               value="<?= sanitize($formData['receipt_number']) ?>" required>
                        <button class="btn btn-outline-secondary" type="button" id="regenReceipt"
                                title="Generate new receipt number">
                            <i class="bi bi-arrow-clockwise"></i>
                        </button>
                    </div>
                </div>
                <div class="col-12">
                    <label class="form-label">Remarks</label>
                    <textarea name="remarks" class="form-control" rows="2"
                              placeholder="Optional notes…"><?= sanitize($formData['remarks']) ?></textarea>
                </div>
                <div class="col-12 d-flex gap-2">
                    <button type="submit" class="btn btn-success px-4">
                        <i class="bi bi-check-lg me-1"></i>Save Payment
                    </button>
                    <a href="<?= BASE_URL ?>/modules/fees/index.php" class="btn btn-outline-secondary">Cancel</a>
                </div>
            </div>
        </form>
    </div>
</div>

<script>
document.getElementById('regenReceipt').addEventListener('click', function () {
    const now  = new Date();
    const ts   = now.getFullYear().toString() +
                 String(now.getMonth()+1).padStart(2,'0') +
                 String(now.getDate()).padStart(2,'0');
    const rand = Math.random().toString(36).substring(2, 8).toUpperCase();
    document.querySelector('input[name="receipt_number"]').value = 'RCP-' + ts + '-' + rand;
});
</script>

<?php require_once __DIR__ . '/../../includes/footer.php'; ?>
