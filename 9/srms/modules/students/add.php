<?php
// ============================================================
// SRMS – Add Student
// ============================================================
define('PAGE_TITLE', 'Add Student');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();
requireRole(['admin','registrar']);

$departments = getAllDepartments();
$errors      = [];
$formData    = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verifyCsrf();

    // Collect and sanitise
    $fields = [
        'matric_number','first_name','last_name','middle_name',
        'date_of_birth','gender','email','phone','address',
        'state_of_origin','nationality','religion','department_id','level',
        'admission_date','status','guardian_name','guardian_phone',
        'guardian_email','guardian_relationship','guardian_address',
    ];
    foreach ($fields as $f) {
        $formData[$f] = trim($_POST[$f] ?? '');
    }

    // Validation
    if (empty($formData['matric_number'])) $errors[] = 'Matric number is required.';
    if (empty($formData['first_name']))    $errors[] = 'First name is required.';
    if (empty($formData['last_name']))     $errors[] = 'Last name is required.';
    if (empty($formData['gender']))        $errors[] = 'Gender is required.';
    if (empty($formData['department_id'])) $errors[] = 'Department is required.';
    if (empty($formData['level']))         $errors[] = 'Level is required.';

    // Check duplicate matric
    if (!empty($formData['matric_number'])) {
        $exists = db()->fetchOne(
            'SELECT id FROM students WHERE matric_number = :m',
            [':m' => $formData['matric_number']]
        );
        if ($exists) $errors[] = 'Matric number already exists.';
    }

    if (!in_array($formData['gender'], ['male','female','other'])) {
        $errors[] = 'Invalid gender value.';
    }

    if (empty($errors)) {
        try {
            db()->execute(
                'INSERT INTO students
                 (matric_number, first_name, last_name, middle_name, date_of_birth, gender,
                  email, phone, address, state_of_origin, nationality, religion,
                  department_id, level, admission_date, status,
                  guardian_name, guardian_phone, guardian_email,
                  guardian_relationship, guardian_address)
                 VALUES
                 (:matric_number, :first_name, :last_name, :middle_name, :dob, :gender,
                  :email, :phone, :address, :state, :nationality, :religion,
                  :dept_id, :level, :admission_date, :status,
                  :g_name, :g_phone, :g_email, :g_rel, :g_address)',
                [
                    ':matric_number'  => $formData['matric_number'],
                    ':first_name'     => $formData['first_name'],
                    ':last_name'      => $formData['last_name'],
                    ':middle_name'    => $formData['middle_name'] ?: null,
                    ':dob'            => $formData['date_of_birth'] ?: null,
                    ':gender'         => $formData['gender'],
                    ':email'          => $formData['email'] ?: null,
                    ':phone'          => $formData['phone'] ?: null,
                    ':address'        => $formData['address'] ?: null,
                    ':state'          => $formData['state_of_origin'] ?: null,
                    ':nationality'    => $formData['nationality'] ?: 'Nigerian',
                    ':religion'       => $formData['religion'] ?: null,
                    ':dept_id'        => (int)$formData['department_id'],
                    ':level'          => $formData['level'],
                    ':admission_date' => $formData['admission_date'] ?: null,
                    ':status'         => $formData['status'] ?: 'active',
                    ':g_name'         => $formData['guardian_name'] ?: null,
                    ':g_phone'        => $formData['guardian_phone'] ?: null,
                    ':g_email'        => $formData['guardian_email'] ?: null,
                    ':g_rel'          => $formData['guardian_relationship'] ?: null,
                    ':g_address'      => $formData['guardian_address'] ?: null,
                ]
            );
            $newId = (int)db()->lastInsertId();
            logAudit($_SESSION['user_id'], 'ADD_STUDENT', 'students',
                "Added student {$formData['matric_number']} – {$formData['first_name']} {$formData['last_name']}");
            flashMessage('success', "Student {$formData['matric_number']} registered successfully.");
            redirect(BASE_URL . '/modules/students/view.php?id=' . $newId);
        } catch (PDOException $e) {
            $errors[] = 'Database error: ' . $e->getMessage();
        }
    }
}

$breadcrumbs = ['Students' => BASE_URL . '/modules/students/index.php', 'Add Student' => null];
require_once __DIR__ . '/../../includes/header.php';
?>

<h4 class="page-title"><i class="bi bi-person-plus me-2"></i>Register New Student</h4>

<?php if (!empty($errors)): ?>
<div class="alert alert-danger">
    <strong><i class="bi bi-exclamation-triangle me-1"></i>Please fix the following errors:</strong>
    <ul class="mb-0 mt-1">
        <?php foreach ($errors as $e): ?>
        <li><?= sanitize($e) ?></li>
        <?php endforeach; ?>
    </ul>
</div>
<?php endif; ?>

