<?php
// ============================================================
// SRMS – Header (HTML head + top navbar)
// ============================================================
if (!defined('PAGE_TITLE')) define('PAGE_TITLE', 'Dashboard');
?>
<!DOCTYPE html>
<html lang="en" data-bs-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Student Record Management System">
    <title><?= sanitize(PAGE_TITLE) ?> – <?= SITE_SHORT_NAME ?></title>

    <!-- Bootstrap 5.3 -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <!-- Custom styles -->
    <link rel="stylesheet" href="<?= BASE_URL ?>/assets/css/style.css">
</head>
<body>
<!-- TOP NAVBAR -->
<nav class="navbar navbar-expand-lg navbar-dark srms-topbar fixed-top">
    <div class="container-fluid">
        <!-- Sidebar toggle (mobile) -->
        <button class="btn btn-link text-white me-2 sidebar-toggle d-lg-none" type="button" id="sidebarToggleBtn">
            <i class="bi bi-list fs-4"></i>
        </button>

        <a class="navbar-brand fw-bold" href="<?= BASE_URL ?>/modules/dashboard/index.php">
            <i class="bi bi-mortarboard-fill me-1"></i><?= SITE_SHORT_NAME ?>
        </a>

        <div class="d-flex align-items-center ms-auto gap-2">
            <!-- Dark mode toggle -->
            <button class="btn btn-sm btn-outline-light" id="darkModeToggle" title="Toggle dark mode">
                <i class="bi bi-moon-fill" id="darkModeIcon"></i>
            </button>

            <!-- User dropdown -->
            <div class="dropdown">
                <button class="btn btn-sm btn-outline-light dropdown-toggle d-flex align-items-center gap-1"
                        type="button" data-bs-toggle="dropdown">
                    <i class="bi bi-person-circle"></i>
                    <span class="d-none d-md-inline"><?= sanitize($_SESSION['user_name'] ?? 'User') ?></span>
                </button>
                <ul class="dropdown-menu dropdown-menu-end">
                    <li><h6 class="dropdown-header"><?= sanitize($_SESSION['user_role'] ?? '') ?></h6></li>
                    <li><a class="dropdown-item" href="<?= BASE_URL ?>/modules/users/edit.php?id=<?= (int)($_SESSION['user_id'] ?? 0) ?>">
                        <i class="bi bi-person me-1"></i>My Profile</a></li>
                    <li><hr class="dropdown-divider"></li>
                    <li><a class="dropdown-item text-danger" href="<?= BASE_URL ?>/modules/auth/logout.php">
                        <i class="bi bi-box-arrow-right me-1"></i>Logout</a></li>
                </ul>
            </div>
        </div>
    </div>
</nav>

<!-- WRAPPER -->
<div class="srms-wrapper">
<?php require_once __DIR__ . '/sidebar.php'; ?>
<!-- MAIN CONTENT -->
<main class="srms-main" id="mainContent">
    <div class="container-fluid px-4 py-3">
        <!-- Flash message -->
        <?= displayFlash() ?>
        <!-- Breadcrumb placeholder -->
        <?php if (!empty($breadcrumbs)): ?>
        <nav aria-label="breadcrumb" class="mb-3">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="<?= BASE_URL ?>/modules/dashboard/index.php">
                    <i class="bi bi-house"></i></a></li>
                <?php foreach ($breadcrumbs as $label => $url): ?>
                    <?php if ($url): ?>
                        <li class="breadcrumb-item"><a href="<?= sanitize($url) ?>"><?= sanitize($label) ?></a></li>
                    <?php else: ?>
                        <li class="breadcrumb-item active"><?= sanitize($label) ?></li>
                    <?php endif; ?>
                <?php endforeach; ?>
            </ol>
        </nav>
        <?php endif; ?>
