<?php
// ============================================================
// SRMS – Sidebar Navigation
// ============================================================
$role        = $_SESSION['user_role'] ?? '';
$currentFile = $_SERVER['PHP_SELF'] ?? '';

function navItem(string $href, string $icon, string $label, string $currentFile): string {
    $active = (strpos($currentFile, $href) !== false) ? 'active' : '';
    return <<<HTML
<li class="nav-item">
    <a class="nav-link {$active}" href="{$href}">
        <i class="bi bi-{$icon} nav-icon"></i>
        <span class="nav-label">{$label}</span>
    </a>
</li>
HTML;
}
?>
<!-- SIDEBAR -->
<aside class="srms-sidebar" id="sidebar">
    <div class="sidebar-header">
        <div class="sidebar-brand">
            <i class="bi bi-mortarboard-fill me-2"></i>
            <span><?= SITE_SHORT_NAME ?></span>
        </div>
        <small class="text-muted d-block text-center sidebar-institution">
            <?= INSTITUTION_NAME ?>
        </small>
    </div>

    <div class="sidebar-body">
        <ul class="nav flex-column">
            <?= navItem(BASE_URL . '/modules/dashboard/index.php', 'speedometer2', 'Dashboard', $currentFile) ?>

            <?php if (in_array($role, ['admin','registrar'])): ?>
            <li class="nav-section-label">STUDENTS</li>
            <?= navItem(BASE_URL . '/modules/students/index.php', 'people', 'All Students', $currentFile) ?>
            <?= navItem(BASE_URL . '/modules/students/add.php', 'person-plus', 'Add Student', $currentFile) ?>
            <?php endif; ?>

            <?php if (in_array($role, ['admin','registrar','teacher'])): ?>
            <li class="nav-section-label">ACADEMICS</li>
            <?= navItem(BASE_URL . '/modules/courses/index.php', 'book', 'Courses', $currentFile) ?>
            <?= navItem(BASE_URL . '/modules/grades/index.php', 'bar-chart', 'Grades', $currentFile) ?>
            <?= navItem(BASE_URL . '/modules/grades/gpa_calculator.php', 'calculator', 'GPA Calculator', $currentFile) ?>
            <?= navItem(BASE_URL . '/modules/attendance/index.php', 'calendar-check', 'Attendance', $currentFile) ?>
            <?php endif; ?>

            <?php if (in_array($role, ['admin','registrar'])): ?>
            <li class="nav-section-label">FINANCE</li>
            <?= navItem(BASE_URL . '/modules/fees/index.php', 'cash-coin', 'Fee Management', $currentFile) ?>
            <?= navItem(BASE_URL . '/modules/fees/add_payment.php', 'receipt', 'Record Payment', $currentFile) ?>
            <?php endif; ?>

            <?php if (in_array($role, ['admin','registrar'])): ?>
            <li class="nav-section-label">REPORTS</li>
            <?= navItem(BASE_URL . '/modules/reports/index.php', 'file-earmark-text', 'Reports', $currentFile) ?>
            <?= navItem(BASE_URL . '/modules/reports/transcript.php', 'file-earmark-person', 'Transcripts', $currentFile) ?>
            <?php endif; ?>

            <?php if ($role === 'admin'): ?>
            <li class="nav-section-label">ADMINISTRATION</li>
            <?= navItem(BASE_URL . '/modules/users/index.php', 'people-fill', 'User Accounts', $currentFile) ?>
            <?= navItem(BASE_URL . '/modules/audit/index.php', 'shield-check', 'Audit Logs', $currentFile) ?>
            <?php endif; ?>
        </ul>
    </div>

    <div class="sidebar-footer">
        <a href="<?= BASE_URL ?>/modules/auth/logout.php" class="btn btn-sm btn-outline-light w-100">
            <i class="bi bi-box-arrow-right me-1"></i>Logout
        </a>
    </div>
</aside>
