<?php
define('PAGE_TITLE', 'Attendance');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();
requireRole(['admin','registrar','teacher']);

$currentSession = getCurrentSession();
$sessions = getAllSessions();
$filterSession = (int)($_GET['session_id'] ?? ($currentSession['id'] ?? 0));

// Summary: attendance per student per course
$records = db()->fetchAll(
    'SELECT s.matric_number, s.first_name, s.last_name, c.course_code, c.course_title,
            COUNT(*) AS total_classes,
            SUM(a.status IN ("present","late")) AS attended,
            SUM(a.status = "absent") AS absences
     FROM attendance a
     JOIN students s ON s.id = a.student_id
     JOIN courses c ON c.id = a.course_id
     WHERE a.session_id = :sess
     GROUP BY a.student_id, a.course_id
     ORDER BY s.last_name, c.course_code',
    [':sess' => $filterSession]
);

$breadcrumbs = ['Attendance' => null];
require_once __DIR__ . '/../../includes/header.php';
?>

<div class="d-flex justify-content-between align-items-center mb-3">
    <h4 class="page-title mb-0"><i class="bi bi-calendar-check me-2"></i>Attendance Overview</h4>
    <div class="d-flex gap-2">
        <a href="<?= BASE_URL ?>/modules/attendance/mark.php" class="btn btn-primary btn-sm">
            <i class="bi bi-check2-all me-1"></i>Mark Attendance
        </a>
        <a href="<?= BASE_URL ?>/modules/attendance/report.php" class="btn btn-outline-secondary btn-sm">
            <i class="bi bi-file-text me-1"></i>Report
        </a>
    </div>
</div>

<div class="card mb-3">
    <div class="card-body py-2">
        <form method="GET" class="row g-2 align-items-end">
            <div class="col-sm-5">
                <label class="form-label small mb-1">Session</label>
                <select name="session_id" class="form-select form-select-sm">
                    <?php foreach ($sessions as $s): ?>
                    <option value="<?= $s['id'] ?>" <?= $filterSession == $s['id'] ? 'selected' : '' ?>>
                        <?= sanitize($s['session_name']) ?> (<?= ucfirst($s['semester']) ?>)
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

<div class="card">
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-hover table-sm mb-0">
                <thead>
                <tr>
                    <th>Matric No.</th><th>Student</th><th>Course</th>
                    <th>Total Classes</th><th>Attended</th><th>Absences</th>
                    <th>Rate</th><th>Status</th>
                </tr>
                </thead>
                <tbody>
                <?php foreach ($records as $r): ?>
                <?php $rate = $r['total_classes'] > 0 ? round(($r['attended'] / $r['total_classes']) * 100, 1) : 0; ?>
                <tr>
                    <td><?= sanitize($r['matric_number']) ?></td>
                    <td><?= sanitize($r['last_name'] . ', ' . $r['first_name']) ?></td>
                    <td><?= sanitize($r['course_code']) ?></td>
                    <td><?= $r['total_classes'] ?></td>
                    <td class="text-success fw-bold"><?= $r['attended'] ?></td>
                    <td class="text-danger"><?= $r['absences'] ?></td>
                    <td>
                        <div class="d-flex align-items-center gap-2">
                            <div class="progress flex-grow-1" style="height:8px;">
                                <div class="progress-bar <?= $rate>=75 ? 'bg-success' : ($rate>=50 ? 'bg-warning' : 'bg-danger') ?>"
                                     style="width:<?= $rate ?>%"></div>
                            </div>
                            <span class="small"><?= $rate ?>%</span>
                        </div>
                    </td>
                    <td>
                        <?php if ($rate >= 75): ?>
                        <span class="badge bg-success">Good</span>
                        <?php elseif ($rate >= 50): ?>
                        <span class="badge bg-warning text-dark">Low</span>
                        <?php else: ?>
                        <span class="badge bg-danger">Critical</span>
                        <?php endif; ?>
                    </td>
                </tr>
                <?php endforeach; ?>
                <?php if (empty($records)): ?>
                <tr><td colspan="8" class="text-center text-muted py-4">No attendance records for this session.</td></tr>
                <?php endif; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>

<?php require_once __DIR__ . '/../../includes/footer.php'; ?>
