<?php
// ============================================================
// SRMS – Edit Student
// ============================================================
define('PAGE_TITLE', 'Edit Student');
require_once __DIR__ . '/../../config/config.php';
require_once __DIR__ . '/../../config/database.php';
require_once __DIR__ . '/../../includes/functions.php';

requireLogin();
requireRole(['admin','registrar']);

$id      = (int)($_GET['id'] ?? 0);
$student = getStudentById($id);
if (!$student) {
    flashMessage('danger', 'Student not found.');
    redirect(BASE_URL . '/modules/students/index.php');
}

$departments = getAllDepartments();
$errors      = [];
$formData    = $student; // pre-fill with existing data

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verifyCsrf();

    $fields = [
        'matric_number','first_name','last_name','middle_name',
        'date_of_birth','gender','email','phone','address',
        'state_of_origin','nationality','religion','department_id','level',
        'admission_date','graduation_date','status',
        'guardian_name','guardian_phone','guardian_email',
        'guardian_relationship','guardian_address',
    ];
    foreach ($fields as $f) {
        $formData[$f] = trim($_POST[$f] ?? '');
    }

    if (empty($formData['first_name']))     $errors[] = 'First name is required.';
    if (empty($formData['last_name']))      $errors[] = 'Last name is required.';
    if (empty($formData['matric_number']))  $errors[] = 'Matric number is required.';

    // Check duplicate matric (exclude self)
    $dup = db()->fetchOne(
        'SELECT id FROM students WHERE matric_number = :m AND id != :id',
        [':m' => $formData['matric_number'], ':id' => $id]
    );
    if ($dup) $errors[] = 'Matric number already used by another student.';

    if (empty($errors)) {
        db()->execute(
            'UPDATE students SET
                matric_number=:matric, first_name=:fn, last_name=:ln, middle_name=:mn,
                date_of_birth=:dob, gender=:gender, email=:email, phone=:phone,
                address=:address, state_of_origin=:state, nationality=:nationality,
                religion=:religion, department_id=:dept, level=:level,
                admission_date=:adm, graduation_date=:grad, status=:status,
                guardian_name=:gn, guardian_phone=:gp, guardian_email=:ge,
                guardian_relationship=:gr, guardian_address=:ga
             WHERE id=:id',
            [
                ':matric'     => $formData['matric_number'],
                ':fn'         => $formData['first_name'],
                ':ln'         => $formData['last_name'],
                ':mn'         => $formData['middle_name'] ?: null,
                ':dob'        => $formData['date_of_birth'] ?: null,
                ':gender'     => $formData['gender'],
                ':email'      => $formData['email'] ?: null,
                ':phone'      => $formData['phone'] ?: null,
                ':address'    => $formData['address'] ?: null,
                ':state'      => $formData['state_of_origin'] ?: null,
                ':nationality'=> $formData['nationality'] ?: 'Nigerian',
                ':religion'   => $formData['religion'] ?: null,
                ':dept'       => (int)$formData['department_id'],
                ':level'      => $formData['level'],
                ':adm'        => $formData['admission_date'] ?: null,
                ':grad'       => $formData['graduation_date'] ?: null,
                ':status'     => $formData['status'],
                ':gn'         => $formData['guardian_name'] ?: null,
                ':gp'         => $formData['guardian_phone'] ?: null,
                ':ge'         => $formData['guardian_email'] ?: null,
                ':gr'         => $formData['guardian_relationship'] ?: null,
                ':ga'         => $formData['guardian_address'] ?: null,
                ':id'         => $id,
            ]
        );
        logAudit($_SESSION['user_id'], 'EDIT_STUDENT', 'students',
            "Updated student {$formData['matric_number']}");
        flashMessage('success', 'Student record updated successfully.');
        redirect(BASE_URL . '/modules/students/view.php?id=' . $id);
    }
}

$breadcrumbs = [
    'Students' => BASE_URL . '/modules/students/index.php',
    'Edit: ' . sanitize($student['first_name'] . ' ' . $student['last_name']) => null,
];
require_once __DIR__ . '/../../includes/header.php';
?>

