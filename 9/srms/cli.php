<?php
/**
 * SRMS — Terminal client.
 *
 * The functionality of the web application, from the terminal: login,
 * students, courses, grades (with the same GPA/CGPA logic), attendance,
 * fees, reports and the audit log. It loads the same configuration,
 * database connection and business functions (includes/functions.php)
 * as the website, so everything reads and writes the same MySQL
 * database. Works fully offline (local database only).
 *
 * Usage:  php cli.php
 */

if (PHP_SAPI !== 'cli') {
    die("cli.php must be run from the command line\n");
}

session_start();                      // functions.php uses $_SESSION

require_once __DIR__ . '/config/config.php';
require_once __DIR__ . '/config/database.php';
require_once __DIR__ . '/includes/functions.php';

$db = Database::getInstance()->getConnection();

function ask(string $prompt, string $default = ''): string
{
    $suffix = $default !== '' ? " [$default]" : '';
    echo $prompt . $suffix . ': ';
    $line = trim(fgets(STDIN) ?: '');
    return $line === '' ? $default : $line;
}

function askSecret(string $prompt): string
{
    // Hide input when possible; fall back to plain read.
    if (function_exists('shell_exec') && strncasecmp(PHP_OS, 'WIN', 3) !== 0) {
        echo $prompt . ': ';
        shell_exec('stty -echo 2>/dev/null');
        $line = trim(fgets(STDIN) ?: '');
        shell_exec('stty echo 2>/dev/null');
        echo "\n";
        return $line;
    }
    return ask($prompt);
}

function table(array $rows, array $cols): void
{
    if (!$rows) {
        echo "  (no records)\n";
        return;
    }
    $w = [];
    foreach ($cols as $c) {
        $w[$c] = strlen($c);
        foreach ($rows as $r) {
            $w[$c] = max($w[$c], strlen((string)($r[$c] ?? '')));
        }
    }
    $line = '  ';
    foreach ($cols as $c) $line .= str_pad(strtoupper($c), $w[$c] + 2);
    echo $line . "\n";
    foreach ($rows as $r) {
        $line = '  ';
        foreach ($cols as $c) $line .= str_pad((string)($r[$c] ?? ''), $w[$c] + 2);
        echo $line . "\n";
    }
}

// ---------------------------------------------------------------------------
// Auth (same rules as modules/auth/login.php)
// ---------------------------------------------------------------------------

