<?php
// ============================================================
// SRMS – Grade Entry
// ============================================================
define('PAGE_TITLE', 'Grade Entry');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();
requireRole(['admin','registrar','teacher']);

$sessions = getAllSessions();
$currentSession = getCurrentSession();

$selectedSession = (int)($_GET['session_id'] ?? ($currentSession['id'] ?? 0));
$selectedCourse  = (int)($_GET['course_id'] ?? 0);

// Courses for selected session
$courses = db()->fetchAll(
    'SELECT DISTINCT c.id, c.course_code, c.course_title, c.credit_units
     FROM courses c
     JOIN student_courses sc ON sc.course_id = c.id AND sc.session_id = :s
     ORDER BY c.course_code',
    [':s' => $selectedSession]
);

// Students enrolled in selected course
$enrolledStudents = [];
if ($selectedCourse && $selectedSession) {
    $enrolledStudents = db()->fetchAll(
        'SELECT s.id, s.matric_number, s.first_name, s.last_name,
                g.ca_score, g.exam_score, g.total_score, g.letter_grade, g.grade_points
         FROM student_courses sc
         JOIN students s ON s.id = sc.student_id
         LEFT JOIN grades g ON g.student_id = sc.student_id
             AND g.course_id = sc.course_id AND g.session_id = sc.session_id
         WHERE sc.course_id = :c AND sc.session_id = :s
         ORDER BY s.last_name, s.first_name',
        [':c' => $selectedCourse, ':s' => $selectedSession]
    );
}

// Handle POST – batch grade save
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['save_grades'])) {
    verifyCsrf();

    $postSessionId = (int)$_POST['session_id'];
    $postCourseId  = (int)$_POST['course_id'];

    // Fetch credit units for this course
    $courseInfo = db()->fetchOne('SELECT credit_units FROM courses WHERE id = :id', [':id' => $postCourseId]);
    $creditUnits = $courseInfo ? (int)$courseInfo['credit_units'] : 2;

    $studentIds = $_POST['student_id'] ?? [];
    $caScores   = $_POST['ca_score']   ?? [];
    $examScores = $_POST['exam_score'] ?? [];

    db()->beginTransaction();
    try {
        foreach ($studentIds as $idx => $studentId) {
            $studentId = (int)$studentId;
            $ca   = min(MAX_CA_SCORE,   max(0, (float)($caScores[$idx]   ?? 0)));
            $exam = min(MAX_EXAM_SCORE,  max(0, (float)($examScores[$idx] ?? 0)));
            $total = $ca + $exam;
            $gradeInfo = getLetterGrade($total);

            db()->execute(
                'INSERT INTO grades (student_id, course_id, session_id, ca_score, exam_score,
                 letter_grade, grade_points, credit_units, entered_by)
                 VALUES (:sid, :cid, :sess, :ca, :exam, :lg, :gp, :cu, :eby)
                 ON DUPLICATE KEY UPDATE
                    ca_score=VALUES(ca_score), exam_score=VALUES(exam_score),
                    letter_grade=VALUES(letter_grade), grade_points=VALUES(grade_points),
                    credit_units=VALUES(credit_units), entered_by=VALUES(entered_by)',
                [
                    ':sid'  => $studentId,
                    ':cid'  => $postCourseId,
                    ':sess' => $postSessionId,
                    ':ca'   => $ca,
                    ':exam' => $exam,
                    ':lg'   => $gradeInfo['letter'],
                    ':gp'   => $gradeInfo['points'],
                    ':cu'   => $creditUnits,
                    ':eby'  => $_SESSION['user_id'],
                ]
            );
        }
        db()->commit();

        $courseName = '';
        foreach ($courses as $c) {
            if ($c['id'] == $postCourseId) { $courseName = $c['course_code']; break; }
        }
        logAudit($_SESSION['user_id'], 'GRADE_ENTRY', 'grades',
            "Entered grades for course {$courseName} – session ID {$postSessionId}");
        flashMessage('success', 'Grades saved successfully.');
        redirect(BASE_URL . '/modules/grades/entry.php?session_id=' . $postSessionId . '&course_id=' . $postCourseId);
    } catch (PDOException $e) {
        db()->rollback();
        flashMessage('danger', 'Error saving grades: ' . $e->getMessage());
    }
}

$breadcrumbs = ['Grades' => BASE_URL . '/modules/grades/index.php', 'Entry' => null];
require_once __DIR__ . '/../../includes/header.php';
?>

<h4 class="page-title"><i class="bi bi-pencil-square me-2"></i>Grade Entry</h4>

