<?php
define('PAGE_TITLE', 'Edit Course');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();
requireRole(['admin','registrar']);

$id = (int)($_GET['id'] ?? 0);
$course = db()->fetchOne('SELECT * FROM courses WHERE id = :id', [':id' => $id]);
if (!$course) {
    flashMessage('danger', 'Course not found.');
    redirect(BASE_URL . '/modules/courses/index.php');
}

$departments = getAllDepartments();
$errors   = [];
$formData = $course;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verifyCsrf();
    $fields = ['course_code','course_title','credit_units','department_id','level','semester','description','status'];
    foreach ($fields as $f) $formData[$f] = trim($_POST[$f] ?? '');

    if (empty($formData['course_code']))   $errors[] = 'Course code is required.';
    if (empty($formData['course_title']))  $errors[] = 'Course title is required.';

    $dup = db()->fetchOne(
        'SELECT id FROM courses WHERE course_code = :c AND id != :id',
        [':c' => strtoupper($formData['course_code']), ':id' => $id]
    );
    if ($dup) $errors[] = 'Course code already in use.';

    if (empty($errors)) {
        db()->execute(
            'UPDATE courses SET course_code=:code, course_title=:title, credit_units=:units,
             department_id=:dept, level=:level, semester=:sem, description=:desc, status=:status
             WHERE id=:id',
            [
                ':code'   => strtoupper($formData['course_code']),
                ':title'  => $formData['course_title'],
                ':units'  => max(1, (int)$formData['credit_units']),
                ':dept'   => (int)$formData['department_id'],
                ':level'  => $formData['level'],
                ':sem'    => $formData['semester'],
                ':desc'   => $formData['description'] ?: null,
                ':status' => $formData['status'],
                ':id'     => $id,
            ]
        );
        logAudit($_SESSION['user_id'], 'EDIT_COURSE', 'courses', "Updated course {$formData['course_code']}");
        flashMessage('success', 'Course updated.');
        redirect(BASE_URL . '/modules/courses/index.php');
    }
}

$breadcrumbs = ['Courses' => BASE_URL . '/modules/courses/index.php', 'Edit' => null];
require_once __DIR__ . '/../../includes/header.php';
?>
<h4 class="page-title"><i class="bi bi-pencil me-2"></i>Edit Course</h4>

<?php if (!empty($errors)): ?>
<div class="alert alert-danger"><ul class="mb-0">
    <?php foreach ($errors as $e): ?><li><?= sanitize($e) ?></li><?php endforeach; ?>
</ul></div>
<?php endif; ?>

<div class="card" style="max-width:700px;">
    <div class="card-body">
        <form method="POST" novalidate>
            <input type="hidden" name="csrf_token" value="<?= htmlspecialchars($_SESSION['csrf_token']) ?>">
            <div class="row g-3">
                <div class="col-md-4">
                    <label class="form-label">Course Code</label>
                    <input type="text" name="course_code" class="form-control text-uppercase"
                           value="<?= sanitize($formData['course_code']) ?>">
                </div>
                <div class="col-md-8">
                    <label class="form-label">Course Title</label>
                    <input type="text" name="course_title" class="form-control"
                           value="<?= sanitize($formData['course_title']) ?>">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Department</label>
                    <select name="department_id" class="form-select">
                        <?php foreach ($departments as $d): ?>
                        <option value="<?= $d['id'] ?>"
                            <?= $formData['department_id'] == $d['id'] ? 'selected' : '' ?>>
                            <?= sanitize($d['name']) ?>
                        </option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="col-md-3">
                    <label class="form-label">Level</label>
                    <select name="level" class="form-select">
                        <?php foreach (['100','200','300','400','500'] as $l): ?>
                        <option value="<?= $l ?>" <?= $formData['level'] === $l ? 'selected' : '' ?>><?= $l ?>L</option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="col-md-3">
                    <label class="form-label">Semester</label>
                    <select name="semester" class="form-select">
                        <option value="first"  <?= $formData['semester'] === 'first'  ? 'selected' : '' ?>>First</option>
                        <option value="second" <?= $formData['semester'] === 'second' ? 'selected' : '' ?>>Second</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <label class="form-label">Credits</label>
                    <input type="number" name="credit_units" class="form-control" min="1" max="6"
                           value="<?= (int)$formData['credit_units'] ?>">
                </div>
                <div class="col-md-3">
                    <label class="form-label">Status</label>
                    <select name="status" class="form-select">
                        <option value="active"   <?= $formData['status'] === 'active'   ? 'selected' : '' ?>>Active</option>
                        <option value="inactive" <?= $formData['status'] === 'inactive' ? 'selected' : '' ?>>Inactive</option>
                    </select>
                </div>
                <div class="col-12">
                    <label class="form-label">Description</label>
                    <textarea name="description" class="form-control" rows="2"><?= sanitize($formData['description'] ?? '') ?></textarea>
                </div>
                <div class="col-12 d-flex gap-2">
                    <button type="submit" class="btn btn-primary"><i class="bi bi-check-lg me-1"></i>Update</button>
                    <a href="<?= BASE_URL ?>/modules/courses/index.php" class="btn btn-outline-secondary">Cancel</a>
                </div>
            </div>
        </form>
    </div>
</div>

<?php require_once __DIR__ . '/../../includes/footer.php'; ?>