function login(PDO $db): ?array
{
    for ($i = 0; $i < 5; $i++) {
        $username = ask('Username or email');
        $password = askSecret('Password');
        $stmt = $db->prepare(
            "SELECT * FROM users
             WHERE (username = ? OR email = ?) AND status = 'active'");
        $stmt->execute([$username, $username]);
        $user = $stmt->fetch();
        if ($user && password_verify($password, $user['password_hash'])) {
            $_SESSION['user_id'] = (int)$user['id'];
            $_SESSION['role'] = $user['role'];
            $_SESSION['full_name'] = $user['full_name'];
            logAudit((int)$user['id'], 'login', 'auth', 'CLI login');
            echo "\nWelcome, {$user['full_name']} ({$user['role']})\n";
            return $user;
        }
        echo "Invalid username or password.\n";
    }
    return null;
}

// ---------------------------------------------------------------------------
// Students
// ---------------------------------------------------------------------------

function studentsList(PDO $db): void
{
    $q = ask('Search (name/matric, blank = all)');
    $sql = "SELECT s.id, s.matric_number,
                   CONCAT(s.first_name, ' ', s.last_name) AS name,
                   d.code AS dept, s.level, s.status
            FROM students s JOIN departments d ON d.id = s.department_id";
    $params = [];
    if ($q !== '') {
        $sql .= " WHERE s.matric_number LIKE ? OR s.first_name LIKE ? OR s.last_name LIKE ?";
        $params = ["%$q%", "%$q%", "%$q%"];
    }
    $sql .= " ORDER BY s.id LIMIT 50";
    $stmt = $db->prepare($sql);
    $stmt->execute($params);
    table($stmt->fetchAll(), ['id', 'matric_number', 'name', 'dept', 'level', 'status']);
}

function studentAdd(PDO $db, array $me): void
{
    echo "\n== New student ==\n";
    table(getAllDepartments(), ['id', 'name', 'code']);
    $stmt = $db->prepare(
        "INSERT INTO students (matric_number, first_name, last_name, gender,
                               email, phone, department_id, level, admission_date)
         VALUES (?,?,?,?,?,?,?,?,CURDATE())");
    $stmt->execute([
        ask('Matric number'),
        ask('First name'),
        ask('Last name'),
        ask('Gender (male/female/other)', 'male'),
        ask('Email'),
        ask('Phone'),
        (int)ask('Department id'),
        ask('Level (100-500)', '100'),
    ]);
    $id = (int)$db->lastInsertId();
    logAudit((int)$me['id'], 'create', 'students', "CLI: added student #$id");
    echo "Student #$id created.\n";
}

function studentProfile(PDO $db): void
{
    $id = (int)ask('Student id');
    $s = getStudentById($id);
    if (!$s) {
        echo "Not found.\n";
        return;
    }
    foreach (['matric_number', 'first_name', 'last_name', 'gender', 'email',
              'phone', 'level', 'status'] as $k) {
        printf("  %-14s: %s\n", $k, $s[$k] ?? '');
    }
    $cgpa = calculateCGPA($id);
    printf("  %-14s: %.2f (%s)\n", 'CGPA', $cgpa, getClassStanding($cgpa));
    $session = getCurrentSession();
    if ($session) {
        $bal = getFeeBalance($id, (int)$session['id']);
        printf("  %-14s: paid %s of %s (balance %s)\n", 'fees',
            formatCurrency($bal['paid']), formatCurrency($bal['due']),
            formatCurrency($bal['balance']));
    }
}

// ---------------------------------------------------------------------------
// Courses
// ---------------------------------------------------------------------------

function coursesList(PDO $db): void
{
    $rows = $db->query(
        "SELECT c.id, c.course_code, c.title, c.credit_units, c.level,
                c.semester, d.code AS dept
         FROM courses c JOIN departments d ON d.id = c.department_id
         ORDER BY c.course_code LIMIT 100")->fetchAll();
    table($rows, ['id', 'course_code', 'title', 'credit_units', 'level', 'semester', 'dept']);
}

function courseAdd(PDO $db, array $me): void
{
    table(getAllDepartments(), ['id', 'name', 'code']);
    $stmt = $db->prepare(
        "INSERT INTO courses (course_code, title, credit_units, level,
                              semester, department_id)
         VALUES (?,?,?,?,?,?)");
    $stmt->execute([
        strtoupper(ask('Course code (e.g. CSC301)')),
        ask('Title'),
        (int)ask('Credit units', '2'),
        ask('Level (100-500)', '100'),
        ask('Semester (first/second)', 'first'),
        (int)ask('Department id'),
    ]);
    $id = (int)$db->lastInsertId();
    logAudit((int)$me['id'], 'create', 'courses', "CLI: added course #$id");
    echo "Course #$id created.\n";
}

// ---------------------------------------------------------------------------
// Grades (same letter-grade + GPA logic as the web app)
// ---------------------------------------------------------------------------

function gradesView(PDO $db): void
{
    $sid = (int)ask('Student id');
    $rows = $db->prepare(
        "SELECT g.id, c.course_code, g.ca_score, g.exam_score, g.total_score,
                g.letter_grade, g.grade_points, g.credit_units,
                a.session_name AS session
         FROM grades g
         JOIN courses c ON c.id = g.course_id
         JOIN academic_sessions a ON a.id = g.session_id
         WHERE g.student_id = ? ORDER BY a.id, c.course_code");
    $rows->execute([$sid]);
    table($rows->fetchAll(), ['id', 'course_code', 'ca_score', 'exam_score',
                              'total_score', 'letter_grade', 'grade_points',
                              'credit_units', 'session']);
    $session = getCurrentSession();
    if ($session) {
        printf("  GPA (current session): %.2f   CGPA: %.2f\n",
            calculateGPA($sid, (int)$session['id']), calculateCGPA($sid));
    }
}

function gradeEnter(PDO $db, array $me): void
{
    $sid = (int)ask('Student id');
    $cid = (int)ask('Course id');
    $session = getCurrentSession();
    if (!$session) {
        echo "No current academic session configured.\n";
        return;
    }
    $ca = (float)ask('CA score (0-30)');
    $exam = (float)ask('Exam score (0-70)');
    [$letter, $points] = getLetterGrade($ca + $exam);
    $units = (int)ask('Credit units', '2');
    $stmt = $db->prepare(
        "INSERT INTO grades (student_id, course_id, session_id, ca_score,
                             exam_score, letter_grade, grade_points,
                             credit_units, entered_by)
         VALUES (?,?,?,?,?,?,?,?,?)
         ON DUPLICATE KEY UPDATE ca_score = VALUES(ca_score),
             exam_score = VALUES(exam_score),
             letter_grade = VALUES(letter_grade),
             grade_points = VALUES(grade_points),
             credit_units = VALUES(credit_units),
             entered_by = VALUES(entered_by)");
    $stmt->execute([$sid, $cid, (int)$session['id'], $ca, $exam,
                    $letter, $points, $units, (int)$me['id']]);
    logAudit((int)$me['id'], 'create', 'grades',
        "CLI: grade for student #$sid course #$cid");
    printf("Saved: total %.1f -> %s (%.1f points)\n", $ca + $exam, $letter, $points);
}

// ---------------------------------------------------------------------------
// Attendance
// ---------------------------------------------------------------------------

function attendanceMark(PDO $db, array $me): void
{
    $sid = (int)ask('Student id');
    $cid = (int)ask('Course id');
    $session = getCurrentSession();
    if (!$session) {
        echo "No current academic session configured.\n";
        return;
    }
    $date = ask('Date (YYYY-MM-DD)', date('Y-m-d'));
    $status = ask('Status (present/absent/late/excused)', 'present');
    $stmt = $db->prepare(
        "INSERT INTO attendance (student_id, course_id, session_id,
                                 attendance_date, status, marked_by)
         VALUES (?,?,?,?,?,?)
         ON DUPLICATE KEY UPDATE status = VALUES(status),
             marked_by = VALUES(marked_by)");
    $stmt->execute([$sid, $cid, (int)$session['id'], $date, $status, (int)$me['id']]);
    logAudit((int)$me['id'], 'create', 'attendance',
        "CLI: $status for student #$sid course #$cid on $date");
    echo "Attendance saved.\n";
}

function attendanceReport(PDO $db): void
{
    $sid = (int)ask('Student id');
    $cid = (int)ask('Course id');
    $session = getCurrentSession();
    if (!$session) {
        echo "No current academic session configured.\n";
        return;
    }
    printf("Attendance rate: %.1f%%\n",
        getAttendanceRate($sid, $cid, (int)$session['id']));
}

// ---------------------------------------------------------------------------
// Fees
// ---------------------------------------------------------------------------

function feeStatement(PDO $db): void
{
    $sid = (int)ask('Student id');
    $session = getCurrentSession();
    if (!$session) {
        echo "No current academic session configured.\n";
        return;
    }
    $bal = getFeeBalance($sid, (int)$session['id']);
    printf("  Total due : %s\n  Paid      : %s\n  Balance   : %s\n",
        formatCurrency($bal['due']), formatCurrency($bal['paid']),
        formatCurrency($bal['balance']));
    $stmt = $db->prepare(
        "SELECT receipt_number, amount_paid, payment_date, payment_method
         FROM fee_payments WHERE student_id = ? AND session_id = ?
         ORDER BY payment_date");
    $stmt->execute([$sid, (int)$session['id']]);
    table($stmt->fetchAll(), ['receipt_number', 'amount_paid', 'payment_date', 'payment_method']);
}

function feeRecord(PDO $db, array $me): void
{
    $sid = (int)ask('Student id');
    $session = getCurrentSession();
    if (!$session) {
        echo "No current academic session configured.\n";
        return;
    }
    $structs = $db->query(
        "SELECT id, level, amount FROM fee_structures ORDER BY level")->fetchAll();
    table($structs, ['id', 'level', 'amount']);
    $stmt = $db->prepare(
        "INSERT INTO fee_payments (student_id, session_id, fee_structure_id,
                                   amount_paid, payment_date, payment_method,
                                   receipt_number, received_by)
         VALUES (?,?,?,?,CURDATE(),?,?,?)");
    $receipt = generateReceiptNumber();
    $stmt->execute([
        $sid, (int)$session['id'], (int)ask('Fee structure id'),
        (float)ask('Amount paid'),
        ask('Method (bank_transfer/cash/online)', 'cash'),
        $receipt, (int)$me['id'],
    ]);
    logAudit((int)$me['id'], 'create', 'fees', "CLI: payment $receipt for student #$sid");
    echo "Payment recorded — receipt $receipt\n";
}

// ---------------------------------------------------------------------------
// Reports / audit
// ---------------------------------------------------------------------------

function reportSummary(PDO $db): void
{
    $n = fn($sql) => (int)$db->query($sql)->fetchColumn();
    printf("  Students (active) : %d\n", $n("SELECT COUNT(*) FROM students WHERE status='active'"));
    printf("  Courses           : %d\n", $n("SELECT COUNT(*) FROM courses"));
    printf("  Departments       : %d\n", $n("SELECT COUNT(*) FROM departments"));
    printf("  Grades recorded   : %d\n", $n("SELECT COUNT(*) FROM grades"));
    printf("  Fees collected    : %s\n",
        formatCurrency((float)$db->query("SELECT COALESCE(SUM(amount_paid),0) FROM fee_payments")->fetchColumn()));
    $rows = $db->query(
        "SELECT d.name AS department, COUNT(s.id) AS students
         FROM departments d LEFT JOIN students s ON s.department_id = d.id
         GROUP BY d.id ORDER BY students DESC")->fetchAll();
    echo "\n  Students by department:\n";
    table($rows, ['department', 'students']);
}

function auditLog(PDO $db): void
{
    $rows = $db->query(
        "SELECT a.created_at, u.username, a.action, a.module, a.description
         FROM audit_logs a LEFT JOIN users u ON u.id = a.user_id
         ORDER BY a.id DESC LIMIT 20")->fetchAll();
    table($rows, ['created_at', 'username', 'action', 'module', 'description']);
}

function usersList(PDO $db): void
{
    $rows = $db->query(
        "SELECT id, username, email, role, full_name, status
         FROM users ORDER BY id")->fetchAll();
    table($rows, ['id', 'username', 'email', 'role', 'full_name', 'status']);
}

// ---------------------------------------------------------------------------
// Main menu
// ---------------------------------------------------------------------------

echo str_repeat('=', 46) . "\n  SRMS — terminal client\n" . str_repeat('=', 46) . "\n\n";

$me = login($db);
if (!$me) {
    exit(1);
}

$isAdmin = in_array($me['role'], ['admin', 'registrar'], true);

$menu = [
    ['Students: list/search',   fn() => studentsList($db)],
    ['Students: profile',       fn() => studentProfile($db)],
    ['Courses: list',           fn() => coursesList($db)],
    ['Grades: view student',    fn() => gradesView($db)],
    ['Grades: enter/update',    fn() => gradeEnter($db, $me)],
    ['Attendance: mark',        fn() => attendanceMark($db, $me)],
    ['Attendance: report',      fn() => attendanceReport($db)],
    ['Fees: statement',         fn() => feeStatement($db)],
    ['Fees: record payment',    fn() => feeRecord($db, $me)],
    ['Reports: summary',        fn() => reportSummary($db)],
];
if ($isAdmin) {
    $menu[] = ['Students: add',  fn() => studentAdd($db, $me)];
    $menu[] = ['Courses: add',   fn() => courseAdd($db, $me)];
    $menu[] = ['Users: list',    fn() => usersList($db)];
    $menu[] = ['Audit log',      fn() => auditLog($db)];
}

while (true) {
    echo "\n===== SRMS — {$me['full_name']} ({$me['role']}) =====\n";
    foreach ($menu as $i => [$label, $_]) {
        printf("  %2d. %s\n", $i + 1, $label);
    }
    echo "   0. Exit\n";
    $choice = ask('>');
    if ($choice === '0') {
        break;
    }
    $idx = (int)$choice - 1;
    if (!isset($menu[$idx])) {
        echo "Invalid choice.\n";
        continue;
    }
    try {
        $menu[$idx][1]();
    } catch (Throwable $e) {
        echo 'Error: ' . $e->getMessage() . "\n";
    }
}
echo "Bye.\n";
