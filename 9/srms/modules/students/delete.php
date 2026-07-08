<?php
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();
requireRole(['admin']);

$id = (int)($_GET['id'] ?? 0);
$student = getStudentById($id);

if (!$student) {
    flashMessage('danger', 'Student not found.');
    redirect(BASE_URL . '/modules/students/index.php');
}

db()->execute('DELETE FROM students WHERE id = :id', [':id' => $id]);
logAudit($_SESSION['user_id'], 'DELETE_STUDENT', 'students',
    "Deleted student {$student['matric_number']} – {$student['first_name']} {$student['last_name']}");

flashMessage('success', "Student {$student['matric_number']} deleted successfully.");
redirect(BASE_URL . '/modules/students/index.php');
