<?php
// ============================================================
// SRMS – Global Helper Functions
// ============================================================

require_once __DIR__ . '/../config/database.php';

// ------------------------------------------------------------
// GRADE FUNCTIONS
// ------------------------------------------------------------

/**
 * Return letter grade, grade points for a numeric score.
 * Scale: A(70-100)=4.0, B(60-69)=3.0, C(50-59)=2.0, D(45-49)=1.0, F(0-44)=0.0
 */
function getLetterGrade(float $score): array {
    if ($score >= 70) return ['letter' => 'A', 'points' => 4.0];
    if ($score >= 60) return ['letter' => 'B', 'points' => 3.0];
    if ($score >= 50) return ['letter' => 'C', 'points' => 2.0];
    if ($score >= 45) return ['letter' => 'D', 'points' => 1.0];
    return ['letter' => 'F', 'points' => 0.0];
}

/**
 * Calculate GPA for a student in a specific session.
 * GPA = Σ(grade_points × credit_units) / Σ(credit_units)
 */
function calculateGPA(int $student_id, int $session_id): float {
    $rows = db()->fetchAll(
        'SELECT grade_points, credit_units FROM grades WHERE student_id = :s AND session_id = :ss',
        [':s' => $student_id, ':ss' => $session_id]
    );
    if (empty($rows)) return 0.0;

    $totalWeighted = 0.0;
    $totalUnits    = 0;
    foreach ($rows as $row) {
        $totalWeighted += (float)$row['grade_points'] * (int)$row['credit_units'];
        $totalUnits    += (int)$row['credit_units'];
    }
    if ($totalUnits === 0) return 0.0;
    return round($totalWeighted / $totalUnits, 2);
}

/**
 * Calculate CGPA for a student across ALL sessions.
 */
function calculateCGPA(int $student_id): float {
    $rows = db()->fetchAll(
        'SELECT grade_points, credit_units FROM grades WHERE student_id = :s',
        [':s' => $student_id]
    );
    if (empty($rows)) return 0.0;

    $totalWeighted = 0.0;
    $totalUnits    = 0;
    foreach ($rows as $row) {
        $totalWeighted += (float)$row['grade_points'] * (int)$row['credit_units'];
        $totalUnits    += (int)$row['credit_units'];
    }
    if ($totalUnits === 0) return 0.0;
    return round($totalWeighted / $totalUnits, 2);
}

/**
 * Return class standing based on CGPA.
 */
function getClassStanding(float $cgpa): string {
    if ($cgpa >= 3.5) return 'First Class';
    if ($cgpa >= 3.0) return 'Second Class Upper';
    if ($cgpa >= 2.0) return 'Second Class Lower';
    if ($cgpa >= 1.0) return 'Third Class';
    return 'Fail';
}

// ------------------------------------------------------------
// ATTENDANCE FUNCTIONS
// ------------------------------------------------------------

/**
 * Calculate attendance rate (%) for a student in a course/session.
 * Rate = (present + late) / total × 100
 */
function getAttendanceRate(int $student_id, int $course_id, int $session_id): float {
    $row = db()->fetchOne(
        'SELECT
            COUNT(*) AS total,
            SUM(status IN ("present","late")) AS attended
         FROM attendance
         WHERE student_id = :s AND course_id = :c AND session_id = :ss',
        [':s' => $student_id, ':c' => $course_id, ':ss' => $session_id]
    );
    if (!$row || (int)$row['total'] === 0) return 0.0;
    return round(((float)$row['attended'] / (int)$row['total']) * 100, 1);
}

// ------------------------------------------------------------
// FEE FUNCTIONS
// ------------------------------------------------------------

/**
 * Get fee balance for a student in a session.
 * Balance = total_due - total_paid
 */
function getFeeBalance(int $student_id, int $session_id): array {
    // Total due: sum of applicable fee structures
    $student = db()->fetchOne(
        'SELECT department_id, level FROM students WHERE id = :s',
        [':s' => $student_id]
    );
    if (!$student) return ['due' => 0, 'paid' => 0, 'balance' => 0];

    $due_row = db()->fetchOne(
        'SELECT COALESCE(SUM(amount),0) AS total_due
         FROM fee_structures
         WHERE session_id = :ss
           AND (department_id IS NULL OR department_id = :d)
           AND (level = "all" OR level = :l)',
        [':ss' => $session_id, ':d' => $student['department_id'], ':l' => $student['level']]
    );

    $paid_row = db()->fetchOne(
        'SELECT COALESCE(SUM(amount_paid),0) AS total_paid
         FROM fee_payments
         WHERE student_id = :s AND session_id = :ss',
        [':s' => $student_id, ':ss' => $session_id]
    );

    $due  = (float)$due_row['total_due'];
    $paid = (float)$paid_row['total_paid'];

    return [
        'due'     => $due,
        'paid'    => $paid,
        'balance' => $due - $paid,
    ];
}

// ------------------------------------------------------------
// AUDIT LOG
// ------------------------------------------------------------

/**
 * Write an audit log entry.
 */
function logAudit(int $user_id, string $action, string $module, string $description): void {
    $ip = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
    db()->execute(
        'INSERT INTO audit_logs (user_id, action, module, description, ip_address)
         VALUES (:u, :a, :m, :d, :ip)',
        [':u' => $user_id, ':a' => $action, ':m' => $module, ':d' => $description, ':ip' => $ip]
    );
}

