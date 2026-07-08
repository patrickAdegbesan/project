<?php
define('PAGE_TITLE', 'Mark Attendance');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();
requireRole(['admin','registrar','teacher']);

$sessions       = getAllSessions();
$currentSession = getCurrentSession();

$selectedSession = (int)($_GET['session_id'] ?? ($currentSession['id'] ?? 0));
$selectedCourse  = (int)($_GET['course_id'] ?? 0);
$selectedDate    = sanitize($_GET['date'] ?? date('Y-m-d'));

// Courses for selected session
$courses = db()->fetchAll(
    'SELECT DISTINCT c.id, c.course_code, c.course_title
     FROM courses c
     JOIN student_courses sc ON sc.course_id = c.id AND sc.session_id = :s
     ORDER BY c.course_code',
    [':s' => $selectedSession]
);

// Students enrolled
$enrolledStudents = [];
if ($selectedCourse && $selectedSession) {
    $enrolledStudents = db()->fetchAll(
        'SELECT s.id, s.matric_number, s.first_name, s.last_name,
                a.status AS existing_status, a.remarks AS existing_remarks
         FROM student_courses sc
         JOIN students s ON s.id = sc.student_id
         LEFT JOIN attendance a ON a.student_id = sc.student_id
             AND a.course_id = sc.course_id
             AND a.session_id = sc.session_id
             AND a.date = :d
         WHERE sc.course_id = :c AND sc.session_id = :s
         ORDER BY s.last_name, s.first_name',
        [':d' => $selectedDate, ':c' => $selectedCourse, ':s' => $selectedSession]
    );
}

// Save attendance
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['save_attendance'])) {
    verifyCsrf();

    $postSession = (int)$_POST['session_id'];
    $postCourse  = (int)$_POST['course_id'];
    $postDate    = $_POST['att_date'] ?? date('Y-m-d');
    $studentIds  = $_POST['student_id'] ?? [];
    $statuses    = $_POST['att_status'] ?? [];
    $remarks     = $_POST['remarks']    ?? [];

    db()->beginTransaction();
    try {
        foreach ($studentIds as $idx => $sid) {
            $sid    = (int)$sid;
            $status = in_array($statuses[$idx] ?? '', ['present','absent','late','excused'])
                      ? $statuses[$idx] : 'absent';
            $remark = trim($remarks[$idx] ?? '');

            db()->execute(
                'INSERT INTO attendance (student_id, course_id, session_id, date, status, remarks, marked_by)
                 VALUES (:s, :c, :ss, :d, :st, :r, :mb)
                 ON DUPLICATE KEY UPDATE status=VALUES(status), remarks=VALUES(remarks), marked_by=VALUES(marked_by)',
                [
                    ':s'  => $sid,
                    ':c'  => $postCourse,
                    ':ss' => $postSession,
                    ':d'  => $postDate,
                    ':st' => $status,
                    ':r'  => $remark ?: null,
                    ':mb' => $_SESSION['user_id'],
                ]
            );
        }
        db()->commit();
        logAudit($_SESSION['user_id'], 'MARK_ATTENDANCE', 'attendance',
            "Marked attendance for course ID {$postCourse} on {$postDate}");
        flashMessage('success', 'Attendance saved successfully.');
        redirect(BASE_URL . "/modules/attendance/mark.php?session_id={$postSession}&course_id={$postCourse}&date={$postDate}");
    } catch (PDOException $e) {
        db()->rollback();
        flashMessage('danger', 'Error saving attendance: ' . $e->getMessage());
    }
}

$breadcrumbs = ['Attendance' => BASE_URL . '/modules/attendance/index.php', 'Mark' => null];
require_once __DIR__ . '/../../includes/header.php';
?>

<h4 class="page-title"><i class="bi bi-check2-all me-2"></i>Mark Attendance</h4>

<!-- Selection -->
<div class="card mb-3">
    <div class="card-header"><i class="bi bi-filter me-1"></i>Select Course &amp; Date</div>
    <div class="card-body">
        <form method="GET" class="row g-3 align-items-end">
            <div class="col-sm-3">
                <label class="form-label">Session</label>
                <select name="session_id" class="form-select">
                    <?php foreach ($sessions as $s): ?>
                    <option value="<?= $s['id'] ?>" <?= $selectedSession == $s['id'] ? 'selected' : '' ?>>
                        <?= sanitize($s['session_name']) ?>
                    </option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-sm-4">
                <label class="form-label">Course</label>
                <select name="course_id" class="form-select">
                    <option value="">Select course</option>
                    <?php foreach ($courses as $c): ?>
                    <option value="<?= $c['id'] ?>" <?= $selectedCourse == $c['id'] ? 'selected' : '' ?>>
                        <?= sanitize($c['course_code']) ?> – <?= sanitize($c['course_title']) ?>
                    </option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-sm-3">
                <label class="form-label">Date</label>
                <input type="date" name="date" class="form-control" value="<?= sanitize($selectedDate) ?>">
            </div>
            <div class="col-auto">
                <button type="submit" class="btn btn-primary">Load</button>
            </div>
        </form>
    </div>
