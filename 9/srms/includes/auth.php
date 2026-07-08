<?php
// ============================================================
// SRMS – Authentication Functions
// ============================================================

require_once __DIR__ . '/../config/database.php';
require_once __DIR__ . '/functions.php';

/**
 * Attempt to log a user in.
 * Returns ['success' => true] or ['success' => false, 'error' => '...']
 */
function loginUser(string $username, string $password): array {
    // Look up by username OR email
    $user = db()->fetchOne(
        'SELECT * FROM users WHERE (username = :u OR email = :u2) AND status = "active" LIMIT 1',
        [':u' => $username, ':u2' => $username]
    );

    if (!$user || !password_verify($password, $user['password_hash'])) {
        return ['success' => false, 'error' => 'Invalid username or password.'];
    }

    // Regenerate session ID to prevent fixation
    session_regenerate_id(true);

    $_SESSION['user_id']       = $user['id'];
    $_SESSION['user_username'] = $user['username'];
    $_SESSION['user_role']     = $user['role'];
    $_SESSION['user_name']     = $user['full_name'];
    $_SESSION['login_time']    = time();

    // Update last login
    db()->execute(
        'UPDATE users SET last_login = NOW() WHERE id = :id',
        [':id' => $user['id']]
    );

    logAudit($user['id'], 'LOGIN', 'auth', 'User logged in successfully');

    return ['success' => true, 'role' => $user['role']];
}

/**
 * Log the current user out.
 */
function logoutUser(): void {
    if (isLoggedIn()) {
        logAudit((int)$_SESSION['user_id'], 'LOGOUT', 'auth', 'User logged out');
    }
    $_SESSION = [];
    if (ini_get('session.use_cookies')) {
        $params = session_get_cookie_params();
        setcookie(
            session_name(), '', time() - 42000,
            $params['path'], $params['domain'],
            $params['secure'], $params['httponly']
        );
    }
    session_destroy();
}

/**
 * Check login attempt throttling (stored in session for simplicity).
 */
function checkLoginThrottle(string $username): bool {
    $key     = 'login_attempts_' . md5($username);
    $timeKey = 'login_attempt_time_' . md5($username);

    $attempts = (int)($_SESSION[$key] ?? 0);
    $lastTime = (int)($_SESSION[$timeKey] ?? 0);

    // Reset after 15 minutes
    if ($lastTime && (time() - $lastTime) > 900) {
        $_SESSION[$key]     = 0;
        $_SESSION[$timeKey] = 0;
        return true;
    }

    return $attempts < 5;
}

function incrementLoginAttempts(string $username): void {
    $key     = 'login_attempts_' . md5($username);
    $timeKey = 'login_attempt_time_' . md5($username);
    $_SESSION[$key]     = ((int)($_SESSION[$key] ?? 0)) + 1;
    $_SESSION[$timeKey] = time();
}

function resetLoginAttempts(string $username): void {
    $key     = 'login_attempts_' . md5($username);
    $timeKey = 'login_attempt_time_' . md5($username);
    $_SESSION[$key]     = 0;
    $_SESSION[$timeKey] = 0;
}

function getRemainingAttempts(string $username): int {
    $key = 'login_attempts_' . md5($username);
    return max(0, 5 - (int)($_SESSION[$key] ?? 0));
}
