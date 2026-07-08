<?php
define('PAGE_TITLE', 'Add User');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();
requireRole(['admin']);

$errors   = [];
$formData = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verifyCsrf();

    $fields = ['username','email','full_name','phone','role','status','password','password_confirm'];
    foreach ($fields as $f) $formData[$f] = trim($_POST[$f] ?? '');

    if (empty($formData['username']))   $errors[] = 'Username is required.';
    if (empty($formData['email']))      $errors[] = 'Email is required.';
    if (empty($formData['full_name']))  $errors[] = 'Full name is required.';
    if (empty($formData['role']))       $errors[] = 'Role is required.';
    if (strlen($formData['password']) < 8)
        $errors[] = 'Password must be at least 8 characters.';
    if ($formData['password'] !== $formData['password_confirm'])
        $errors[] = 'Passwords do not match.';

    $dupUser = db()->fetchOne('SELECT id FROM users WHERE username = :u', [':u' => $formData['username']]);
    if ($dupUser) $errors[] = 'Username already taken.';

    $dupEmail = db()->fetchOne('SELECT id FROM users WHERE email = :e', [':e' => $formData['email']]);
    if ($dupEmail) $errors[] = 'Email already registered.';

    if (empty($errors)) {
        db()->execute(
            'INSERT INTO users (username, email, password_hash, role, full_name, phone, status)
             VALUES (:u, :e, :p, :r, :fn, :ph, :st)',
            [
                ':u'  => $formData['username'],
                ':e'  => $formData['email'],
                ':p'  => password_hash($formData['password'], PASSWORD_BCRYPT, ['cost' => 12]),
                ':r'  => $formData['role'],
                ':fn' => $formData['full_name'],
                ':ph' => $formData['phone'] ?: null,
                ':st' => $formData['status'] ?: 'active',
            ]
        );
        logAudit($_SESSION['user_id'], 'ADD_USER', 'users', "Created user: {$formData['username']}");
        flashMessage('success', "User {$formData['username']} created successfully.");
        redirect(BASE_URL . '/modules/users/index.php');
    }
}

$breadcrumbs = ['Users' => BASE_URL . '/modules/users/index.php', 'Add User' => null];
require_once __DIR__ . '/../../includes/header.php';
?>

<h4 class="page-title"><i class="bi bi-person-plus me-2"></i>Add User Account</h4>

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
                    <label class="form-label">Full Name <span class="text-danger">*</span></label>
                    <input type="text" name="full_name" class="form-control"
                           value="<?= sanitize($formData['full_name'] ?? '') ?>" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Username <span class="text-danger">*</span></label>
                    <input type="text" name="username" class="form-control"
                           value="<?= sanitize($formData['username'] ?? '') ?>" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Email <span class="text-danger">*</span></label>
                    <input type="email" name="email" class="form-control"
                           value="<?= sanitize($formData['email'] ?? '') ?>" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Phone</label>
                    <input type="tel" name="phone" class="form-control"
                           value="<?= sanitize($formData['phone'] ?? '') ?>">
                </div>
                <div class="col-md-6">
                    <label class="form-label">Role <span class="text-danger">*</span></label>
                    <select name="role" class="form-select" required>
                        <option value="">Select Role</option>
                        <?php foreach (['admin','registrar','teacher','student'] as $r): ?>
                        <option value="<?= $r ?>"
                            <?= ($formData['role'] ?? '') === $r ? 'selected' : '' ?>>
                            <?= ucfirst($r) ?>
                        </option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Status</label>
                    <select name="status" class="form-select">
                        <option value="active" <?= ($formData['status'] ?? 'active') === 'active' ? 'selected' : '' ?>>Active</option>
                        <option value="inactive" <?= ($formData['status'] ?? '') === 'inactive' ? 'selected' : '' ?>>Inactive</option>
                    </select>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Password <span class="text-danger">*</span></label>
                    <input type="password" name="password" class="form-control"
                           placeholder="Min 8 characters" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Confirm Password <span class="text-danger">*</span></label>
                    <input type="password" name="password_confirm" class="form-control" required>
                </div>
                <div class="col-12 d-flex gap-2">
                    <button type="submit" class="btn btn-primary">
                        <i class="bi bi-person-check me-1"></i>Create User
                    </button>
                    <a href="<?= BASE_URL ?>/modules/users/index.php" class="btn btn-outline-secondary">Cancel</a>
                </div>
            </div>
        </form>
    </div>
</div>

<?php require_once __DIR__ . '/../../includes/footer.php'; ?>
