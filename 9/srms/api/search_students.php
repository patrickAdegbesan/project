<?php
// ============================================================
// SRMS – API: Search Students (AJAX)
// Returns JSON array
// ============================================================
header('Content-Type: application/json; charset=utf-8');

require_once __DIR__ . '/../config/config.php';
require_once __DIR__ . '/../config/database.php';
require_once __DIR__ . '/../includes/functions.php';

// Must be logged in
if (!isLoggedIn()) {
    http_response_code(401);
    echo json_encode(['error' => 'Unauthorised']);
    exit;
}

$q = trim($_GET['q'] ?? '');

if (strlen($q) < 2) {
    echo json_encode([]);
    exit;
}

$results = db()->fetchAll(
    'SELECT s.id, s.matric_number,
            CONCAT(s.first_name, " ", s.last_name) AS full_name,
            d.code AS dept_code, s.level, s.status
     FROM students s
     JOIN departments d ON d.id = s.department_id
     WHERE s.matric_number LIKE :q
        OR s.first_name LIKE :q
        OR s.last_name LIKE :q
        OR s.email LIKE :q
     ORDER BY s.last_name, s.first_name
     LIMIT 15',
    [':q' => '%' . $q . '%']
);

echo json_encode($results);
