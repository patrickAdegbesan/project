<?php
// ============================================================
// SRMS – View Student Profile
// ============================================================
define('PAGE_TITLE', 'Student Profile');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();

$id      = (int)($_GET['id'] ?? 0);
$student = getStudentById($id);

if (!$student) {
    flashMessage('danger', 'Student not found.');
    redirect(BASE_URL . '/modules/students/index.php');
}

$currentSession = getCurrentSession();
$sessionId      = $currentSession ? (int)$currentSession['id'] : 0;

// GPA / CGPA
$gpa  = calculateGPA($id, $sessionId);
$cgpa = calculateCGPA($id);

// Current session enrollments with grades
$enrollments = db()->fetchAll(
    'SELECT c.course_code, c.course_title, c.credit_units, c.semester,
            g.ca_score, g.exam_score, g.total_score, g.letter_grade, g.grade_points,
            sc.session_id,
            sess.session_name
     FROM student_courses sc
     JOIN courses c ON c.id = sc.course_id
     JOIN academic_sessions sess ON sess.id = sc.session_id
     LEFT JOIN grades g ON g.student_id = sc.student_id
         AND g.course_id = sc.course_id AND g.session_id = sc.session_id
     WHERE sc.student_id = :s
     ORDER BY sess.id DESC, c.course_code',
    [':s' => $id]
);

// Attendance summary per course
$attendanceSummary = db()->fetchAll(
    'SELECT c.course_code, c.course_title,
            COUNT(*) AS total,
            SUM(a.status IN ("present","late")) AS attended
     FROM attendance a
     JOIN courses c ON c.id = a.course_id
     WHERE a.student_id = :s AND a.session_id = :ss
     GROUP BY c.id',
    [':s' => $id, ':ss' => $sessionId]
);

// Fee balance
$feeInfo = getFeeBalance($id, $sessionId);

// Initials for avatar
$initials = strtoupper(substr($student['first_name'], 0, 1) . substr($student['last_name'], 0, 1));

$breadcrumbs = [
    'Students' => BASE_URL . '/modules/students/index.php',
    sanitize($student['first_name'] . ' ' . $student['last_name']) => null,
];
require_once __DIR__ . '/../../includes/header.php';
?>

<div class="d-flex justify-content-between align-items-start mb-3 flex-wrap gap-2">
    <h4 class="page-title mb-0"><i class="bi bi-person-circle me-2"></i>Student Profile</h4>
    <div class="d-flex gap-2 no-print">
        <?php if (in_array($_SESSION['user_role'], ['admin','registrar'])): ?>
        <a href="<?= BASE_URL ?>/modules/students/edit.php?id=<?= $id ?>"
           class="btn btn-outline-secondary btn-sm">
            <i class="bi bi-pencil me-1"></i>Edit
        </a>
        <?php endif; ?>
        <a href="<?= BASE_URL ?>/modules/reports/transcript.php?student_id=<?= $id ?>"
           class="btn btn-outline-info btn-sm" target="_blank">
            <i class="bi bi-file-earmark-person me-1"></i>Transcript
        </a>
        <button class="btn btn-outline-secondary btn-sm" onclick="window.print()">
            <i class="bi bi-printer me-1"></i>Print
        </button>
    </div>
</div>

