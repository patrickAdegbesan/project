<?php
// ============================================================
// SRMS – Application Configuration
// ============================================================

// --- Error reporting (set to 0 in production) ---
error_reporting(E_ALL);
ini_set('display_errors', 1);

// --- Database credentials ---
define('DB_HOST', 'localhost');
define('DB_NAME', 'srms');
define('DB_USER', 'root');
define('DB_PASS', '');
define('DB_CHARSET', 'utf8mb4');

// --- Application constants ---
define('BASE_URL', 'http://localhost/srms');
define('SITE_NAME', 'Student Record Management System');
define('SITE_SHORT_NAME', 'SRMS');
define('INSTITUTION_NAME', 'Federal University of Technology');
define('INSTITUTION_ADDRESS', 'Minna, Niger State, Nigeria');

// --- Paths ---
define('ROOT_PATH', dirname(__DIR__));
define('UPLOAD_PATH', ROOT_PATH . '/assets/uploads/');
define('UPLOAD_URL', BASE_URL . '/assets/uploads/');

// --- Grading constants ---
define('MAX_CA_SCORE', 30);
define('MAX_EXAM_SCORE', 70);

// --- Session configuration ---
if (session_status() === PHP_SESSION_NONE) {
    ini_set('session.cookie_httponly', 1);
    ini_set('session.use_strict_mode', 1);
    ini_set('session.cookie_samesite', 'Lax');
    session_start();
}

// --- Timezone ---
date_default_timezone_set('Africa/Lagos');

// --- CSRF helper ---
if (empty($_SESSION['csrf_token'])) {
    $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
}
