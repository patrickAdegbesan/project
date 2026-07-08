<?php
define('PAGE_TITLE', 'User Accounts');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();
requireRole(['admin']);

$users = db()->fetchAll(
    'SELECT * FROM users ORDER BY role, full_name'
);

$breadcrumbs = ['User Accounts' => null];
require_once __DIR__ . '/../../includes/header.php';
?>

<div class="d-flex justify-content-between align-items-center mb-3">
    <h4 class="page-title mb-0"><i class="bi bi-people-fill me-2"></i>User Accounts</h4>
    <a href="<?= BASE_URL ?>/modules/users/add.php" class="btn btn-primary btn-sm">
        <i class="bi bi-person-plus me-1"></i>Add User
    </a>
</div>

<div class="card">
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-hover table-sm mb-0">
                <thead>
                <tr>
                    <th>#</th><th>Full Name</th><th>Username</th><th>Email</th>
                    <th>Role</th><th>Phone</th><th>Status</th><th>Last Login</th>
                    <th class="text-center">Actions</th>
                </tr>
                </thead>
                <tbody>
                <?php foreach ($users as $i => $u): ?>
                <?php
                $roleColor = [
                    'admin'     => 'danger',
                    'registrar' => 'warning',
                    'teacher'   => 'info',
                    'student'   => 'secondary',
                ][$u['role']] ?? 'secondary';
                ?>
                <tr>
                    <td><?= $i + 1 ?></td>
                    <td><?= sanitize($u['full_name']) ?></td>
                    <td><code><?= sanitize($u['username']) ?></code></td>
                    <td><?= sanitize($u['email']) ?></td>
                    <td><span class="badge bg-<?= $roleColor ?>"><?= ucfirst(sanitize($u['role'])) ?></span></td>
                    <td><?= sanitize($u['phone'] ?? 'N/A') ?></td>
                    <td><?= statusBadge($u['status']) ?></td>
                    <td class="small text-muted">
                        <?= $u['last_login'] ? formatDate($u['last_login'], 'd/m/Y H:i') : 'Never' ?>
                    </td>
                    <td class="text-center">
                        <div class="btn-group btn-group-sm">
                            <a href="<?= BASE_URL ?>/modules/users/edit.php?id=<?= $u['id'] ?>"
                               class="btn btn-outline-secondary"><i class="bi bi-pencil"></i></a>
                            <?php if ($u['id'] != $_SESSION['user_id']): ?>
                            <a href="<?= BASE_URL ?>/modules/users/delete.php?id=<?= $u['id'] ?>"
                               class="btn btn-outline-danger btn-delete"
                               data-label="<?= sanitize($u['full_name']) ?>">
                                <i class="bi bi-trash"></i>
                            </a>
                            <?php endif; ?>
                        </div>
                    </td>
                </tr>
                <?php endforeach; ?>
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
