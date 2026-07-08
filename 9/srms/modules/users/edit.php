<?php
define('PAGE_TITLE', 'Edit User');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();

$id = (int)($_GET['id'] ?? 0);

// Users can only edit themselves; admins can edit anyone
if ($_SESSION['user_role'] !== 'admin' && $id !== (int)$_SESSION['user_id']) {
    flashMessage('danger', 'Access denied.');
    redirect(BASE_URL . '/modules/dashboard/index.php');
}

$user = db()->fetchOne('SELECT * FROM users WHERE id = :id', [':id' => $id]);
if (!$user) {
    flashMessage('danger', 'User not found.');
    redirect(BASE_URL . '/modules/users/index.php');
}

$errors   = [];
$formData = $user;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verifyCsrf();

    $fields = ['full_name','email','phone','role','status'];
    foreach ($fields as $f) $formData[$f] = trim($_POST[$f] ?? '');

    if (empty($formData['full_name'])) $errors[] = 'Full name is required.';
    if (empty($formData['email']))     $errors[] = 'Email is required.';

    $dup = db()->fetchOne('SELECT id FROM users WHERE email = :e AND id != :id',
        [':e' => $formData['email'], ':id' => $id]);
    if ($dup) $errors[] = 'Email already in use by another account.';

    // Password change (optional)
    $newPassword = trim($_POST['new_password'] ?? '');
    $confirmPassword = trim($_POST['confirm_password'] ?? '');
    if (!empty($newPassword)) {
        if (strlen($newPassword) < 8) {
            $errors[] = 'New password must be at least 8 characters.';
        } elseif ($newPassword !== $confirmPassword) {
            $errors[] = 'Passwords do not match.';
        }
    }

    if (empty($errors)) {
        $params = [
            ':fn'  => $formData['full_name'],
            ':e'   => $formData['email'],
            ':ph'  => $formData['phone'] ?: null,
            ':id'  => $id,
        ];
        $sql = 'UPDATE users SET full_name=:fn, email=:e, phone=:ph';

        // Only admin can change role/status
        if ($_SESSION['user_role'] === 'admin') {
            $sql .= ', role=:role, status=:st';
            $params[':role'] = $formData['role'];
            $params[':st']   = $formData['status'];
        }

        if (!empty($newPassword)) {
            $sql .= ', password_hash=:pw';
            $params[':pw'] = password_hash($newPassword, PASSWORD_BCRYPT, ['cost' => 12]);
        }

        $sql .= ' WHERE id=:id';
        db()->execute($sql, $params);

        logAudit($_SESSION['user_id'], 'EDIT_USER', 'users', "Updated user ID {$id}");
        flashMessage('success', 'Account updated successfully.');

        if ($_SESSION['user_role'] === 'admin') {
            redirect(BASE_URL . '/modules/users/index.php');
        } else {
            redirect(BASE_URL . '/modules/users/edit.php?id=' . $id);
        }
    }
}

$breadcrumbs = ['Users' => BASE_URL . '/modules/users/index.php', 'Edit' => null];
require_once __DIR__ . '/../../includes/header.php';
?>

<h4 class="page-title"><i class="bi bi-pencil me-2"></i>Edit User Account</h4>

<?php if (!empty($errors)): ?>
<div class="alert alert-danger"><ul class="mb-0">
    <?php foreach ($errors as $e): ?><li><?= sanitize($e) ?></li><?php endforeach; ?>
</ul></div>
<?php endif; ?>

<div class="card" style="max-width:650px;">
    <div class="card-body">
        <form method="POST" novalidate>
            <input type="hidden" name="csrf_token" value="<?= htmlspecialchars($_SESSION['csrf_token']) ?>">
            <div class="row g-3">
                <div class="col-md-6">
                    <label class="form-label">Full Name</label>
                    <input type="text" name="full_name" class="form-control"
                           value="<?= sanitize($formData['full_name']) ?>" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Username</label>
                    <input type="text" class="form-control" value="<?= sanitize($user['username']) ?>" disabled>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Email</label>
                    <input type="email" name="email" class="form-control"
                           value="<?= sanitize($formData['email']) ?>" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Phone</label>
                    <input type="tel" name="phone" class="form-control"
                           value="<?= sanitize($formData['phone'] ?? '') ?>">
                </div>

                <?php if ($_SESSION['user_role'] === 'admin'): ?>
                <div class="col-md-6">
                    <label class="form-label">Role</label>
                    <select name="role" class="form-select">
                        <?php foreach (['admin','registrar','teacher','student'] as $r): ?>
                        <option value="<?= $r ?>" <?= $formData['role'] === $r ? 'selected' : '' ?>>
                            <?= ucfirst($r) ?>
                        </option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Status</label>
                    <select name="status" class="form-select">
                        <option value="active"   <?= $formData['status'] === 'active'   ? 'selected' : '' ?>>Active</option>
                        <option value="inactive" <?= $formData['status'] === 'inactive' ? 'selected' : '' ?>>Inactive</option>
                    </select>
                </div>
                <?php endif; ?>

                <div class="col-12"><hr><small class="text-muted">Change Password (leave blank to keep current)</small></div>
                <div class="col-md-6">
                    <label class="form-label">New Password</label>
                    <input type="password" name="new_password" class="form-control"
                           placeholder="Min 8 characters">
                </div>
                <div class="col-md-6">
                    <label class="form-label">Confirm New Password</label>
                    <input type="password" name="confirm_password" class="form-control">
                </div>

                <div class="col-12 d-flex gap-2">
                    <button type="submit" class="btn btn-primary">
                        <i class="bi bi-check-lg me-1"></i>Save Changes
                    </button>
                    <a href="<?= BASE_URL ?>/modules/users/index.php" class="btn btn-outline-secondary">Cancel</a>
                </div>
            </div>
        </form>
    </div>
</div>

<?php require_once __DIR__ . '/../../includes/footer.php'; ?>