<h4 class="page-title"><i class="bi bi-pencil me-2"></i>Edit Student Record</h4>

<?php if (!empty($errors)): ?>
<div class="alert alert-danger">
    <ul class="mb-0">
        <?php foreach ($errors as $e): ?><li><?= sanitize($e) ?></li><?php endforeach; ?>
    </ul>
</div>
<?php endif; ?>

<form method="POST" novalidate>
    <input type="hidden" name="csrf_token" value="<?= htmlspecialchars($_SESSION['csrf_token']) ?>">

    <div class="card mb-3">
        <div class="card-header"><i class="bi bi-person me-1"></i>Personal Information</div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-md-4">
                    <label class="form-label">Matric Number <span class="text-danger">*</span></label>
                    <input type="text" name="matric_number" class="form-control"
                           value="<?= sanitize($formData['matric_number']) ?>" required>
                </div>
                <div class="col-md-4">
                    <label class="form-label">First Name <span class="text-danger">*</span></label>
                    <input type="text" name="first_name" class="form-control"
                           value="<?= sanitize($formData['first_name']) ?>" required>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Last Name <span class="text-danger">*</span></label>
                    <input type="text" name="last_name" class="form-control"
                           value="<?= sanitize($formData['last_name']) ?>" required>
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
                    <label class="form-label">Gender</label>
                    <select name="gender" class="form-select">
                        <?php foreach (['male'=>'Male','female'=>'Female','other'=>'Other'] as $v=>$l): ?>
                        <option value="<?= $v ?>" <?= $formData['gender'] === $v ? 'selected' : '' ?>><?= $l ?></option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Email</label>
                    <input type="email" name="email" class="form-control"
                           value="<?= sanitize($formData['email'] ?? '') ?>">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Phone</label>
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
                    <label class="form-label">Address</label>
                    <textarea name="address" class="form-control" rows="2"><?= sanitize($formData['address'] ?? '') ?></textarea>
                </div>
            </div>
        </div>
    </div>

    <div class="card mb-3">
        <div class="card-header"><i class="bi bi-mortarboard me-1"></i>Academic Information</div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-md-4">
                    <label class="form-label">Department</label>
                    <select name="department_id" class="form-select">
                        <?php foreach ($departments as $d): ?>
                        <option value="<?= $d['id'] ?>"
                            <?= $formData['department_id'] == $d['id'] ? 'selected' : '' ?>>
                            <?= sanitize($d['name']) ?>
                        </option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="col-md-3">
                    <label class="form-label">Level</label>
                    <select name="level" class="form-select">
                        <?php foreach (['100','200','300','400','500'] as $lvl): ?>
                        <option value="<?= $lvl ?>" <?= $formData['level'] === $lvl ? 'selected' : '' ?>>
                            <?= $lvl ?>L
                        </option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="col-md-3">
                    <label class="form-label">Status</label>
                    <select name="status" class="form-select">
                        <?php foreach (['active','suspended','graduated','withdrawn'] as $st): ?>
                        <option value="<?= $st ?>" <?= $formData['status'] === $st ? 'selected' : '' ?>>
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
                <div class="col-md-3">
                    <label class="form-label">Graduation Date</label>
                    <input type="date" name="graduation_date" class="form-control"
                           value="<?= sanitize($formData['graduation_date'] ?? '') ?>">
                </div>
            </div>
        </div>
    </div>

    <div class="card mb-4">
        <div class="card-header"><i class="bi bi-house-heart me-1"></i>Guardian Information</div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-md-4">
                    <label class="form-label">Guardian Name</label>
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
            <i class="bi bi-check-lg me-1"></i>Save Changes
        </button>
        <a href="<?= BASE_URL ?>/modules/students/view.php?id=<?= $id ?>"
           class="btn btn-outline-secondary">Cancel</a>
    </div>
</form>

<?php require_once __DIR__ . '/../../includes/footer.php'; ?>
