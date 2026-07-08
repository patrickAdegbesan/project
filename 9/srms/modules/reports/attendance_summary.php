<?php
// Redirect to attendance/report.php (the canonical attendance report)
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../includes/functions.php';
redirect(BASE_URL . '/modules/attendance/report.php');
