<?php
// ============================================================
// SRMS – API: Analytics data for dashboard charts
// Returns JSON
// ============================================================
header('Content-Type: application/json; charset=utf-8');

require_once __DIR__ . '/../config/config.php';
require_once __DIR__ . '/../config/database.php';
require_once __DIR__ . '/../includes/functions.php';

if (!isLoggedIn()) {
    http_response_code(401);
    echo json_encode(['error' => 'Unauthorised']);
    exit;
}

$currentSession = getCurrentSession();
$sessionId      = $currentSession ? (int)$currentSession['id'] : 0;

// Students per department (active)
$deptData = db()->fetchAll(
    'SELECT d.name AS dept_name, d.code, COUNT(s.id) AS count
     FROM departments d
     LEFT JOIN students s ON s.department_id = d.id AND s.status = "active"
     GROUP BY d.id ORDER BY d.name'
);

// Grade distribution (current session)
$gradeData = db()->fetchAll(
    'SELECT letter_grade, COUNT(*) AS count
     FROM grades
     WHERE session_id = :s
     GROUP BY letter_grade ORDER BY letter_grade',
    [':s' => $sessionId]
);

// Fees summary (current session)
$feesCollected = (float)(db()->fetchOne(
    'SELECT COALESCE(SUM(amount_paid),0) AS total FROM fee_payments WHERE session_id = :s',
    [':s' => $sessionId]
)['total'] ?? 0);

$feesDue = (float)(db()->fetchOne(
    'SELECT COALESCE(SUM(amount),0) AS total FROM fee_structures WHERE session_id = :s',
    [':s' => $sessionId]
)['total'] ?? 0);

// Monthly enrollment counts (last 6 months)
$monthlyEnrollment = db()->fetchAll(
    "SELECT DATE_FORMAT(created_at, '%Y-%m') AS month, COUNT(*) AS count
     FROM students
     WHERE created_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
     GROUP BY month ORDER BY month"
);

echo json_encode([
    'students_per_dept'  => $deptData,
    'grade_distribution' => $gradeData,
    'fees' => [
        'collected' => $feesCollected,
        'due'       => $feesDue,
        'pending'   => max(0, $feesDue - $feesCollected),
    ],
    'monthly_enrollment' => $monthlyEnrollment,
    'session'            => $currentSession,
]);
