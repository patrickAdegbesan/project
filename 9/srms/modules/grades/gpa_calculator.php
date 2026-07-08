<?php
define('PAGE_TITLE', 'GPA Calculator');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();
requireRole(['admin','registrar','teacher']);

$studentId       = (int)($_GET['student_id'] ?? 0);
$students        = db()->fetchAll(
    'SELECT id, matric_number, first_name, last_name FROM students ORDER BY last_name'
);
$selectedStudent = null;
$gradesBySession = [];
$cgpa            = 0.0;

if ($studentId) {
    $selectedStudent = getStudentById($studentId);
    if ($selectedStudent) {
        // Fetch all sessions this student has grades
        $sessionsWithGrades = db()->fetchAll(
            'SELECT DISTINCT sess.id, sess.session_name, sess.semester
             FROM grades g
             JOIN academic_sessions sess ON sess.id = g.session_id
             WHERE g.student_id = :s
             ORDER BY sess.id',
            [':s' => $studentId]
        );

        foreach ($sessionsWithGrades as $sess) {
            $rows = db()->fetchAll(
                'SELECT g.*, c.course_code, c.course_title
                 FROM grades g
                 JOIN courses c ON c.id = g.course_id
                 WHERE g.student_id = :s AND g.session_id = :ss
                 ORDER BY c.course_code',
                [':s' => $studentId, ':ss' => $sess['id']]
            );
            $sessionGPA = calculateGPA($studentId, (int)$sess['id']);
            $gradesBySession[] = [
                'session'  => $sess,
                'rows'     => $rows,
                'gpa'      => $sessionGPA,
            ];
        }
        $cgpa = calculateCGPA($studentId);
    }
}

$breadcrumbs = ['Grades' => BASE_URL . '/modules/grades/index.php', 'GPA Calculator' => null];
require_once __DIR__ . '/../../includes/header.php';
?>

<h4 class="page-title"><i class="bi bi-calculator me-2"></i>GPA / CGPA Calculator</h4>

<div class="card mb-3">
    <div class="card-body">
        <form method="GET" class="row g-3 align-items-end">
            <div class="col-sm-6">
                <label class="form-label">Select Student</label>
                <select name="student_id" class="form-select" required>
                    <option value="">-- Choose a student --</option>
                    <?php foreach ($students as $s): ?>
                    <option value="<?= $s['id'] ?>" <?= $studentId == $s['id'] ? 'selected' : '' ?>>
                        <?= sanitize($s['matric_number'] . ' – ' . $s['last_name'] . ', ' . $s['first_name']) ?>
                    </option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-auto">
                <button type="submit" class="btn btn-primary">
                    <i class="bi bi-calculator me-1"></i>Calculate
                </button>
            </div>
        </form>
    </div>
</div>

<?php if ($selectedStudent && !empty($gradesBySession)): ?>

<!-- CGPA Summary -->
<div class="row g-3 mb-3">
    <div class="col-sm-6 col-md-3">
        <div class="card stat-card card-gradient-blue p-3 text-center">
            <div class="stat-label">Cumulative GPA</div>
            <div class="stat-value"><?= number_format($cgpa, 2) ?></div>
        </div>
    </div>
    <div class="col-sm-6 col-md-3">
        <div class="card stat-card card-gradient-green p-3 text-center">
            <div class="stat-label">Class Standing</div>
            <div class="fw-bold fs-5 mt-1"><?= getClassStanding($cgpa) ?></div>
        </div>
    </div>
    <div class="col-sm-6 col-md-3">
        <div class="card stat-card card-gradient-teal p-3 text-center">
            <div class="stat-label">Total Sessions</div>
            <div class="stat-value"><?= count($gradesBySession) ?></div>
        </div>
    </div>
    <div class="col-sm-6 col-md-3">
        <div class="card stat-card card-gradient-purple p-3 text-center">
            <div class="stat-label">Total Credit Units</div>
            <div class="stat-value">
                <?php
                $totalUnits = 0;
                foreach ($gradesBySession as $g) {
                    foreach ($g['rows'] as $r) $totalUnits += (int)$r['credit_units'];
                }
                echo $totalUnits;
                ?>
            </div>
        </div>
    </div>
</div>

<div class="card mb-2">
    <div class="card-header">
        <i class="bi bi-person me-1"></i>
        <?= sanitize($selectedStudent['first_name'] . ' ' . $selectedStudent['last_name']) ?>
        – <?= sanitize($selectedStudent['matric_number']) ?>
        (<?= sanitize($selectedStudent['dept_name']) ?>)
    </div>
</div>

<?php foreach ($gradesBySession as $sessionData): ?>
<div class="card mb-3">
    <div class="card-header d-flex justify-content-between align-items-center">
        <span>
            <i class="bi bi-calendar3 me-1"></i>
            <?= sanitize($sessionData['session']['session_name']) ?>
            – <?= ucfirst(sanitize($sessionData['session']['semester'])) ?> Semester
        </span>
        <span>
            Session GPA:
            <strong class="text-primary fs-5"><?= number_format($sessionData['gpa'], 2) ?></strong>
        </span>
    </div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-sm mb-0">
                <thead>
                <tr>
                    <th>Course Code</th><th>Course Title</th>
                    <th>Credit Units</th><th>Score</th>
                    <th>Grade</th><th>Points</th>
                    <th>Weighted (P×U)</th>
                </tr>
                </thead>
                <tbody>
                <?php
                $sessionUnits    = 0;
                $sessionWeighted = 0.0;
                foreach ($sessionData['rows'] as $row):
                    $weighted = (float)$row['grade_points'] * (int)$row['credit_units'];
                    $sessionUnits    += (int)$row['credit_units'];
                    $sessionWeighted += $weighted;
                    $bc = ['A'=>'success','B'=>'primary','C'=>'warning','D'=>'secondary','F'=>'danger'][$row['letter_grade']] ?? 'secondary';
                ?>
                <tr>
                    <td><strong><?= sanitize($row['course_code']) ?></strong></td>
                    <td><?= sanitize($row['course_title']) ?></td>
                    <td class="text-center"><?= $row['credit_units'] ?></td>
                    <td><?= number_format((float)$row['total_score'], 1) ?></td>
                    <td><span class="badge bg-<?= $bc ?>"><?= sanitize($row['letter_grade']) ?></span></td>
                    <td><?= number_format((float)$row['grade_points'], 1) ?></td>
                    <td><?= number_format($weighted, 1) ?></td>
                </tr>
                <?php endforeach; ?>
                </tbody>
                <tfoot class="table-light fw-bold">
                <tr>
                    <td colspan="2" class="text-end">Session Total</td>
                    <td class="text-center"><?= $sessionUnits ?></td>
                    <td colspan="2"></td>
                    <td></td>
                    <td><?= number_format($sessionWeighted, 1) ?></td>
                </tr>
                <tr>
                    <td colspan="6" class="text-end">GPA = <?= number_format($sessionWeighted, 1) ?> / <?= $sessionUnits ?> =</td>
                    <td class="text-primary"><?= number_format($sessionData['gpa'], 2) ?></td>
                </tr>
                </tfoot>
            </table>
        </div>
    </div>
</div>
<?php endforeach; ?>

<?php elseif ($studentId && empty($gradesBySession)): ?>
<div class="alert alert-info">No grade records found for this student.</div>
<?php endif; ?>

<?php require_once __DIR__ . '/../../includes/footer.php'; ?>
