<?php
define('PAGE_TITLE', 'Attendance Report');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();
requireRole(['admin','registrar','teacher']);

$sessions       = getAllSessions();
$departments    = getAllDepartments();
$currentSession = getCurrentSession();
$filterSession  = (int)($_GET['session_id'] ?? ($currentSession['id'] ?? 0));
$filterDept     = (int)($_GET['dept_id'] ?? 0);

$where  = ['a.session_id = :sess'];
$params = [':sess' => $filterSession];
if ($filterDept) {
    $where[]         = 's.department_id = :dept';
    $params[':dept'] = $filterDept;
}

$data = db()->fetchAll(
    'SELECT s.matric_number, s.first_name, s.last_name, d.code AS dept_code,
            c.course_code, c.course_title,
            COUNT(*) AS total,
            SUM(a.status = "present") AS present_count,
            SUM(a.status = "absent")  AS absent_count,
            SUM(a.status = "late")    AS late_count,
            SUM(a.status = "excused") AS excused_count
     FROM attendance a
     JOIN students s ON s.id = a.student_id
     JOIN departments d ON d.id = s.department_id
     JOIN courses c ON c.id = a.course_id
     WHERE ' . implode(' AND ', $where) . '
     GROUP BY a.student_id, a.course_id
     ORDER BY s.last_name, c.course_code',
    $params
);

$sessionInfo = null;
foreach ($sessions as $s) {
    if ($s['id'] == $filterSession) { $sessionInfo = $s; break; }
}

$breadcrumbs = ['Attendance' => BASE_URL . '/modules/attendance/index.php', 'Report' => null];
require_once __DIR__ . '/../../includes/header.php';
?>

<div class="d-flex justify-content-between align-items-center mb-3">
    <h4 class="page-title mb-0"><i class="bi bi-file-text me-2"></i>Attendance Summary Report</h4>
    <button class="btn btn-outline-secondary btn-sm no-print" onclick="window.print()">
        <i class="bi bi-printer me-1"></i>Print
    </button>
</div>

<div class="card mb-3 no-print">
    <div class="card-body py-2">
        <form method="GET" class="row g-2 align-items-end">
            <div class="col-sm-4">
                <label class="form-label small mb-1">Session</label>
                <select name="session_id" class="form-select form-select-sm">
                    <?php foreach ($sessions as $s): ?>
                    <option value="<?= $s['id'] ?>" <?= $filterSession == $s['id'] ? 'selected' : '' ?>>
                        <?= sanitize($s['session_name']) ?> (<?= ucfirst($s['semester']) ?>)
                    </option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-sm-4">
                <label class="form-label small mb-1">Department</label>
                <select name="dept_id" class="form-select form-select-sm">
                    <option value="">All Departments</option>
                    <?php foreach ($departments as $d): ?>
                    <option value="<?= $d['id'] ?>" <?= $filterDept == $d['id'] ? 'selected' : '' ?>>
                        <?= sanitize($d['name']) ?>
                    </option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-auto">
                <button type="submit" class="btn btn-sm btn-primary">Generate</button>
            </div>
        </form>
    </div>
</div>

<!-- Print header -->
<div class="transcript-header d-none d-print-block mb-3">
    <h4><?= INSTITUTION_NAME ?></h4>
    <h5>Attendance Summary Report</h5>
    <p>Session: <?= $sessionInfo ? sanitize($sessionInfo['session_name'] . ' – ' . ucfirst($sessionInfo['semester']) . ' Semester') : 'N/A' ?></p>
    <p>Generated: <?= date('d/m/Y H:i') ?></p>
</div>

<div class="card">
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-bordered table-sm mb-0">
                <thead class="table-dark">
                <tr>
                    <th>Matric No.</th>
                    <th>Student Name</th>
                    <th>Dept</th>
                    <th>Course</th>
                    <th>Total</th>
                    <th>Present</th>
                    <th>Absent</th>
                    <th>Late</th>
                    <th>Excused</th>
                    <th>Rate (%)</th>
                    <th>Remark</th>
                </tr>
                </thead>
                <tbody>
                <?php foreach ($data as $r): ?>
                <?php
                $attended = (int)$r['present_count'] + (int)$r['late_count'];
                $rate     = $r['total'] > 0 ? round(($attended / $r['total']) * 100, 1) : 0;
                $remark   = $rate >= 75 ? 'Satisfactory' : ($rate >= 50 ? 'Low' : 'Critical');
                ?>
                <tr>
                    <td><?= sanitize($r['matric_number']) ?></td>
                    <td><?= sanitize($r['last_name'] . ', ' . $r['first_name']) ?></td>
                    <td><?= sanitize($r['dept_code']) ?></td>
                    <td><?= sanitize($r['course_code']) ?></td>
                    <td><?= $r['total'] ?></td>
                    <td class="text-success"><?= $r['present_count'] ?></td>
                    <td class="text-danger"><?= $r['absent_count'] ?></td>
                    <td class="text-warning"><?= $r['late_count'] ?></td>
                    <td><?= $r['excused_count'] ?></td>
                    <td><strong><?= $rate ?>%</strong></td>
                    <td><?= $remark ?></td>
                </tr>
                <?php endforeach; ?>
                <?php if (empty($data)): ?>
                <tr><td colspan="11" class="text-center text-muted py-3">No data.</td></tr>
                <?php endif; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>

<?php require_once __DIR__ . '/../../includes/footer.php'; ?>