</div>

<?php if ($selectedCourse && !empty($enrolledStudents)): ?>
<div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
        <span>
            Attendance for
            <strong><?= sanitize(($courses[array_search($selectedCourse, array_column($courses, 'id'))] ?? [])['course_code'] ?? '') ?></strong>
            on <?= date('d M Y', strtotime($selectedDate)) ?>
        </span>
        <div class="d-flex gap-2 no-print">
            <button type="button" class="btn btn-sm btn-success" onclick="markAll('present')">All Present</button>
            <button type="button" class="btn btn-sm btn-danger" onclick="markAll('absent')">All Absent</button>
        </div>
    </div>
    <div class="card-body p-0">
        <form method="POST">
            <input type="hidden" name="csrf_token" value="<?= htmlspecialchars($_SESSION['csrf_token']) ?>">
            <input type="hidden" name="save_attendance" value="1">
            <input type="hidden" name="session_id" value="<?= $selectedSession ?>">
            <input type="hidden" name="course_id" value="<?= $selectedCourse ?>">
            <input type="hidden" name="att_date" value="<?= sanitize($selectedDate) ?>">

            <div class="table-responsive">
                <table class="table table-hover table-sm mb-0">
                    <thead>
                    <tr>
                        <th>#</th>
                        <th>Matric No.</th>
                        <th>Student Name</th>
                        <th>Present</th>
                        <th>Absent</th>
                        <th>Late</th>
                        <th>Excused</th>
                        <th>Remarks</th>
                    </tr>
                    </thead>
                    <tbody>
                    <?php foreach ($enrolledStudents as $i => $s): ?>
                    <?php $existing = $s['existing_status'] ?? 'present'; ?>
                    <tr>
                        <td><?= $i + 1 ?></td>
                        <td><?= sanitize($s['matric_number']) ?></td>
                        <td><strong><?= sanitize($s['last_name'] . ', ' . $s['first_name']) ?></strong></td>
                        <td>
                            <input type="hidden" name="student_id[]" value="<?= $s['id'] ?>">
                            <div class="form-check">
                                <input class="form-check-input att-radio" type="radio"
                                       name="att_status[<?= $i ?>]" value="present"
                                       <?= $existing === 'present' ? 'checked' : '' ?>>
                            </div>
                        </td>
                        <td>
                            <div class="form-check">
                                <input class="form-check-input att-radio" type="radio"
                                       name="att_status[<?= $i ?>]" value="absent"
                                       <?= $existing === 'absent' ? 'checked' : '' ?>>
                            </div>
                        </td>
                        <td>
                            <div class="form-check">
                                <input class="form-check-input att-radio" type="radio"
                                       name="att_status[<?= $i ?>]" value="late"
                                       <?= $existing === 'late' ? 'checked' : '' ?>>
                            </div>
                        </td>
                        <td>
                            <div class="form-check">
                                <input class="form-check-input att-radio" type="radio"
                                       name="att_status[<?= $i ?>]" value="excused"
                                       <?= $existing === 'excused' ? 'checked' : '' ?>>
                            </div>
                        </td>
                        <td>
                            <input type="text" name="remarks[<?= $i ?>]" class="form-control form-control-sm"
                                   placeholder="Optional remark"
                                   value="<?= sanitize($s['existing_remarks'] ?? '') ?>">
                        </td>
                    </tr>
                    <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
            <div class="p-3 border-top">
                <button type="submit" class="btn btn-success px-4">
                    <i class="bi bi-save me-1"></i>Save Attendance
                </button>
            </div>
        </form>
    </div>
</div>

<script>
function markAll(status) {
    document.querySelectorAll('.att-radio[value="' + status + '"]').forEach(function(r) {
        r.checked = true;
    });
}
</script>

<?php elseif ($selectedCourse): ?>
<div class="alert alert-info">No students enrolled in this course for the selected session.</div>
<?php endif; ?>

<?php require_once __DIR__ . '/../../includes/footer.php'; ?>
