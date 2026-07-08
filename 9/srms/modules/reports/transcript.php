<?php
define('PAGE_TITLE', 'Academic Transcript');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();

$studentId = (int)($_GET['student_id'] ?? 0);
$students  = db()->fetchAll(
    'SELECT id, matric_number, first_name, last_name FROM students ORDER BY last_name'
);
$student        = null;
$sessionRecords = [];
$cgpa           = 0.0;

if ($studentId) {
    $student = getStudentById($studentId);
    if ($student) {
        $sessionsWithGrades = db()->fetchAll(
            'SELECT DISTINCT sess.* FROM grades g
             JOIN academic_sessions sess ON sess.id = g.session_id
             WHERE g.student_id = :s ORDER BY sess.id',
            [':s' => $studentId]
        );

        foreach ($sessionsWithGrades as $sess) {
            $grades = db()->fetchAll(
                'SELECT g.*, c.course_code, c.course_title, c.credit_units AS cu
                 FROM grades g JOIN courses c ON c.id = g.course_id
                 WHERE g.student_id = :s AND g.session_id = :ss ORDER BY c.course_code',
                [':s' => $studentId, ':ss' => $sess['id']]
            );
            $sessionRecords[] = [
                'session'      => $sess,
                'grades'       => $grades,
                'session_gpa'  => calculateGPA($studentId, (int)$sess['id']),
            ];
        }
        $cgpa = calculateCGPA($studentId);
    }
}

$isPrint = isset($_GET['print']);
if ($isPrint) {
    // Output bare HTML for print, no layout
    require_once __DIR__ . '/../../config/config.php';
    require_once __DIR__ . '/../../config/database.php';
    require_once __DIR__ . '/../../includes/functions.php';
}

if (!$isPrint) {
    $breadcrumbs = ['Reports' => BASE_URL . '/modules/reports/index.php', 'Transcript' => null];
    require_once __DIR__ . '/../../includes/header.php';
}
?>

<?php if (!$isPrint): ?>
<div class="d-flex justify-content-between align-items-center mb-3">
    <h4 class="page-title mb-0"><i class="bi bi-file-earmark-person me-2"></i>Academic Transcript</h4>
    <?php if ($student): ?>
    <button class="btn btn-outline-secondary btn-sm no-print" onclick="window.print()">
        <i class="bi bi-printer me-1"></i>Print Transcript
    </button>
    <?php endif; ?>
</div>

<!-- Student selector -->
<div class="card mb-3 no-print">
    <div class="card-body">
        <form method="GET" class="row g-3 align-items-end">
            <div class="col-sm-6">
                <label class="form-label">Select Student</label>
                <select name="student_id" class="form-select">
                    <option value="">-- Choose a student --</option>
                    <?php foreach ($students as $s): ?>
                    <option value="<?= $s['id'] ?>" <?= $studentId == $s['id'] ? 'selected' : '' ?>>
                        <?= sanitize($s['matric_number'] . ' – ' . $s['last_name'] . ', ' . $s['first_name']) ?>
                    </option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-auto">
                <button type="submit" class="btn btn-primary">Load Transcript</button>
            </div>
        </form>
    </div>
</div>
<?php endif; ?>