<!-- PROFILE HEADER CARD -->
<div class="card mb-3">
    <div class="card-body">
        <div class="row align-items-center g-3">
            <div class="col-auto">
                <div class="avatar-circle"><?= $initials ?></div>
            </div>
            <div class="col">
                <h5 class="mb-0 fw-bold">
                    <?= sanitize($student['first_name'] . ' ' . ($student['middle_name'] ? $student['middle_name'] . ' ' : '') . $student['last_name']) ?>
                </h5>
                <div class="text-muted small"><?= sanitize($student['matric_number']) ?></div>
                <div class="mt-1">
                    <?= statusBadge($student['status']) ?>
                    <span class="badge bg-secondary ms-1"><?= sanitize($student['dept_code']) ?></span>
                    <span class="badge bg-light text-dark border ms-1"><?= sanitize($student['level']) ?>L</span>
                </div>
            </div>
            <div class="col-md-auto">
                <div class="row g-3 text-center">
                    <div class="col">
                        <div class="fw-bold fs-4 text-primary"><?= number_format($gpa, 2) ?></div>
                        <small class="text-muted">Session GPA</small>
                    </div>
                    <div class="col">
                        <div class="fw-bold fs-4 text-success"><?= number_format($cgpa, 2) ?></div>
                        <small class="text-muted">CGPA</small>
                    </div>
                    <div class="col">
                        <div class="fw-bold fs-4 <?= $feeInfo['balance'] > 0 ? 'text-danger' : 'text-success' ?>">
                            <?= formatCurrency($feeInfo['balance']) ?>
                        </div>
                        <small class="text-muted">Fee Balance</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row g-3">
    <!-- PERSONAL DETAILS -->
    <div class="col-lg-5">
        <div class="card h-100">
            <div class="card-header"><i class="bi bi-info-circle me-1"></i>Personal Details</div>
            <div class="card-body">
                <table class="table table-sm table-borderless mb-0">
                    <tr><th class="text-muted small" style="width:40%">Date of Birth</th>
                        <td><?= formatDate($student['date_of_birth']) ?></td></tr>
                    <tr><th class="text-muted small">Gender</th>
                        <td><?= sanitize(ucfirst($student['gender'])) ?></td></tr>
                    <tr><th class="text-muted small">Email</th>
                        <td><?= sanitize($student['email'] ?? 'N/A') ?></td></tr>
                    <tr><th class="text-muted small">Phone</th>
                        <td><?= sanitize($student['phone'] ?? 'N/A') ?></td></tr>
                    <tr><th class="text-muted small">State of Origin</th>
                        <td><?= sanitize($student['state_of_origin'] ?? 'N/A') ?></td></tr>
                    <tr><th class="text-muted small">Nationality</th>
                        <td><?= sanitize($student['nationality'] ?? 'Nigerian') ?></td></tr>
                    <tr><th class="text-muted small">Religion</th>
                        <td><?= sanitize($student['religion'] ?? 'N/A') ?></td></tr>
                    <tr><th class="text-muted small">Address</th>
                        <td><?= sanitize($student['address'] ?? 'N/A') ?></td></tr>
                    <tr><th class="text-muted small">Department</th>
                        <td><?= sanitize($student['dept_name']) ?></td></tr>
                    <tr><th class="text-muted small">Admission Date</th>
                        <td><?= formatDate($student['admission_date']) ?></td></tr>
                    <tr><th class="text-muted small">Class Standing</th>
                        <td><strong><?= getClassStanding($cgpa) ?></strong></td></tr>
                </table>
            </div>
        </div>
    </div>

    <!-- GUARDIAN -->
    <div class="col-lg-3">
        <div class="card mb-3">
            <div class="card-header"><i class="bi bi-house-heart me-1"></i>Guardian Info</div>
            <div class="card-body">
                <table class="table table-sm table-borderless mb-0">
                    <tr><th class="text-muted small">Name</th>
                        <td><?= sanitize($student['guardian_name'] ?? 'N/A') ?></td></tr>
                    <tr><th class="text-muted small">Relationship</th>
                        <td><?= sanitize($student['guardian_relationship'] ?? 'N/A') ?></td></tr>
                    <tr><th class="text-muted small">Phone</th>
                        <td><?= sanitize($student['guardian_phone'] ?? 'N/A') ?></td></tr>
                    <tr><th class="text-muted small">Email</th>
                        <td><?= sanitize($student['guardian_email'] ?? 'N/A') ?></td></tr>
                    <tr><th class="text-muted small">Address</th>
                        <td><?= sanitize($student['guardian_address'] ?? 'N/A') ?></td></tr>
                </table>
            </div>
        </div>

        <!-- FEE SUMMARY -->
        <div class="card">
            <div class="card-header"><i class="bi bi-cash-coin me-1"></i>Fee Summary (Current Session)</div>
            <div class="card-body">
                <div class="d-flex justify-content-between mb-1">
                    <span class="text-muted small">Total Due</span>
                    <strong><?= formatCurrency($feeInfo['due']) ?></strong>
                </div>
                <div class="d-flex justify-content-between mb-1">
                    <span class="text-muted small">Paid</span>
                    <strong class="text-success"><?= formatCurrency($feeInfo['paid']) ?></strong>
                </div>
                <hr class="my-1">
                <div class="d-flex justify-content-between">
                    <span class="small fw-bold">Balance</span>
                    <strong class="<?= $feeInfo['balance'] > 0 ? 'balance-due' : 'balance-clear' ?>">
                        <?= formatCurrency($feeInfo['balance']) ?>
                    </strong>
                </div>
                <?php if (in_array($_SESSION['user_role'], ['admin','registrar'])): ?>
                <a href="<?= BASE_URL ?>/modules/fees/add_payment.php?student_id=<?= $id ?>"
                   class="btn btn-sm btn-outline-success mt-2 w-100 no-print">
                    <i class="bi bi-plus-circle me-1"></i>Record Payment
                </a>
                <?php endif; ?>
            </div>
        </div>
    </div>

    <!-- COURSE + GRADES -->
    <div class="col-lg-4">
        <div class="card mb-3">
            <div class="card-header"><i class="bi bi-bar-chart me-1"></i>Academic Records</div>
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-sm mb-0">
                        <thead>
                        <tr>
                            <th>Course</th>
                            <th>Session</th>
                            <th>Score</th>
                            <th>Grade</th>
                        </tr>
                        </thead>
                        <tbody>
                        <?php foreach ($enrollments as $e): ?>
                        <tr>
                            <td class="small">
                                <strong><?= sanitize($e['course_code']) ?></strong><br>
                                <span class="text-muted" style="font-size:0.7rem"><?= sanitize($e['course_title']) ?></span>
                            </td>
                            <td class="small"><?= sanitize($e['session_name']) ?></td>
                            <td class="small"><?= $e['total_score'] !== null ? number_format((float)$e['total_score'], 1) : '–' ?></td>
                            <td>
                                <?php if ($e['letter_grade']): ?>
                                <span class="badge bg-<?= ['A'=>'success','B'=>'primary','C'=>'warning','D'=>'secondary','F'=>'danger'][$e['letter_grade']] ?? 'secondary' ?>">
                                    <?= sanitize($e['letter_grade']) ?>
                                </span>
                                <?php else: ?>
                                <span class="text-muted">–</span>
                                <?php endif; ?>
                            </td>
                        </tr>
                        <?php endforeach; ?>
                        <?php if (empty($enrollments)): ?>
                        <tr><td colspan="4" class="text-center text-muted py-2">No enrollments.</td></tr>
                        <?php endif; ?>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- ATTENDANCE SUMMARY -->
