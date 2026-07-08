<?php
define('PAGE_TITLE', 'Add Course');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();
requireRole(['admin','registrar']);

$departments = getAllDepartments();
$errors      = [];
$formData    = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verifyCsrf();
    $fields = ['course_code','course_title','credit_units','department_id','level','semester','description','status'];
    foreach ($fields as $f) $formData[$f] = trim($_POST[$f] ?? '');

    if (empty($formData['course_code']))  $errors[] = 'Course code is required.';
    if (empty($formData['course_title'])) $errors[] = 'Course title is required.';
    if (empty($formData['department_id'])) $errors[] = 'Department is required.';

    $dup = db()->fetchOne('SELECT id FROM courses WHERE course_code = :c', [':c' => $formData['course_code']]);
    if ($dup) $errors[] = 'Course code already exists.';

    if (empty($errors)) {
        db()->execute(
            'INSERT INTO courses (course_code, course_title, credit_units, department_id, level, semester, description, status)
             VALUES (:code, :title, :units, :dept, :level, :sem, :desc, :status)',
            [
                ':code'   => strtoupper($formData['course_code']),
                ':title'  => $formData['course_title'],
                ':units'  => max(1, (int)$formData['credit_units']),
                ':dept'   => (int)$formData['department_id'],
                ':level'  => $formData['level'],
                ':sem'    => $formData['semester'],
                ':desc'   => $formData['description'] ?: null,
                ':status' => $formData['status'] ?: 'active',
            ]
        );
        logAudit($_SESSION['user_id'], 'ADD_COURSE', 'courses', "Added course {$formData['course_code']}");
        flashMessage('success', "Course {$formData['course_code']} added successfully.");
        redirect(BASE_URL . '/modules/courses/index.php');
    }
}

$breadcrumbs = ['Courses' => BASE_URL . '/modules/courses/index.php', 'Add Course' => null];
require_once __DIR__ . '/../../includes/header.php';
?>

<h4 class="page-title"><i class="bi bi-plus-circle me-2"></i>Add New Course</h4>

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
                    <label class="form-label">Course Code <span class="text-danger">*</span></label>
                    <input type="text" name="course_code" class="form-control text-uppercase"
                           value="<?= sanitize($formData['course_code'] ?? '') ?>" required>
                </div>
                <div class="col-md-8">
                    <label class="form-label">Course Title <span class="text-danger">*</span></label>
                    <input type="text" name="course_title" class="form-control"
                           value="<?= sanitize($formData['course_title'] ?? '') ?>" required>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Department <span class="text-danger">*</span></label>
                    <select name="department_id" class="form-select" required>
                        <option value="">Select</option>
                        <?php foreach ($departments as $d): ?>
                        <option value="<?= $d['id'] ?>"
                            <?= ($formData['department_id'] ?? '') == $d['id'] ? 'selected' : '' ?>>
                            <?= sanitize($d['name']) ?>
                        </option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="col-md-3">
                    <label class="form-label">Level</label>
                    <select name="level" class="form-select">
                        <?php foreach (['100','200','300','400','500'] as $l): ?>
                        <option value="<?= $l ?>" <?= ($formData['level'] ?? '') === $l ? 'selected' : '' ?>>
                            <?= $l ?>L
                        </option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="col-md-3">
                    <label class="form-label">Semester</label>
                    <select name="semester" class="form-select">
                        <option value="first" <?= ($formData['semester'] ?? '') === 'first' ? 'selected' : '' ?>>First</option>
                        <option value="second" <?= ($formData['semester'] ?? '') === 'second' ? 'selected' : '' ?>>Second</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <label class="form-label">Credit Units</label>
                    <input type="number" name="credit_units" class="form-control" min="1" max="6"
                           value="<?= sanitize($formData['credit_units'] ?? '2') ?>">
                </div>
                <div class="col-md-3">
                    <label class="form-label">Status</label>
                    <select name="status" class="form-select">
                        <option value="active" <?= ($formData['status'] ?? 'active') === 'active' ? 'selected' : '' ?>>Active</option>
                        <option value="inactive" <?= ($formData['status'] ?? '') === 'inactive' ? 'selected' : '' ?>>Inactive</option>
                    </select>
                </div>
                <div class="col-12">
                    <label class="form-label">Description</label>
                    <textarea name="description" class="form-control" rows="2"><?= sanitize($formData['description'] ?? '') ?></textarea>
                </div>
                <div class="col-12 d-flex gap-2">
                    <button type="submit" class="btn btn-primary">
                        <i class="bi bi-check-lg me-1"></i>Save Course
                    </button>
                    <a href="<?= BASE_URL ?>/modules/courses/index.php" class="btn btn-outline-secondary">Cancel</a>
                </div>
            </div>
        </form>
    </div>
</div>

<?php require_once __DIR__ . '/../../includes/footer.php'; ?>