<?php if ($student): ?>
<!-- Transcript Body -->
<div class="transcript-body" id="transcriptBody">
    <!-- Header (visible when printed) -->
    <div class="transcript-header" style="text-align:center;margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:2px solid #1a237e;">
        <h3 class="mb-0"><?= INSTITUTION_NAME ?></h3>
        <h5 class="mb-0"><?= INSTITUTION_ADDRESS ?></h5>
        <hr style="border-color:#1a237e;margin:0.5rem auto;width:60%;">
        <h4 class="mt-2 mb-0"><strong>OFFICIAL ACADEMIC TRANSCRIPT</strong></h4>
    </div>

    <!-- Student header -->
    <div class="card mb-3">
        <div class="card-body">
            <div class="row">
                <div class="col-md-6">
                    <table class="table table-sm table-borderless mb-0">
                        <tr><th style="width:160px;" class="text-muted small">Student Name:</th>
                            <td><strong><?= sanitize($student['first_name'] . ' ' . ($student['middle_name'] ? $student['middle_name'] . ' ' : '') . $student['last_name']) ?></strong></td></tr>
                        <tr><th class="text-muted small">Matric Number:</th>
                            <td><?= sanitize($student['matric_number']) ?></td></tr>
                        <tr><th class="text-muted small">Department:</th>
                            <td><?= sanitize($student['dept_name']) ?></td></tr>
                        <tr><th class="text-muted small">Level:</th>
                            <td><?= sanitize($student['level']) ?>L</td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <table class="table table-sm table-borderless mb-0">
                        <tr><th style="width:160px;" class="text-muted small">Gender:</th>
                            <td><?= sanitize(ucfirst($student['gender'])) ?></td></tr>
                        <tr><th class="text-muted small">Admission Date:</th>
                            <td><?= formatDate($student['admission_date']) ?></td></tr>
                        <tr><th class="text-muted small">Status:</th>
                            <td><?= statusBadge($student['status']) ?></td></tr>
                        <tr><th class="text-muted small">CGPA:</th>
                            <td><strong class="text-primary fs-5"><?= number_format($cgpa, 2) ?></strong>
                                – <em><?= getClassStanding($cgpa) ?></em></td></tr>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- Grades by session -->
    <?php foreach ($sessionRecords as $record): ?>
    <div class="card mb-3">
        <div class="card-header d-flex justify-content-between">
            <span>
                <strong><?= sanitize($record['session']['session_name']) ?></strong>
                &nbsp;–&nbsp;<?= ucfirst(sanitize($record['session']['semester'])) ?> Semester
            </span>
            <span>Session GPA: <strong class="text-primary"><?= number_format($record['session_gpa'], 2) ?></strong></span>
        </div>
        <div class="card-body p-0">
            <table class="table table-sm table-bordered mb-0">
                <thead class="table-light">
                <tr>
                    <th>S/N</th>
                    <th>Course Code</th>
                    <th>Course Title</th>
                    <th class="text-center">Credit Units</th>
                    <th class="text-center">CA</th>
                    <th class="text-center">Exam</th>
                    <th class="text-center">Total</th>
                    <th class="text-center">Grade</th>
                    <th class="text-center">Points</th>
                    <th class="text-center">Weighted</th>
                </tr>
                </thead>
                <tbody>
                <?php
                $sUnits = 0; $sWeighted = 0.0;
                foreach ($record['grades'] as $idx => $g):
                    $weighted = (float)$g['grade_points'] * (int)$g['credit_units'];
                    $sUnits    += (int)$g['credit_units'];
                    $sWeighted += $weighted;
                    $bc = ['A'=>'success','B'=>'primary','C'=>'warning','D'=>'secondary','F'=>'danger'][$g['letter_grade']] ?? 'secondary';
                ?>
                <tr>
                    <td><?= $idx + 1 ?></td>
                    <td><strong><?= sanitize($g['course_code']) ?></strong></td>
                    <td><?= sanitize($g['course_title']) ?></td>
                    <td class="text-center"><?= $g['credit_units'] ?></td>
                    <td class="text-center"><?= number_format((float)$g['ca_score'], 1) ?></td>
                    <td class="text-center"><?= number_format((float)$g['exam_score'], 1) ?></td>
                    <td class="text-center"><strong><?= number_format((float)$g['total_score'], 1) ?></strong></td>
                    <td class="text-center">
                        <span class="badge bg-<?= $bc ?>"><?= sanitize($g['letter_grade']) ?></span>
                    </td>
                    <td class="text-center"><?= number_format((float)$g['grade_points'], 1) ?></td>
                    <td class="text-center"><?= number_format($weighted, 1) ?></td>
                </tr>
                <?php endforeach; ?>
                </tbody>
                <tfoot class="table-light fw-bold">
                <tr>
                    <td colspan="3" class="text-end">Session Total</td>
                    <td class="text-center"><?= $sUnits ?></td>
                    <td colspan="5"></td>
                    <td class="text-center"><?= number_format($sWeighted, 1) ?></td>
                </tr>
                <tr>
                    <td colspan="8" class="text-end">
                        Session GPA = <?= number_format($sWeighted, 1) ?> / <?= $sUnits ?> =
                    </td>
                    <td colspan="2" class="text-center text-primary">
                        <?= number_format($record['session_gpa'], 2) ?>
                    </td>
                </tr>
                </tfoot>
            </table>
        </div>
    </div>
    <?php endforeach; ?>

    <?php if (empty($sessionRecords)): ?>
    <div class="alert alert-info">No academic records found for this student.</div>
    <?php endif; ?>

    <!-- CGPA Summary -->
    <div class="card border-primary">
        <div class="card-body d-flex justify-content-between align-items-center">
            <div>
                <h5 class="mb-0 fw-bold">Cumulative GPA (CGPA)</h5>
                <small class="text-muted">Based on all <?= count($sessionRecords) ?> recorded session(s)</small>
            </div>
            <div class="text-end">
                <div class="fw-bold fs-3 text-primary"><?= number_format($cgpa, 2) ?></div>
                <div class="badge bg-primary fs-6"><?= getClassStanding($cgpa) ?></div>
            </div>
        </div>
    </div>

    <!-- Grading key -->
    <div class="card mt-3">
        <div class="card-header small fw-bold">Grading Key</div>
        <div class="card-body py-2">
            <table class="table table-sm table-bordered mb-0" style="max-width:500px;">
                <thead><tr><th>Score Range</th><th>Letter Grade</th><th>Grade Points</th><th>Remark</th></tr></thead>
                <tbody>
                <tr><td>70 – 100</td><td><span class="badge bg-success">A</span></td><td>4.0</td><td>Excellent</td></tr>
                <tr><td>60 – 69</td><td><span class="badge bg-primary">B</span></td><td>3.0</td><td>Very Good</td></tr>
                <tr><td>50 – 59</td><td><span class="badge bg-warning text-dark">C</span></td><td>2.0</td><td>Good</td></tr>
                <tr><td>45 – 49</td><td><span class="badge bg-secondary">D</span></td><td>1.0</td><td>Pass</td></tr>
                <tr><td>0 – 44</td><td><span class="badge bg-danger">F</span></td><td>0.0</td><td>Fail</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <!-- Signature block (shows on print) -->
    <div class="print-signature-block mt-5">
        <div class="print-signature-line">Registrar's Signature &amp; Date</div>
        <div class="print-signature-line">Registry Stamp</div>
    </div>
</div>
<?php endif; ?>

<?php if (!$isPrint): require_once __DIR__ . '/../../includes/footer.php'; endif; ?>
