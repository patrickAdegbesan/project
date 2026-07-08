<?php
define('PAGE_TITLE', 'Courses');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();
requireRole(['admin','registrar','teacher']);

$departments = getAllDepartments();
$filterDept  = (int)($_GET['dept'] ?? 0);
$filterLevel = sanitize($_GET['level'] ?? '');
$filterSem   = sanitize($_GET['semester'] ?? '');

$where  = ['1=1'];
$params = [];
if ($filterDept)  { $where[] = 'c.department_id = :dept'; $params[':dept'] = $filterDept; }
if ($filterLevel) { $where[] = 'c.level = :level';         $params[':level'] = $filterLevel; }
if ($filterSem)   { $where[] = 'c.semester = :sem';        $params[':sem'] = $filterSem; }

$courses = db()->fetchAll(
    'SELECT c.*, d.name AS dept_name, d.code AS dept_code,
            (SELECT COUNT(*) FROM student_courses sc WHERE sc.course_id = c.id) AS enrollment_count
     FROM courses c
     JOIN departments d ON d.id = c.department_id
     WHERE ' . implode(' AND ', $where) . '
     ORDER BY c.course_code',
    $params
);

$breadcrumbs = ['Courses' => null];
require_once __DIR__ . '/../../includes/header.php';
?>

<div class="d-flex justify-content-between align-items-center mb-3">
    <h4 class="page-title mb-0"><i class="bi bi-book me-2"></i>Courses</h4>
    <?php if (in_array($_SESSION['user_role'], ['admin','registrar'])): ?>
    <a href="<?= BASE_URL ?>/modules/courses/add.php" class="btn btn-primary">
        <i class="bi bi-plus-lg me-1"></i>Add Course
    </a>
    <?php endif; ?>
</div>

<div class="card mb-3">
    <div class="card-body py-2">
        <form method="GET" class="row g-2 align-items-end">
            <div class="col-sm-4">
                <label class="form-label small mb-1">Department</label>
                <select name="dept" class="form-select form-select-sm">
                    <option value="">All Departments</option>
                    <?php foreach ($departments as $d): ?>
                    <option value="<?= $d['id'] ?>" <?= $filterDept == $d['id'] ? 'selected' : '' ?>>
                        <?= sanitize($d['name']) ?>
                    </option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-sm-2">
                <label class="form-label small mb-1">Level</label>
                <select name="level" class="form-select form-select-sm">
                    <option value="">All</option>
                    <?php foreach (['100','200','300','400','500'] as $l): ?>
                    <option value="<?= $l ?>" <?= $filterLevel === $l ? 'selected' : '' ?>><?= $l ?></option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-sm-2">
                <label class="form-label small mb-1">Semester</label>
                <select name="semester" class="form-select form-select-sm">
                    <option value="">All</option>
                    <option value="first" <?= $filterSem === 'first' ? 'selected' : '' ?>>First</option>
                    <option value="second" <?= $filterSem === 'second' ? 'selected' : '' ?>>Second</option>
                </select>
            </div>
            <div class="col-auto">
                <button type="submit" class="btn btn-sm btn-primary">Filter</button>
                <a href="<?= BASE_URL ?>/modules/courses/index.php" class="btn btn-sm btn-outline-secondary ms-1">Reset</a>
            </div>
        </form>
    </div>
</div>

<div class="card">
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
                <thead>
                <tr>
                    <th>Code</th><th>Title</th><th>Department</th>
                    <th>Level</th><th>Semester</th><th>Credits</th>
                    <th>Enrolled</th><th>Status</th>
                    <?php if (in_array($_SESSION['user_role'], ['admin','registrar'])): ?>
                    <th class="text-center">Actions</th>
                    <?php endif; ?>
                </tr>
                </thead>
                <tbody>
                <?php foreach ($courses as $c): ?>
                <tr>
                    <td><strong><?= sanitize($c['course_code']) ?></strong></td>
                    <td><?= sanitize($c['course_title']) ?></td>
                    <td><span class="badge bg-light text-dark border"><?= sanitize($c['dept_code']) ?></span></td>
                    <td><?= sanitize($c['level']) ?>L</td>
                    <td><?= ucfirst(sanitize($c['semester'])) ?></td>
                    <td><?= $c['credit_units'] ?></td>
                    <td><span class="badge bg-primary"><?= $c['enrollment_count'] ?></span></td>
                    <td><?= statusBadge($c['status']) ?></td>
                    <?php if (in_array($_SESSION['user_role'], ['admin','registrar'])): ?>
                    <td class="text-center">
                        <div class="btn-group btn-group-sm">
                            <a href="<?= BASE_URL ?>/modules/courses/edit.php?id=<?= $c['id'] ?>"
                               class="btn btn-outline-secondary"><i class="bi bi-pencil"></i></a>
                            <a href="<?= BASE_URL ?>/modules/courses/delete.php?id=<?= $c['id'] ?>"
                               class="btn btn-outline-danger btn-delete"
                               data-label="<?= sanitize($c['course_code']) ?>">
                                <i class="bi bi-trash"></i></a>
                        </div>
                    </td>
                    <?php endif; ?>
                </tr>
                <?php endforeach; ?>
                <?php if (empty($courses)): ?>
                <tr><td colspan="9" class="text-center text-muted py-4">No courses found.</td></tr>
                <?php endif; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- Delete modal -->
<div class="modal fade" id="deleteModal" tabindex="-1">
    <div class="modal-dialog"><div class="modal-content">
        <div class="modal-header">
            <h5 class="modal-title" id="deleteConfirmLabel">Confirm Delete</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body" id="deleteConfirmBody">Are you sure?</div>
        <div class="modal-footer">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <a href="#" class="btn btn-danger" id="deleteConfirmBtn">Delete</a>
        </div>
    </div></div>
</div>

<?php require_once __DIR__ . '/../../includes/footer.php'; ?>
