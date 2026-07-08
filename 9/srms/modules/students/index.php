<?php
// ============================================================
// SRMS – Student List
// ============================================================
define('PAGE_TITLE', 'Students');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();
requireRole(['admin','registrar','teacher']);

$departments = getAllDepartments();

// Filters
$filterDept   = (int)($_GET['dept']   ?? 0);
$filterLevel  = sanitize($_GET['level']  ?? '');
$filterStatus = sanitize($_GET['status'] ?? '');
$search       = sanitize($_GET['q']      ?? '');

// Pagination
$perPage = 15;
$page    = max(1, (int)($_GET['page'] ?? 1));
$offset  = ($page - 1) * $perPage;

$where  = ['1=1'];
$params = [];

if ($filterDept) {
    $where[]          = 's.department_id = :dept';
    $params[':dept']  = $filterDept;
}
if ($filterLevel) {
    $where[]           = 's.level = :level';
    $params[':level']  = $filterLevel;
}
if ($filterStatus) {
    $where[]            = 's.status = :status';
    $params[':status']  = $filterStatus;
}
if ($search) {
    $where[]  = '(s.matric_number LIKE :q OR s.first_name LIKE :q OR s.last_name LIKE :q OR s.email LIKE :q)';
    $params[':q'] = '%' . $search . '%';
}

$whereClause = implode(' AND ', $where);

$total = (int)db()->fetchOne(
    "SELECT COUNT(*) AS c FROM students s WHERE {$whereClause}", $params
)['c'];

$totalPages = max(1, (int)ceil($total / $perPage));

$students = db()->fetchAll(
    "SELECT s.id, s.matric_number, s.first_name, s.last_name, s.gender,
            s.level, s.status, s.email, s.phone, s.admission_date,
            d.name AS dept_name, d.code AS dept_code
     FROM students s
     JOIN departments d ON d.id = s.department_id
     WHERE {$whereClause}
     ORDER BY s.last_name, s.first_name
     LIMIT {$perPage} OFFSET {$offset}",
    $params
);

$breadcrumbs = ['Students' => null];
require_once __DIR__ . '/../../includes/header.php';
?>

<div class="d-flex justify-content-between align-items-center mb-3">
    <h4 class="page-title mb-0"><i class="bi bi-people me-2"></i>Student Records</h4>
    <?php if (in_array($_SESSION['user_role'], ['admin','registrar'])): ?>
    <a href="<?= BASE_URL ?>/modules/students/add.php" class="btn btn-primary">
        <i class="bi bi-person-plus me-1"></i>Add Student
    </a>
    <?php endif; ?>
</div>

<!-- Search bar -->
<div class="mb-3 position-relative" style="max-width:340px;">
    <input type="text" class="form-control" id="studentSearchInput"
           placeholder="Quick search by name or matric…" value="<?= sanitize($search) ?>">
    <div id="studentSearchResults" class="card position-absolute w-100 shadow-sm"
         style="display:none;z-index:999;top:100%;max-height:220px;overflow-y:auto;"></div>
</div>

<!-- Filters card -->
<div class="card mb-3">
    <div class="card-body py-2">
        <form method="GET" class="row g-2 align-items-end">
            <div class="col-sm-4 col-md-3">
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
            <div class="col-sm-3 col-md-2">
                <label class="form-label small mb-1">Level</label>
                <select name="level" class="form-select form-select-sm">
                    <option value="">All Levels</option>
                    <?php foreach (['100','200','300','400','500'] as $lvl): ?>
                    <option value="<?= $lvl ?>" <?= $filterLevel === $lvl ? 'selected' : '' ?>><?= $lvl ?></option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-sm-3 col-md-2">
                <label class="form-label small mb-1">Status</label>
                <select name="status" class="form-select form-select-sm">
                    <option value="">All Statuses</option>
                    <?php foreach (['active','suspended','graduated','withdrawn'] as $st): ?>
                    <option value="<?= $st ?>" <?= $filterStatus === $st ? 'selected' : '' ?>>
                        <?= ucfirst($st) ?>
                    </option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-sm-4 col-md-3">
                <label class="form-label small mb-1">Search</label>
                <input type="text" name="q" class="form-control form-control-sm"
                       placeholder="Name, matric, email…" value="<?= sanitize($search) ?>">
            </div>
            <div class="col-auto">
                <button type="submit" class="btn btn-sm btn-primary">
                    <i class="bi bi-funnel me-1"></i>Filter
                </button>
                <a href="<?= BASE_URL ?>/modules/students/index.php" class="btn btn-sm btn-outline-secondary ms-1">
                    Reset
                </a>
            </div>
        </form>
    </div>
