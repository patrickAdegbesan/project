<?php
// ============================================================
// SRMS – Login Page
// ============================================================
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';
require_once __DIR__ . '/../../includes/auth.php';

// Already logged in
if (isLoggedIn()) {
    redirect(BASE_URL . '/modules/dashboard/index.php');
}

$error    = '';
$username = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // CSRF check
    $token = $_POST['csrf_token'] ?? '';
    if (!hash_equals($_SESSION['csrf_token'], $token)) {
        $error = 'Security token mismatch. Please reload the page and try again.';
    } else {
        $username = trim($_POST['username'] ?? '');
        $password = $_POST['password'] ?? '';

        if (empty($username) || empty($password)) {
            $error = 'Username and password are required.';
        } elseif (!checkLoginThrottle($username)) {
            $error = 'Too many failed attempts. Please wait 15 minutes before trying again.';
        } else {
            $result = loginUser($username, $password);
            if ($result['success']) {
                resetLoginAttempts($username);
                redirect(BASE_URL . '/modules/dashboard/index.php');
            } else {
                incrementLoginAttempts($username);
                $remaining = getRemainingAttempts($username);
                $error = $result['error'] . " ({$remaining} attempt(s) remaining)";
            }
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login – <?= SITE_SHORT_NAME ?></title>
    <link rel="stylesheet" href="<?= BASE_URL ?>/assets/vendor/css/bootstrap.min.css">
    <link rel="stylesheet" href="<?= BASE_URL ?>/assets/vendor/css/bootstrap-icons.min.css">
    <link rel="stylesheet" href="<?= BASE_URL ?>/assets/css/style.css">
    <style>
        body {
            background: linear-gradient(135deg, #1a237e 0%, #3949ab 50%, #1565c0 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-card {
            width: 100%;
            max-width: 420px;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.4);
            overflow: hidden;
        }
        .login-header {
            background: #1a237e;
            color: #fff;
            padding: 2rem;
            text-align: center;
        }
        .login-header .logo-icon {
            font-size: 3rem;
            margin-bottom: 0.5rem;
        }
        .login-body {
            padding: 2rem;
            background: #fff;
        }
        .input-group-text { background: #f0f2f5; border-right: none; }
        .form-control { border-left: none; }
        .form-control:focus { border-left: none; box-shadow: none; border-color: #ced4da; }
        .btn-login {
            background: linear-gradient(135deg, #1a237e, #3949ab);
            border: none;
            color: #fff;
            padding: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.05em;
        }
        .btn-login:hover { background: linear-gradient(135deg, #283593, #3949ab); color: #fff; }
    </style>
</head>
<body>
<div class="login-card">
    <div class="login-header">
        <div class="logo-icon"><i class="bi bi-mortarboard-fill"></i></div>
        <h4 class="mb-0 fw-bold"><?= SITE_SHORT_NAME ?></h4>
        <p class="mb-0 opacity-75 small"><?= INSTITUTION_NAME ?></p>
    </div>
    <div class="login-body">
        <h5 class="mb-1 fw-semibold text-center">Welcome Back</h5>
        <p class="text-muted text-center small mb-3">Sign in to your account</p>

        <?php if ($error): ?>
        <div class="alert alert-danger alert-dismissible fade show py-2" role="alert">
            <i class="bi bi-exclamation-triangle me-1"></i><?= sanitize($error) ?>
            <button type="button" class="btn-close btn-sm" data-bs-dismiss="alert"></button>
        </div>
        <?php endif; ?>

        <?= displayFlash() ?>

        <form method="POST" action="" novalidate>
            <input type="hidden" name="csrf_token" value="<?= htmlspecialchars($_SESSION['csrf_token']) ?>">

            <div class="mb-3">
                <label for="username" class="form-label fw-semibold">Username or Email</label>
                <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-person"></i></span>
                    <input type="text" class="form-control" id="username" name="username"
                           value="<?= sanitize($username) ?>"
                           placeholder="Enter username or email"
                           autocomplete="username" required>
                </div>
            </div>

            <div class="mb-3">
                <label for="password" class="form-label fw-semibold">Password</label>
                <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-lock"></i></span>
                    <input type="password" class="form-control" id="password" name="password"
                           placeholder="Enter your password"
                           autocomplete="current-password" required>
                    <button class="btn btn-outline-secondary" type="button" id="togglePassword"
                            title="Show/hide password">
                        <i class="bi bi-eye" id="eyeIcon"></i>
                    </button>
                </div>
            </div>

            <div class="d-grid mt-4">
                <button type="submit" class="btn btn-login btn-lg">
                    <i class="bi bi-box-arrow-in-right me-1"></i>Sign In
                </button>
            </div>
        </form>

        <div class="mt-3 text-center">
            <small class="text-muted">
                Default credentials: <strong>admin</strong> / <strong>Admin@1234</strong>
            </small>
        </div>
    </div>
</div>

<script src="<?= BASE_URL ?>/assets/vendor/js/bootstrap.bundle.min.js"></script>
<script>
document.getElementById('togglePassword').addEventListener('click', function () {
    const pw  = document.getElementById('password');
    const eye = document.getElementById('eyeIcon');
    if (pw.type === 'password') {
        pw.type = 'text';
        eye.classList.replace('bi-eye', 'bi-eye-slash');
    } else {
        pw.type = 'password';
        eye.classList.replace('bi-eye-slash', 'bi-eye');
    }
});
</script>
</body>
</html>
