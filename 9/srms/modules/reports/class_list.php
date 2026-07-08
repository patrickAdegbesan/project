<?php
define('PAGE_TITLE', 'Class List');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();
requireRole(['admin','registrar','teacher']);

$departments = getAllDepartments();
$filterDept  = (int)($_GET['dept'] ?? 0);
$filterLevel = sanitize($_GET['level'] ?? '');

$students = [];
if ($filterDept || $filterLevel) {
    $where  = ['1=1'];
    $params = [];
    if ($filterDept)  { $where[] = 's.department_id = :dept'; $params[':dept'] = $filterDept; }
    if ($filterLevel) { $where[] = 's.level = :lvl';          $params[':lvl'] = $filterLevel; }

    $students = db()->fetchAll(
        'SELECT s.*, d.name AS dept_name, d.code AS dept_code
         FROM students s JOIN departments d ON d.id = s.department_id
         WHERE ' . implode(' AND ', $where) . ' AND s.status = "active"
         ORDER BY s.last_name, s.first_name',
        $params
    );
}

$breadcrumbs = ['Reports' => BASE_URL . '/modules/reports/index.php', 'Class List' => null];
require_once __DIR__ . '/../../includes/header.php';
?>

<div class="d-flex justify-content-between align-items-center mb-3">
    <h4 class="page-title mb-0"><i class="bi bi-list-ul me-2"></i>Class List</h4>
    <?php if (!empty($students)): ?>
    <button class="btn btn-outline-secondary btn-sm no-print" onclick="window.print()">
        <i class="bi bi-printer me-1"></i>Print List
    </button>
    <?php endif; ?>
</div>

<div class="card mb-3 no-print">
    <div class="card-body">
        <form method="GET" class="row g-3 align-items-end">
            <div class="col-sm-5">
                <label class="form-label">Department</label>
                <select name="dept" class="form-select">
                    <option value="">All Departments</option>
                    <?php foreach ($departments as $d): ?>
                    <option value="<?= $d['id'] ?>" <?= $filterDept == $d['id'] ? 'selected' : '' ?>>
                        <?= sanitize($d['name']) ?>
                    </option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-sm-3">
                <label class="form-label">Level</label>
                <select name="level" class="form-select">
                    <option value="">All Levels</option>
                    <?php foreach (['100','200','300','400','500'] as $l): ?>
                    <option value="<?= $l ?>" <?= $filterLevel === $l ? 'selected' : '' ?>><?= $l ?>L</option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-auto">
                <button type="submit" class="btn btn-primary">Generate List</button>
            </div>
        </form>
    </div>
</div>

<?php if (!empty($students)): ?>
<!-- Print header -->
<div class="transcript-header d-none d-print-block mb-3">
    <h4><?= INSTITUTION_NAME ?></h4>
    <h5>Class List <?= $filterLevel ? '– ' . sanitize($filterLevel) . 'L' : '' ?></h5>
    <p>Date: <?= date('d/m/Y') ?> | Total Students: <?= count($students) ?></p>
</div>

<div class="card">
    <div class="card-header d-flex justify-content-between no-print">
        <span>
            <?= count($students) ?> student(s) found
            <?= $filterLevel ? ' – ' . sanitize($filterLevel) . 'L' : '' ?>
        </span>
    </div>
    <div class="card-body p-0">
        <table class="table table-bordered table-sm mb-0">
            <thead class="table-dark">
            <tr>
                <th>S/N</th>
                <th>Matric Number</th>
                <th>Surname</th>
                <th>First Name</th>
                <th>Middle Name</th>
                <th>Gender</th>
                <th>Department</th>
                <th>Level</th>
                <th>Phone</th>
                <th>Status</th>
            </tr>
            </thead>
            <tbody>
            <?php foreach ($students as $i => $s): ?>
            <tr>
                <td><?= $i + 1 ?></td>
                <td><?= sanitize($s['matric_number']) ?></td>
                <td><?= sanitize($s['last_name']) ?></td>
                <td><?= sanitize($s['first_name']) ?></td>
                <td><?= sanitize($s['middle_name'] ?? '') ?></td>
                <td><?= sanitize(ucfirst($s['gender'])) ?></td>
                <td><?= sanitize($s['dept_name']) ?></td>
                <td><?= sanitize($s['level']) ?>L</td>
                <td><?= sanitize($s['phone'] ?? '') ?></td>
                <td><?= sanitize(ucfirst($s['status'])) ?></td>
            </tr>
            <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</div>
<?php endif; ?>

<?php require_once __DIR__ . '/../../includes/footer.php'; ?>
