<?php
define('PAGE_TITLE', 'Grades');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();
requireRole(['admin','registrar','teacher']);

$sessions    = getAllSessions();
$departments = getAllDepartments();
$currentSession = getCurrentSession();

$filterSession = (int)($_GET['session_id'] ?? ($currentSession['id'] ?? 0));
$filterCourse  = (int)($_GET['course_id'] ?? 0);

// Get courses for selected session
$courses = db()->fetchAll(
    'SELECT DISTINCT c.id, c.course_code, c.course_title
     FROM courses c
     JOIN student_courses sc ON sc.course_id = c.id AND sc.session_id = :s
     ORDER BY c.course_code',
    [':s' => $filterSession]
);

// Grade records
$where  = ['g.session_id = :sess'];
$params = [':sess' => $filterSession];
if ($filterCourse) {
    $where[]         = 'g.course_id = :course';
    $params[':course'] = $filterCourse;
}

$grades = db()->fetchAll(
    'SELECT g.*, s.matric_number, s.first_name, s.last_name, d.code AS dept_code,
            c.course_code, c.course_title, c.credit_units AS course_credits
     FROM grades g
     JOIN students s ON s.id = g.student_id
     JOIN departments d ON d.id = s.department_id
     JOIN courses c ON c.id = g.course_id
     WHERE ' . implode(' AND ', $where) . '
     ORDER BY c.course_code, s.last_name',
    $params
);

$breadcrumbs = ['Grades' => null];
require_once __DIR__ . '/../../includes/header.php';
?>

<div class="d-flex justify-content-between align-items-center mb-3">
    <h4 class="page-title mb-0"><i class="bi bi-bar-chart me-2"></i>Grade Records</h4>
    <?php if (in_array($_SESSION['user_role'], ['admin','registrar','teacher'])): ?>
    <a href="<?= BASE_URL ?>/modules/grades/entry.php" class="btn btn-primary">
        <i class="bi bi-pencil-square me-1"></i>Enter Grades
    </a>
    <?php endif; ?>
</div>

<!-- Filter -->
<div class="card mb-3">
    <div class="card-body py-2">
        <form method="GET" class="row g-2 align-items-end">
            <div class="col-sm-4">
                <label class="form-label small mb-1">Academic Session</label>
                <select name="session_id" class="form-select form-select-sm">
                    <?php foreach ($sessions as $sess): ?>
                    <option value="<?= $sess['id'] ?>"
                        <?= $filterSession == $sess['id'] ? 'selected' : '' ?>>
                        <?= sanitize($sess['session_name']) ?> – <?= ucfirst($sess['semester']) ?>
                    </option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-sm-4">
                <label class="form-label small mb-1">Course</label>
                <select name="course_id" class="form-select form-select-sm">
                    <option value="">All Courses</option>
                    <?php foreach ($courses as $c): ?>
                    <option value="<?= $c['id'] ?>" <?= $filterCourse == $c['id'] ? 'selected' : '' ?>>
                        <?= sanitize($c['course_code']) ?> – <?= sanitize($c['course_title']) ?>
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
                    <th>Matric No.</th><th>Student Name</th><th>Dept</th>
                    <th>Course</th><th>CA (30)</th><th>Exam (70)</th>
                    <th>Total</th><th>Grade</th><th>Points</th><th>Units</th>
                </tr>
                </thead>
                <tbody>
                <?php foreach ($grades as $g): ?>
                <tr>
                    <td><?= sanitize($g['matric_number']) ?></td>
                    <td><?= sanitize($g['last_name'] . ', ' . $g['first_name']) ?></td>
                    <td><?= sanitize($g['dept_code']) ?></td>
                    <td><?= sanitize($g['course_code']) ?></td>
                    <td><?= number_format((float)$g['ca_score'], 1) ?></td>
                    <td><?= number_format((float)$g['exam_score'], 1) ?></td>
                    <td><strong><?= number_format((float)$g['total_score'], 1) ?></strong></td>
                    <td>
                        <span class="badge bg-<?= ['A'=>'success','B'=>'primary','C'=>'warning','D'=>'secondary','F'=>'danger'][$g['letter_grade']] ?? 'secondary' ?>">
                            <?= sanitize($g['letter_grade']) ?>
                        </span>
                    </td>
                    <td><?= number_format((float)$g['grade_points'], 1) ?></td>
                    <td><?= $g['credit_units'] ?></td>
                </tr>
                <?php endforeach; ?>
                <?php if (empty($grades)): ?>
                <tr><td colspan="10" class="text-center text-muted py-4">No grade records found.</td></tr>
                <?php endif; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>

<?php require_once __DIR__ . '/../../includes/footer.php'; ?>
