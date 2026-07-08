<?php
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';
require_once __DIR__ . '/../../includes/auth.php';

logoutUser();
flashMessage('success', 'You have been logged out successfully.');
redirect(BASE_URL . '/modules/auth/login.php');
