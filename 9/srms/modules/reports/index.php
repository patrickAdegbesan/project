<?php
define('PAGE_TITLE', 'Reports');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();
requireRole(['admin','registrar']);

$breadcrumbs = ['Reports' => null];
require_once __DIR__ . '/../../includes/header.php';
?>

<h4 class="page-title"><i class="bi bi-file-earmark-text me-2"></i>Reports Centre</h4>

<div class="row g-3">
    <div class="col-sm-6 col-lg-4">
        <div class="card h-100 text-center p-3">
            <div class="fs-1 text-primary mb-2"><i class="bi bi-file-earmark-person"></i></div>
            <h5>Academic Transcript</h5>
            <p class="text-muted small">Generate a full academic transcript for any student.</p>
            <a href="<?= BASE_URL ?>/modules/reports/transcript.php" class="btn btn-primary btn-sm mt-auto">
                Open
            </a>
        </div>
    </div>
    <div class="col-sm-6 col-lg-4">
        <div class="card h-100 text-center p-3">
            <div class="fs-1 text-success mb-2"><i class="bi bi-list-ul"></i></div>
            <h5>Class List</h5>
            <p class="text-muted small">Print a class list by department, level, or course.</p>
            <a href="<?= BASE_URL ?>/modules/reports/class_list.php" class="btn btn-success btn-sm mt-auto">
                Open
            </a>
        </div>
    </div>
    <div class="col-sm-6 col-lg-4">
        <div class="card h-100 text-center p-3">
            <div class="fs-1 text-warning mb-2"><i class="bi bi-calendar-check"></i></div>
            <h5>Attendance Summary</h5>
            <p class="text-muted small">View and print attendance report per course/department.</p>
            <a href="<?= BASE_URL ?>/modules/attendance/report.php" class="btn btn-warning btn-sm mt-auto">
                Open
            </a>
        </div>
    </div>
    <div class="col-sm-6 col-lg-4">
        <div class="card h-100 text-center p-3">
            <div class="fs-1 text-info mb-2"><i class="bi bi-calculator"></i></div>
            <h5>GPA / CGPA Report</h5>
            <p class="text-muted small">Detailed GPA and CGPA breakdown per student.</p>
            <a href="<?= BASE_URL ?>/modules/grades/gpa_calculator.php" class="btn btn-info btn-sm mt-auto">
                Open
            </a>
        </div>
    </div>
    <div class="col-sm-6 col-lg-4">
        <div class="card h-100 text-center p-3">
            <div class="fs-1 text-danger mb-2"><i class="bi bi-cash-coin"></i></div>
            <h5>Fee Statement</h5>
            <p class="text-muted small">Individual student fee statement with payment history.</p>
            <a href="<?= BASE_URL ?>/modules/fees/index.php" class="btn btn-danger btn-sm mt-auto">
                Open
            </a>
        </div>
    </div>
    <div class="col-sm-6 col-lg-4">
        <div class="card h-100 text-center p-3">
            <div class="fs-1 text-secondary mb-2"><i class="bi bi-shield-check"></i></div>
            <h5>Audit Log</h5>
            <p class="text-muted small">System activity and security audit trail.</p>
            <a href="<?= BASE_URL ?>/modules/audit/index.php" class="btn btn-secondary btn-sm mt-auto">
                Open
            </a>
        </div>
    </div>
</div>

<?php require_once __DIR__ . '/../../includes/footer.php'; ?>