<!-- Step 1 – Select course/session -->
<div class="card mb-3">
    <div class="card-header"><i class="bi bi-filter me-1"></i>Select Course &amp; Session</div>
    <div class="card-body">
        <form method="GET" class="row g-3 align-items-end">
            <div class="col-sm-4">
                <label class="form-label">Academic Session</label>
                <select name="session_id" class="form-select" required>
                    <?php foreach ($sessions as $sess): ?>
                    <option value="<?= $sess['id'] ?>"
                        <?= $selectedSession == $sess['id'] ? 'selected' : '' ?>>
                        <?= sanitize($sess['session_name']) ?> (<?= ucfirst($sess['semester']) ?>)
                    </option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-sm-5">
                <label class="form-label">Course</label>
                <select name="course_id" class="form-select" required>
                    <option value="">Select a course</option>
                    <?php foreach ($courses as $c): ?>
                    <option value="<?= $c['id'] ?>" <?= $selectedCourse == $c['id'] ? 'selected' : '' ?>>
                        <?= sanitize($c['course_code']) ?> – <?= sanitize($c['course_title']) ?>
                        (<?= $c['credit_units'] ?> units)
                    </option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-auto">
                <button type="submit" class="btn btn-primary">
                    <i class="bi bi-table me-1"></i>Load Students
                </button>
            </div>
        </form>
    </div>
</div>

<?php if ($selectedCourse && $selectedSession): ?>
<?php
$selectedCourseInfo = null;
foreach ($courses as $c) {
    if ($c['id'] == $selectedCourse) { $selectedCourseInfo = $c; break; }
}
?>

<div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
        <span>
            <i class="bi bi-table me-1"></i>
            <?php if ($selectedCourseInfo): ?>
            Grades for <strong><?= sanitize($selectedCourseInfo['course_code']) ?></strong>
            – <?= sanitize($selectedCourseInfo['course_title']) ?>
            <?php endif; ?>
        </span>
        <small class="text-muted"><?= count($enrolledStudents) ?> students enrolled</small>
    </div>
    <div class="card-body p-0">
        <?php if (empty($enrolledStudents)): ?>
        <div class="p-4 text-center text-muted">No students enrolled in this course for the selected session.</div>
        <?php else: ?>
        <form method="POST" id="gradeForm">
            <input type="hidden" name="csrf_token" value="<?= htmlspecialchars($_SESSION['csrf_token']) ?>">
            <input type="hidden" name="save_grades" value="1">
            <input type="hidden" name="session_id" value="<?= $selectedSession ?>">
            <input type="hidden" name="course_id" value="<?= $selectedCourse ?>">

            <div class="table-responsive">
                <table class="table table-sm table-hover mb-0 align-middle">
                    <thead>
                    <tr>
                        <th>#</th>
                        <th>Matric No.</th>
                        <th>Student Name</th>
                        <th>CA Score <small class="text-muted">(max <?= MAX_CA_SCORE ?>)</small></th>
                        <th>Exam Score <small class="text-muted">(max <?= MAX_EXAM_SCORE ?>)</small></th>
                        <th>Total (100)</th>
                        <th>Letter Grade</th>
                        <th>Grade Points</th>
                    </tr>
                    </thead>
                    <tbody>
                    <?php foreach ($enrolledStudents as $i => $s): ?>
                    <tr>
                        <td><?= $i + 1 ?></td>
                        <td><?= sanitize($s['matric_number']) ?></td>
                        <td><?= sanitize($s['last_name'] . ', ' . $s['first_name']) ?></td>
                        <td>
                            <input type="hidden" name="student_id[]" value="<?= $s['id'] ?>">
                            <input type="number" name="ca_score[]"
                                   class="form-control form-control-sm grade-input ca-score"
                                   min="0" max="<?= MAX_CA_SCORE ?>" step="0.5"
                                   value="<?= $s['ca_score'] !== null ? number_format((float)$s['ca_score'], 1) : '' ?>"
                                   placeholder="0">
                        </td>
                        <td>
                            <input type="number" name="exam_score[]"
                                   class="form-control form-control-sm grade-input exam-score"
                                   min="0" max="<?= MAX_EXAM_SCORE ?>" step="0.5"
                                   value="<?= $s['exam_score'] !== null ? number_format((float)$s['exam_score'], 1) : '' ?>"
                                   placeholder="0">
                        </td>
                        <td><strong class="total-score">
                            <?= $s['total_score'] !== null ? number_format((float)$s['total_score'], 1) : '–' ?>
                        </strong></td>
                        <td>
                            <?php
                            $badgeMap = ['A'=>'success','B'=>'primary','C'=>'warning','D'=>'secondary','F'=>'danger'];
                            $lg = $s['letter_grade'] ?? '–';
                            $bc = $badgeMap[$lg] ?? 'secondary';
                            ?>
                            <span class="badge bg-<?= $bc ?> letter-grade"><?= sanitize($lg) ?></span>
                        </td>
                        <td><span class="grade-points">
                            <?= $s['grade_points'] !== null ? number_format((float)$s['grade_points'], 1) : '–' ?>
                        </span></td>
                    </tr>
                    <?php endforeach; ?>
                    </tbody>
                </table>
            </div>

            <div class="p-3 border-top d-flex gap-2">
                <button type="submit" class="btn btn-success px-4">
                    <i class="bi bi-save me-1"></i>Save All Grades
                </button>
                <a href="<?= BASE_URL ?>/modules/grades/index.php?session_id=<?= $selectedSession ?>"
                   class="btn btn-outline-secondary">View Grade Sheet</a>
            </div>
        </form>
        <?php endif; ?>
    </div>
</div>
<?php endif; ?>

<?php require_once __DIR__ . '/../../includes/footer.php'; ?>