<div class="card mt-3">
    <div class="card-header"><i class="bi bi-calendar-check me-1"></i>Attendance Summary (Current Session)</div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-sm mb-0">
                <thead>
                <tr><th>Course</th><th>Total Classes</th><th>Attended</th><th>Rate</th><th>Status</th></tr>
                </thead>
                <tbody>
                <?php foreach ($attendanceSummary as $att): ?>
                <?php $rate = $att['total'] > 0 ? round(($att['attended'] / $att['total']) * 100, 1) : 0; ?>
                <tr>
                    <td><strong><?= sanitize($att['course_code']) ?></strong> – <?= sanitize($att['course_title']) ?></td>
                    <td><?= $att['total'] ?></td>
                    <td><?= $att['attended'] ?></td>
                    <td>
                        <div class="progress" style="height:8px;width:80px;">
                            <div class="progress-bar <?= $rate >= 75 ? 'bg-success' : ($rate >= 50 ? 'bg-warning' : 'bg-danger') ?>"
                                 style="width:<?= $rate ?>%"></div>
                        </div>
                        <small><?= $rate ?>%</small>
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
                <?php if (empty($attendanceSummary)): ?>
                <tr><td colspan="5" class="text-center text-muted py-2">No attendance records.</td></tr>
                <?php endif; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>

<?php require_once __DIR__ . '/../../includes/footer.php'; ?>
