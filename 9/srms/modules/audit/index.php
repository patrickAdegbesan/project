<?php
define('PAGE_TITLE', 'Audit Logs');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();
requireRole(['admin']);

// Filters
$filterModule = sanitize($_GET['module'] ?? '');
$filterAction = sanitize($_GET['action'] ?? '');
$filterUser   = (int)($_GET['user_id'] ?? 0);
$dateFrom     = sanitize($_GET['date_from'] ?? '');
$dateTo       = sanitize($_GET['date_to'] ?? '');

$perPage = 25;
$page    = max(1, (int)($_GET['page'] ?? 1));
$offset  = ($page - 1) * $perPage;

$where  = ['1=1'];
$params = [];
if ($filterModule) { $where[] = 'a.module = :mod';  $params[':mod'] = $filterModule; }
if ($filterAction) { $where[] = 'a.action LIKE :act'; $params[':act'] = '%' . $filterAction . '%'; }
if ($filterUser)   { $where[] = 'a.user_id = :uid';  $params[':uid'] = $filterUser; }
if ($dateFrom)     { $where[] = 'DATE(a.created_at) >= :df'; $params[':df'] = $dateFrom; }
if ($dateTo)       { $where[] = 'DATE(a.created_at) <= :dt'; $params[':dt'] = $dateTo; }

$whereClause = implode(' AND ', $where);

$total      = (int)db()->fetchOne("SELECT COUNT(*) AS c FROM audit_logs a WHERE {$whereClause}", $params)['c'];
$totalPages = max(1, (int)ceil($total / $perPage));

$logs = db()->fetchAll(
    "SELECT a.*, u.full_name, u.username FROM audit_logs a
     LEFT JOIN users u ON u.id = a.user_id
     WHERE {$whereClause}
     ORDER BY a.created_at DESC
     LIMIT {$perPage} OFFSET {$offset}",
    $params
);

$modules = db()->fetchAll('SELECT DISTINCT module FROM audit_logs ORDER BY module');
$users   = db()->fetchAll('SELECT id, full_name FROM users ORDER BY full_name');

$moduleColors = [
    'auth'       => 'primary',
    'students'   => 'success',
    'courses'    => 'info',
    'grades'     => 'warning',
    'attendance' => 'secondary',
    'fees'       => 'danger',
    'users'      => 'dark',
];

$breadcrumbs = ['Audit Logs' => null];
require_once __DIR__ . '/../../includes/header.php';
?>

<h4 class="page-title"><i class="bi bi-shield-check me-2"></i>Audit Log</h4>

<div class="card mb-3">
    <div class="card-body py-2">
        <form method="GET" class="row g-2 align-items-end">
            <div class="col-sm-2">
                <label class="form-label small mb-1">Module</label>
                <select name="module" class="form-select form-select-sm">
                    <option value="">All Modules</option>
                    <?php foreach ($modules as $m): ?>
                    <option value="<?= sanitize($m['module']) ?>"
                        <?= $filterModule === $m['module'] ? 'selected' : '' ?>>
                        <?= ucfirst(sanitize($m['module'])) ?>
                    </option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-sm-3">
                <label class="form-label small mb-1">Action (keyword)</label>
                <input type="text" name="action" class="form-control form-control-sm"
                       value="<?= sanitize($filterAction) ?>" placeholder="e.g. LOGIN">
            </div>
            <div class="col-sm-3">
                <label class="form-label small mb-1">User</label>
                <select name="user_id" class="form-select form-select-sm">
                    <option value="">All Users</option>
                    <?php foreach ($users as $u): ?>
                    <option value="<?= $u['id'] ?>" <?= $filterUser == $u['id'] ? 'selected' : '' ?>>
                        <?= sanitize($u['full_name']) ?>
                    </option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-sm-2">
                <label class="form-label small mb-1">From</label>
                <input type="date" name="date_from" class="form-control form-control-sm"
                       value="<?= sanitize($dateFrom) ?>">
            </div>
            <div class="col-sm-2">
                <label class="form-label small mb-1">To</label>
                <input type="date" name="date_to" class="form-control form-control-sm"
                       value="<?= sanitize($dateTo) ?>">
            </div>
            <div class="col-auto">
                <button type="submit" class="btn btn-sm btn-primary">Filter</button>
                <a href="<?= BASE_URL ?>/modules/audit/index.php" class="btn btn-sm btn-outline-secondary ms-1">Reset</a>
            </div>
        </form>
    </div>
</div>

<div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
        <span>
            <i class="bi bi-list-ul me-1"></i>
            <?= number_format($total) ?> log entries
        </span>
        <small class="text-muted">Showing page <?= $page ?> of <?= $totalPages ?></small>
    </div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-hover table-sm mb-0">
                <thead>
                <tr>
                    <th>Timestamp</th><th>User</th><th>Module</th>
                    <th>Action</th><th>Description</th><th>IP Address</th>
                </tr>
                </thead>
                <tbody>
                <?php foreach ($logs as $log): ?>
                <?php $modColor = $moduleColors[$log['module']] ?? 'secondary'; ?>
                <tr>
                    <td class="small text-muted">
                        <?= date('d/m/Y H:i:s', strtotime($log['created_at'])) ?>
                    </td>
                    <td>
                        <?php if ($log['full_name']): ?>
                        <strong><?= sanitize($log['full_name']) ?></strong><br>
                        <small class="text-muted"><?= sanitize($log['username'] ?? '') ?></small>
                        <?php else: ?>
                        <span class="text-muted">System</span>
                        <?php endif; ?>
                    </td>
                    <td>
                        <span class="badge bg-<?= $modColor ?>"><?= ucfirst(sanitize($log['module'])) ?></span>
                    </td>
                    <td><code class="small"><?= sanitize($log['action']) ?></code></td>
                    <td class="small"><?= sanitize($log['description'] ?? '') ?></td>
                    <td class="small text-muted"><?= sanitize($log['ip_address'] ?? '') ?></td>
                </tr>
                <?php endforeach; ?>
                <?php if (empty($logs)): ?>
                <tr><td colspan="6" class="text-center text-muted py-4">No audit log entries.</td></tr>
                <?php endif; ?>
                </tbody>
            </table>
        </div>
    </div>

    <?php if ($totalPages > 1): ?>
    <div class="card-footer">
        <nav>
            <ul class="pagination pagination-sm justify-content-center mb-0">
                <?php
                $startPage = max(1, $page - 3);
                $endPage   = min($totalPages, $page + 3);
                if ($startPage > 1): ?>
                <li class="page-item">
                    <a class="page-link" href="?<?= http_build_query(array_merge($_GET, ['page' => 1])) ?>">1</a>
                </li>
                <li class="page-item disabled"><span class="page-link">…</span></li>
                <?php endif; ?>
                <?php for ($p = $startPage; $p <= $endPage; $p++): ?>
                <li class="page-item <?= $p === $page ? 'active' : '' ?>">
                    <a class="page-link" href="?<?= http_build_query(array_merge($_GET, ['page' => $p])) ?>">
                        <?= $p ?>
                    </a>
                </li>
                <?php endfor; ?>
                <?php if ($endPage < $totalPages): ?>
                <li class="page-item disabled"><span class="page-link">…</span></li>
                <li class="page-item">
                    <a class="page-link" href="?<?= http_build_query(array_merge($_GET, ['page' => $totalPages])) ?>">
                        <?= $totalPages ?>
                    </a>
                </li>
                <?php endif; ?>
            </ul>
        </nav>
    </div>
    <?php endif; ?>
</div>

<?php require_once __DIR__ . '/../../includes/footer.php'; ?>