</div>

<!-- Results info -->
<div class="d-flex justify-content-between align-items-center mb-2">
    <small class="text-muted">
        Showing <?= number_format(($offset + 1)) ?>–<?= number_format(min($offset + $perPage, $total)) ?>
        of <?= number_format($total) ?> students
    </small>
</div>

<!-- Table -->
<div class="card">
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
                <thead>
                <tr>
                    <th>#</th>
                    <th>Matric No.</th>
                    <th>Full Name</th>
                    <th>Department</th>
                    <th>Level</th>
                    <th>Gender</th>
                    <th>Status</th>
                    <th class="text-center">Actions</th>
                </tr>
                </thead>
                <tbody>
                <?php foreach ($students as $i => $s): ?>
                <tr>
                    <td class="text-muted small"><?= $offset + $i + 1 ?></td>
                    <td>
                        <a href="<?= BASE_URL ?>/modules/students/view.php?id=<?= $s['id'] ?>"
                           class="fw-semibold text-decoration-none">
                            <?= sanitize($s['matric_number']) ?>
                        </a>
                    </td>
                    <td><?= sanitize($s['last_name'] . ', ' . $s['first_name']) ?></td>
                    <td><span class="badge bg-light text-dark border"><?= sanitize($s['dept_code']) ?></span>
                        <span class="small text-muted d-none d-lg-inline ms-1"><?= sanitize($s['dept_name']) ?></span>
                    </td>
                    <td><?= sanitize($s['level']) ?>L</td>
                    <td><?= sanitize(ucfirst($s['gender'])) ?></td>
                    <td><?= statusBadge($s['status']) ?></td>
                    <td class="text-center">
                        <div class="btn-group btn-group-sm">
                            <a href="<?= BASE_URL ?>/modules/students/view.php?id=<?= $s['id'] ?>"
                               class="btn btn-outline-primary" title="View" data-bs-toggle="tooltip">
                                <i class="bi bi-eye"></i>
                            </a>
                            <?php if (in_array($_SESSION['user_role'], ['admin','registrar'])): ?>
                            <a href="<?= BASE_URL ?>/modules/students/edit.php?id=<?= $s['id'] ?>"
                               class="btn btn-outline-secondary" title="Edit" data-bs-toggle="tooltip">
                                <i class="bi bi-pencil"></i>
                            </a>
                            <a href="<?= BASE_URL ?>/modules/students/delete.php?id=<?= $s['id'] ?>"
                               class="btn btn-outline-danger btn-delete"
                               data-label="<?= sanitize($s['first_name'] . ' ' . $s['last_name']) ?>"
                               title="Delete" data-bs-toggle="tooltip">
                                <i class="bi bi-trash"></i>
                            </a>
                            <?php endif; ?>
                        </div>
                    </td>
                </tr>
                <?php endforeach; ?>
                <?php if (empty($students)): ?>
                <tr><td colspan="8" class="text-center text-muted py-4">
                    <i class="bi bi-inbox fs-2 d-block mb-2"></i>No students found.
                </td></tr>
                <?php endif; ?>
                </tbody>
            </table>
        </div>
    </div>

    <?php if ($totalPages > 1): ?>
    <div class="card-footer">
        <nav>
            <ul class="pagination pagination-sm justify-content-center mb-0">
                <?php for ($p = 1; $p <= $totalPages; $p++): ?>
                <li class="page-item <?= $p === $page ? 'active' : '' ?>">
                    <a class="page-link" href="?<?= http_build_query(array_merge($_GET, ['page' => $p])) ?>">
                        <?= $p ?>
                    </a>
                </li>
                <?php endfor; ?>
            </ul>
        </nav>
    </div>
    <?php endif; ?>
</div>

<!-- Delete modal -->
<div class="modal fade" id="deleteModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="deleteConfirmLabel">Confirm Delete</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body" id="deleteConfirmBody">Are you sure?</div>
            <div class="modal-footer">
                <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <a href="#" class="btn btn-danger" id="deleteConfirmBtn">Delete</a>
            </div>
        </div>
    </div>
</div>

<?php require_once __DIR__ . '/../../includes/footer.php'; ?>