<form method="POST" novalidate>
    <input type="hidden" name="csrf_token" value="<?= htmlspecialchars($_SESSION['csrf_token']) ?>">

    <!-- PERSONAL INFORMATION -->
    <div class="card mb-3">
        <div class="card-header"><i class="bi bi-person me-1"></i>Personal Information</div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-md-4">
                    <label class="form-label">Matric Number <span class="text-danger">*</span></label>
                    <input type="text" name="matric_number" class="form-control"
                           value="<?= sanitize($formData['matric_number'] ?? '') ?>"
                           placeholder="e.g. CSC/2024/001" required>
                </div>
                <div class="col-md-4">
                    <label class="form-label">First Name <span class="text-danger">*</span></label>
                    <input type="text" name="first_name" class="form-control"
                           value="<?= sanitize($formData['first_name'] ?? '') ?>" required>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Last Name <span class="text-danger">*</span></label>
                    <input type="text" name="last_name" class="form-control"
                           value="<?= sanitize($formData['last_name'] ?? '') ?>" required>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Middle Name</label>
                    <input type="text" name="middle_name" class="form-control"
                           value="<?= sanitize($formData['middle_name'] ?? '') ?>">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Date of Birth</label>
                    <input type="date" name="date_of_birth" class="form-control"
                           value="<?= sanitize($formData['date_of_birth'] ?? '') ?>">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Gender <span class="text-danger">*</span></label>
                    <select name="gender" class="form-select" required>
                        <option value="">Select Gender</option>
                        <?php foreach (['male' => 'Male', 'female' => 'Female', 'other' => 'Other'] as $v => $l): ?>
                        <option value="<?= $v ?>" <?= ($formData['gender'] ?? '') === $v ? 'selected' : '' ?>>
                            <?= $l ?>
                        </option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Email Address</label>
                    <input type="email" name="email" class="form-control"
                           value="<?= sanitize($formData['email'] ?? '') ?>">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Phone Number</label>
                    <input type="tel" name="phone" class="form-control"
                           value="<?= sanitize($formData['phone'] ?? '') ?>">
                </div>
                <div class="col-md-4">
                    <label class="form-label">State of Origin</label>
                    <input type="text" name="state_of_origin" class="form-control"
                           value="<?= sanitize($formData['state_of_origin'] ?? '') ?>">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Nationality</label>
                    <input type="text" name="nationality" class="form-control"
                           value="<?= sanitize($formData['nationality'] ?? 'Nigerian') ?>">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Religion</label>
                    <input type="text" name="religion" class="form-control"
                           value="<?= sanitize($formData['religion'] ?? '') ?>">
                </div>
                <div class="col-12">
                    <label class="form-label">Home Address</label>
                    <textarea name="address" class="form-control" rows="2"><?= sanitize($formData['address'] ?? '') ?></textarea>
                </div>
            </div>
        </div>
    </div>

    <!-- ACADEMIC INFORMATION -->
    <div class="card mb-3">
        <div class="card-header"><i class="bi bi-mortarboard me-1"></i>Academic Information</div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-md-4">
                    <label class="form-label">Department <span class="text-danger">*</span></label>
                    <select name="department_id" class="form-select" required>
                        <option value="">Select Department</option>
                        <?php foreach ($departments as $d): ?>
                        <option value="<?= $d['id'] ?>"
                            <?= ($formData['department_id'] ?? '') == $d['id'] ? 'selected' : '' ?>>
                            <?= sanitize($d['name']) ?>
                        </option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="col-md-3">
                    <label class="form-label">Level <span class="text-danger">*</span></label>
                    <select name="level" class="form-select" required>
                        <option value="">Select Level</option>
                        <?php foreach (['100','200','300','400','500'] as $lvl): ?>
                        <option value="<?= $lvl ?>"
                            <?= ($formData['level'] ?? '') === $lvl ? 'selected' : '' ?>><?= $lvl ?>L</option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="col-md-3">
                    <label class="form-label">Status</label>
                    <select name="status" class="form-select">
                        <?php foreach (['active','suspended','graduated','withdrawn'] as $st): ?>
                        <option value="<?= $st ?>"
                            <?= ($formData['status'] ?? 'active') === $st ? 'selected' : '' ?>>
                            <?= ucfirst($st) ?>
                        </option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="col-md-3">
                    <label class="form-label">Admission Date</label>
                    <input type="date" name="admission_date" class="form-control"
                           value="<?= sanitize($formData['admission_date'] ?? '') ?>">
                </div>
            </div>
        </div>
    </div>

    <!-- GUARDIAN INFORMATION -->
    <div class="card mb-4">
        <div class="card-header"><i class="bi bi-house-heart me-1"></i>Guardian / Next of Kin</div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-md-4">
                    <label class="form-label">Guardian Full Name</label>
                    <input type="text" name="guardian_name" class="form-control"
                           value="<?= sanitize($formData['guardian_name'] ?? '') ?>">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Relationship</label>
                    <select name="guardian_relationship" class="form-select">
                        <option value="">Select</option>
                        <?php foreach (['Father','Mother','Sibling','Spouse','Uncle','Aunt','Other'] as $rel): ?>
                        <option value="<?= $rel ?>"
                            <?= ($formData['guardian_relationship'] ?? '') === $rel ? 'selected' : '' ?>>
                            <?= $rel ?>
                        </option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Guardian Phone</label>
                    <input type="tel" name="guardian_phone" class="form-control"
                           value="<?= sanitize($formData['guardian_phone'] ?? '') ?>">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Guardian Email</label>
                    <input type="email" name="guardian_email" class="form-control"
                           value="<?= sanitize($formData['guardian_email'] ?? '') ?>">
                </div>
                <div class="col-md-8">
                    <label class="form-label">Guardian Address</label>
                    <input type="text" name="guardian_address" class="form-control"
                           value="<?= sanitize($formData['guardian_address'] ?? '') ?>">
                </div>
            </div>
        </div>
    </div>

    <div class="d-flex gap-2">
        <button type="submit" class="btn btn-primary px-4">
            <i class="bi bi-check-lg me-1"></i>Register Student
        </button>
        <a href="<?= BASE_URL ?>/modules/students/index.php" class="btn btn-outline-secondary">
            Cancel
        </a>
    </div>
</form>

<?php require_once __DIR__ . '/../../includes/footer.php'; ?>
