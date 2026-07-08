<?php
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();
requireRole(['admin']);

$id = (int)($_GET['id'] ?? 0);
$course = db()->fetchOne('SELECT * FROM courses WHERE id = :id', [':id' => $id]);

if (!$course) {
    flashMessage('danger', 'Course not found.');
} else {
    db()->execute('DELETE FROM courses WHERE id = :id', [':id' => $id]);
    logAudit($_SESSION['user_id'], 'DELETE_COURSE', 'courses', "Deleted course {$course['course_code']}");
    flashMessage('success', "Course {$course['course_code']} deleted.");
}

redirect(BASE_URL . '/modules/courses/index.php');