// ------------------------------------------------------------
// SECURITY / SANITISATION
// ------------------------------------------------------------

/**
 * Sanitise a value for safe HTML output.
 */
function sanitize(mixed $input): string {
    return htmlspecialchars(trim((string)$input), ENT_QUOTES, 'UTF-8');
}

/**
 * Validate and return a clean CSRF token (throws on mismatch).
 */
function verifyCsrf(): void {
    $token = $_POST['csrf_token'] ?? '';
    if (!hash_equals($_SESSION['csrf_token'] ?? '', $token)) {
        flashMessage('danger', 'Invalid CSRF token. Please try again.');
        redirect(BASE_URL . '/modules/dashboard/index.php');
    }
}

// ------------------------------------------------------------
// NAVIGATION / FLASH
// ------------------------------------------------------------

function redirect(string $url): void {
    header('Location: ' . $url);
    exit;
}

function flashMessage(string $type, string $message): void {
    $_SESSION['flash'] = ['type' => $type, 'message' => $message];
}

function displayFlash(): string {
    if (!isset($_SESSION['flash'])) return '';
    $flash = $_SESSION['flash'];
    unset($_SESSION['flash']);
    $type = sanitize($flash['type']);
    $msg  = sanitize($flash['message']);
    return <<<HTML
<div class="alert alert-{$type} alert-dismissible fade show" role="alert">
    {$msg}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
HTML;
}

// ------------------------------------------------------------
// FINANCIAL HELPERS
// ------------------------------------------------------------

/**
 * Format a number as Nigerian Naira.
 */
function formatCurrency(float $amount): string {
    return '₦' . number_format($amount, 2);
}

/**
 * Generate a unique receipt number.
 */
function generateReceiptNumber(): string {
    return 'RCP-' . date('Ymd') . '-' . strtoupper(substr(bin2hex(random_bytes(3)), 0, 6));
}

// ------------------------------------------------------------
// AUTHENTICATION HELPERS
// ------------------------------------------------------------

function isLoggedIn(): bool {
    return !empty($_SESSION['user_id']);
}

function requireLogin(): void {
    if (!isLoggedIn()) {
        flashMessage('warning', 'Please log in to access this page.');
        redirect(BASE_URL . '/modules/auth/login.php');
    }
}

/**
 * Require one of the given roles; abort if not allowed.
 * @param string|array $roles
 */
function requireRole(string|array $roles): void {
    requireLogin();
    $roles = (array)$roles;
    if (!in_array($_SESSION['user_role'] ?? '', $roles, true)) {
        flashMessage('danger', 'You do not have permission to access that page.');
        redirect(BASE_URL . '/modules/dashboard/index.php');
    }
}

function currentUser(): array {
    if (!isLoggedIn()) return [];
    return db()->fetchOne(
        'SELECT id, username, email, role, full_name, phone FROM users WHERE id = :id',
        [':id' => $_SESSION['user_id']]
    ) ?: [];
}

// ------------------------------------------------------------
// QUERY HELPERS
// ------------------------------------------------------------

function getStudentsByDept(int $dept_id): array {
    return db()->fetchAll(
        'SELECT s.*, d.name AS dept_name
         FROM students s
         JOIN departments d ON d.id = s.department_id
         WHERE s.department_id = :d
         ORDER BY s.last_name, s.first_name',
        [':d' => $dept_id]
    );
}

function getCoursesByDept(int $dept_id, string $level, string $semester): array {
    return db()->fetchAll(
        'SELECT * FROM courses
         WHERE department_id = :d AND level = :l AND semester = :s AND status = "active"
         ORDER BY course_code',
        [':d' => $dept_id, ':l' => $level, ':s' => $semester]
    );
}

function getCurrentSession(): array|false {
    return db()->fetchOne('SELECT * FROM academic_sessions WHERE is_current = 1 LIMIT 1');
}

function getAllDepartments(): array {
    return db()->fetchAll('SELECT * FROM departments ORDER BY name');
}

function getAllSessions(): array {
    return db()->fetchAll('SELECT * FROM academic_sessions ORDER BY id DESC');
}

function getStudentById(int $id): array|false {
    return db()->fetchOne(
        'SELECT s.*, d.name AS dept_name, d.code AS dept_code
         FROM students s
         JOIN departments d ON d.id = s.department_id
         WHERE s.id = :id',
        [':id' => $id]
    );
}

function formatDate(string|null $date, string $format = 'd/m/Y'): string {
    if (empty($date)) return 'N/A';
    try {
        return (new DateTime($date))->format($format);
    } catch (Exception) {
        return $date;
    }
}

function statusBadge(string $status): string {
    $map = [
        'active'    => 'success',
        'suspended' => 'warning',
        'graduated' => 'info',
        'withdrawn' => 'danger',
        'inactive'  => 'secondary',
        'present'   => 'success',
        'absent'    => 'danger',
        'late'      => 'warning',
        'excused'   => 'info',
    ];
    $color = $map[strtolower($status)] ?? 'secondary';
    return '<span class="badge bg-' . $color . '">' . ucfirst(sanitize($status)) . '</span>';
}
