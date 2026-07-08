<?php
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();
requireRole(['admin']);

$id = (int)($_GET['id'] ?? 0);

// Prevent self-deletion
if ($id === (int)$_SESSION['user_id']) {
    flashMessage('danger', 'You cannot delete your own account.');
    redirect(BASE_URL . '/modules/users/index.php');
}

$user = db()->fetchOne('SELECT * FROM users WHERE id = :id', [':id' => $id]);
if (!$user) {
    flashMessage('danger', 'User not found.');
} else {
    db()->execute('DELETE FROM users WHERE id = :id', [':id' => $id]);
    logAudit($_SESSION['user_id'], 'DELETE_USER', 'users',
        "Deleted user: {$user['username']} ({$user['full_name']})");
    flashMessage('success', "User {$user['username']} deleted.");
}

redirect(BASE_URL . '/modules/users/index.php');
