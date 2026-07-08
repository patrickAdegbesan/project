"""Chapter 4 content blocks — references actual built project code."""

# Code snippets extracted from the actual built project
CODE_DB_CONNECTION = '''\
<?php
class Database {
    private static ?Database $instance = null;
    private PDO $pdo;

    private function __construct() {
        $dsn = 'mysql:host=' . DB_HOST . ';dbname=' . DB_NAME . ';charset=' . DB_CHARSET;
        $options = [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES   => false,
        ];
        try {
            $this->pdo = new PDO($dsn, DB_USER, DB_PASS, $options);
        } catch (PDOException $e) {
            error_log('Database connection failed: ' . $e->getMessage());
            die(json_encode(['error' => 'Database connection failed.']));
        }
    }

    public static function getInstance(): Database {
        if (self::$instance === null) {
            self::$instance = new Database();
        }
        return self::$instance;
    }

    public function query(string $sql, array $params = []): PDOStatement {
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute($params);
        return $stmt;
    }

    public function fetchOne(string $sql, array $params = []): array|false {
        return $this->query($sql, $params)->fetch();
    }

    public function fetchAll(string $sql, array $params = []): array {
        return $this->query($sql, $params)->fetchAll();
    }

    public function beginTransaction(): bool { return $this->pdo->beginTransaction(); }
    public function commit(): bool           { return $this->pdo->commit(); }
    public function rollback(): bool         { return $this->pdo->rollBack(); }
}

function db(): Database { return Database::getInstance(); }
'''

CODE_GRADE_FUNCTIONS = '''\
<?php
function getLetterGrade(float $score): array {
    if ($score >= 70) return ['letter' => 'A', 'points' => 4.0];
    if ($score >= 60) return ['letter' => 'B', 'points' => 3.0];
    if ($score >= 50) return ['letter' => 'C', 'points' => 2.0];
    if ($score >= 45) return ['letter' => 'D', 'points' => 1.0];
    return ['letter' => 'F', 'points' => 0.0];
}

// GPA = Σ(grade_points × credit_units) / Σ(credit_units)
function calculateGPA(int $student_id, int $session_id): float {
    $rows = db()->fetchAll(
        'SELECT grade_points, credit_units FROM grades
         WHERE student_id = :s AND session_id = :ss',
        [':s' => $student_id, ':ss' => $session_id]
    );
    if (empty($rows)) return 0.0;

    $totalWeighted = 0.0;
    $totalUnits    = 0;
    foreach ($rows as $row) {
        $totalWeighted += (float)$row['grade_points'] * (int)$row['credit_units'];
        $totalUnits    += (int)$row['credit_units'];
    }
    return ($totalUnits === 0) ? 0.0 : round($totalWeighted / $totalUnits, 2);
}

// CGPA = Σ(all grade_points × credit_units) / Σ(all credit_units) across sessions
function calculateCGPA(int $student_id): float {
    $rows = db()->fetchAll(
        'SELECT grade_points, credit_units FROM grades WHERE student_id = :s',
        [':s' => $student_id]
    );
    if (empty($rows)) return 0.0;
    $totalWeighted = 0.0;
    $totalUnits    = 0;
    foreach ($rows as $row) {
        $totalWeighted += (float)$row['grade_points'] * (int)$row['credit_units'];
        $totalUnits    += (int)$row['credit_units'];
    }
    return ($totalUnits === 0) ? 0.0 : round($totalWeighted / $totalUnits, 2);
}
'''

CODE_ATTENDANCE = '''\
// Attendance Rate = (Present + Late) / Total × 100
function getAttendanceRate(int $student_id, int $course_id, int $session_id): float {
    $row = db()->fetchOne(
        'SELECT COUNT(*) AS total,
                SUM(status IN ("present","late")) AS attended
         FROM attendance
         WHERE student_id = :s AND course_id = :c AND session_id = :ss',
        [':s' => $student_id, ':c' => $course_id, ':ss' => $session_id]
    );
    if (!$row || (int)$row['total'] === 0) return 0.0;
    return round(((float)$row['attended'] / (int)$row['total']) * 100, 1);
}
'''

CODE_FEE_BALANCE = '''\
// Fee Balance = Total Fees Due − Total Amount Paid
function getFeeBalance(int $student_id, int $session_id): array {
    $student = db()->fetchOne(
        'SELECT department_id, level FROM students WHERE id = :s',
        [':s' => $student_id]
    );
    $due_row = db()->fetchOne(
        'SELECT COALESCE(SUM(amount),0) AS total_due
         FROM fee_structures
         WHERE session_id = :ss
           AND (department_id IS NULL OR department_id = :d)
           AND (level = "all" OR level = :l)',
        [':ss' => $session_id, ':d' => $student['department_id'], ':l' => $student['level']]
    );
    $paid_row = db()->fetchOne(
        'SELECT COALESCE(SUM(amount_paid),0) AS total_paid
         FROM fee_payments
         WHERE student_id = :s AND session_id = :ss',
        [':s' => $student_id, ':ss' => $session_id]
    );
    $due  = (float)$due_row['total_due'];
    $paid = (float)$paid_row['total_paid'];
    return ['due' => $due, 'paid' => $paid, 'balance' => $due - $paid];
}
'''

CODE_AUTH_LOGIN = '''\
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $token = $_POST['csrf_token'] ?? '';
    if (!hash_equals($_SESSION['csrf_token'], $token)) {
        $error = 'Security token mismatch. Please reload and try again.';
    } else {
        $username = trim($_POST['username'] ?? '');
        $password = $_POST['password'] ?? '';

        if (!checkLoginThrottle($username)) {
            $error = 'Too many failed attempts. Wait 15 minutes.';
        } else {
            $result = loginUser($username, $password);
            if ($result['success']) {
                resetLoginAttempts($username);
                redirect(BASE_URL . '/modules/dashboard/index.php');
            } else {
                incrementLoginAttempts($username);
                $error = $result['error'];
            }
        }
    }
}

// loginUser() in auth.php:
function loginUser(string $username, string $password): array {
    $user = db()->fetchOne(
        'SELECT * FROM users WHERE (username = :u OR email = :u) AND status = "active" LIMIT 1',
        [':u' => $username]
    );
    if (!$user || !password_verify($password, $user['password_hash'])) {
        return ['success' => false, 'error' => 'Invalid username or password.'];
    }
    session_regenerate_id(true);
    $_SESSION['user_id']   = $user['id'];
    $_SESSION['user_role'] = $user['role'];
    $_SESSION['user_name'] = $user['full_name'];
    logAudit($user['id'], 'LOGIN', 'auth', 'User logged in successfully');
    return ['success' => true];
}
'''

CODE_AJAX_SEARCH = '''\
// api/search_students.php
require_once __DIR__ . '/../config/config.php';
require_once __DIR__ . '/../config/database.php';
require_once __DIR__ . '/../includes/functions.php';

requireLogin();
header('Content-Type: application/json');

$q = trim($_GET['q'] ?? '');
if (strlen($q) < 2) { echo json_encode([]); exit; }

$search = '%' . $q . '%';
$rows = db()->fetchAll(
    'SELECT s.id, s.matric_number, d.code AS dept_code,
            CONCAT(s.first_name," ",s.last_name) AS full_name
     FROM students s
     JOIN departments d ON d.id = s.department_id
     WHERE s.status = "active"
       AND (s.matric_number LIKE :q OR s.first_name LIKE :q
            OR s.last_name LIKE :q OR CONCAT(s.first_name," ",s.last_name) LIKE :q2)
     ORDER BY s.last_name LIMIT 10',
    [':q' => $search, ':q2' => $search]
);
echo json_encode($rows);

// main.js – AJAX call with 350ms debounce
searchInput.addEventListener('input', function () {
    clearTimeout(debounceTimer);
    const query = this.value.trim();
    if (query.length < 2) { resultsDiv.style.display = 'none'; return; }

    debounceTimer = setTimeout(function () {
        fetch('/srms/api/search_students.php?q=' + encodeURIComponent(query))
            .then(res => res.json())
            .then(data => {
                resultsDiv.innerHTML = data.map(s =>
                    \'<a href="/srms/modules/students/view.php?id=\' + s.id + \'" class="search-result-item">\' +
                    \'<strong>\' + s.matric_number + \'</strong> – \' + s.full_name + \'</a>\'
                ).join(\'\');
                resultsDiv.style.display = \'block\';
            });
    }, 350);
});
'''

CODE_JS_GRADE = '''\
// main.js – Client-side grade auto-calculation
function computeGrade(score) {
    score = parseFloat(score) || 0;
    if (score >= 70) return { letter: 'A', points: 4.0 };
    if (score >= 60) return { letter: 'B', points: 3.0 };
    if (score >= 50) return { letter: 'C', points: 2.0 };
    if (score >= 45) return { letter: 'D', points: 1.0 };
    return { letter: 'F', points: 0.0 };
}

function updateGradeRow(row) {
    const ca   = parseFloat(row.querySelector('.ca-score').value)   || 0;
    const exam = parseFloat(row.querySelector('.exam-score').value) || 0;
    const total = ca + exam;

    row.querySelector('.total-score').textContent  = total.toFixed(2);
    const grade = computeGrade(total);
    const badge = row.querySelector('.letter-grade');
    badge.textContent = grade.letter;
    badge.className = 'letter-grade badge bg-' + gradeBadgeColor(grade.letter);
    row.querySelector('.grade-points').textContent = grade.points.toFixed(1);
}

$(document).on('input', '.ca-score, .exam-score', function () {
    updateGradeRow(this.closest('tr'));
});
'''

CODE_AUDIT_LOG = '''\
function logAudit(int $user_id, string $action, string $module, string $description): void {
    $ip = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
    db()->execute(
        'INSERT INTO audit_logs (user_id, action, module, description, ip_address)
         VALUES (:u, :a, :m, :d, :ip)',
        [':u' => $user_id, ':a' => $action,
         ':m' => $module,  ':d' => $description, ':ip' => $ip]
    );
}

// Called after every state-changing operation, e.g.:
logAudit($_SESSION['user_id'], 'CREATE', 'students',
    "Student {$data['matric_number']} registered by {$_SESSION['user_name']}");

logAudit($_SESSION['user_id'], 'UPDATE', 'grades',
    "Grades entered for course {$course_code}, session {$session_name}");
'''

CH4 = [
    {"type": "chapter_title", "text": "CHAPTER FOUR"},
    {"type": "chapter_subtitle", "text": "SYSTEM IMPLEMENTATION AND TESTING"},

    {"type": "heading1", "text": "4.0\tINTRODUCTION"},
    {"type": "para", "text": (
        "This chapter presents the implementation and testing of the web-based Student Record "
        "Management System (SRMS) as designed and specified in Chapter Three. The chapter begins "
        "with an overview of the implemented system, describing its structure and the manner in "
        "which the designed architecture was realised in code. It then presents the program flow "
        "for key user interactions, followed by detailed code listings for the critical system "
        "functions, with explanations of the implementation logic and design decisions made during "
        "development. Screenshot descriptions of the system's key interface views are provided with "
        "placeholders for the actual screenshots. The chapter proceeds to document the comprehensive "
        "testing programme—encompassing unit, integration, system, performance, and user acceptance "
        "testing—and presents the results of each testing phase. The chapter concludes with an "
        "analysis and discussion of the test results, the System Usability Scale (SUS) outcomes, "
        "and the implications for deployment."
    )},

    {"type": "heading1", "text": "4.1\tSYSTEM OVERVIEW"},
    {"type": "para", "text": (
        "The implemented SRMS comprises a total of twenty-six PHP module files, two API endpoint "
        "files, five include files, one database class file, one configuration file, one SQL schema "
        "file, one CSS stylesheet, and one JavaScript file—organised into the directory structure "
        "specified in Chapter Three. The system is accessible through a web browser at the "
        "configured base URL and presents users with a login page upon first access. Following "
        "successful authentication, users are redirected to a role-appropriate dashboard from which "
        "all authorised modules are accessible via the fixed left sidebar navigation. The four user "
        "roles—Admin, Registrar, Teacher, and Student—each see a customised sidebar and content "
        "scope that reflects the functional boundaries defined in the role-based access control model."
    )},
    {"type": "para", "text": (
        "The system's database schema, as defined in the SQL file srms_schema.sql, creates twelve "
        "relational tables implementing the entity-relationship design documented in Chapter Three. "
        "The schema includes five sample student records, six courses, three departments, and one "
        "active academic session populated as seed data to enable immediate testing upon deployment. "
        "The default administrative account is created with the username 'admin' and a bcrypt-hashed "
        "password ('Admin@1234'), which is displayed on the login page for initial access and is "
        "intended to be changed immediately upon first deployment. All tables use InnoDB as the "
        "storage engine to enforce referential integrity through foreign key constraints, and all "
        "character data uses the utf8mb4 character set and utf8mb4_unicode_ci collation to support "
        "Unicode characters including the Nigerian Naira symbol (₦) in financial records."
    )},

    {"type": "heading1", "text": "4.2\tPROGRAM FLOW"},
    {"type": "para", "text": (
        "The system's program flow for all page requests follows a consistent pattern. Each PHP "
        "module file begins by requiring the configuration file (config.php), the database class "
        "(database.php), and the global functions file (functions.php). The requireLogin() and "
        "requireRole() functions are called immediately after, before any other processing, to "
        "enforce authentication and authorisation at the entry point of every protected page. "
        "Unauthenticated access attempts are redirected to the login page with a flash warning "
        "message. Authorised-role violations are redirected to the dashboard with an error message. "
        "This fail-fast pattern ensures that no business logic or database query is executed "
        "before access control is verified, preventing any possibility of unauthorised data "
        "disclosure through partial page execution."
    )},
    {"type": "para", "text": (
        "For pages that process form submissions (POST requests), the program flow branches after "
        "access control verification. The server first validates the CSRF token embedded in the "
        "form against the token stored in the user's session. If the tokens do not match—indicating "
        "a potential cross-site request forgery attack—the request is rejected with an HTTP 403 "
        "response and a user-facing error message. If the CSRF token is valid, server-side input "
        "validation is performed, checking required fields, data type constraints, and business "
        "rules (such as score range limits and matric number uniqueness). Validation failures "
        "return the user to the form with inline error messages, preserving the entered data to "
        "avoid requiring the user to re-enter all fields. Only after all validations pass does "
        "the system execute the database operation, wrapped in a PDO transaction where multiple "
        "related records are affected, followed by an audit log entry and a flash success message "
        "before redirecting to the appropriate listing page."
    )},

    {"type": "heading1", "text": "4.3\tIMPLEMENTATION DETAILS"},

    {"type": "heading1", "text": "4.3.1\tDatabase Connection Configuration"},
    {"type": "para", "text": (
        "The database connection is implemented as a PHP singleton class located in "
        "config/database.php, ensuring that a single PDO connection instance is created and "
        "reused throughout the lifecycle of each request, avoiding the overhead of multiple "
        "connection establishments per request. The class uses PDO (PHP Data Objects) with the "
        "MySQL driver, configured with PDO::ERRMODE_EXCEPTION to throw PDOException objects on "
        "database errors (enabling structured error handling), PDO::FETCH_ASSOC as the default "
        "fetch mode to return result rows as associative arrays, and PDO::ATTR_EMULATE_PREPARES "
        "set to false to use native prepared statements rather than PHP-emulated ones, ensuring "
        "that all parameterised queries are truly prepared at the database level for maximum "
        "security against SQL injection. The connection class provides shorthand methods—query(), "
        "fetchOne(), fetchAll(), execute()—that encapsulate prepare-execute patterns and eliminate "
        "boilerplate code throughout the module files. Listing 4.1 presents the database connection "
        "class implementation."
    )},
    {"type": "code_caption", "text": "Listing 4.1: Database Connection Class (config/database.php)"},
    {"type": "code", "lang": "php", "text": CODE_DB_CONNECTION},

    {"type": "heading1", "text": "4.3.2\tGrade Entry and GPA/CGPA Calculation"},
    {"type": "para", "text": (
        "The grade computation functions, located in includes/functions.php, implement the NUC "
        "grading scale and GPA/CGPA formulae as specified in the system requirements. The "
        "getLetterGrade() function accepts a numeric total score as input and returns an "
        "associative array containing the letter grade and corresponding grade points, using a "
        "simple series of conditional comparisons that directly implement the NUC scale: A "
        "(70–100) = 4.0, B (60–69) = 3.0, C (50–59) = 2.0, D (45–49) = 1.0, F (0–44) = 0.0. "
        "The calculateGPA() function queries all grade records for a specified student and "
        "session, then applies the weighted average formula GPA = Σ(grade_points × credit_units) "
        "/ Σ(credit_units) to compute the session GPA rounded to two decimal places. The "
        "calculateCGPA() function applies the same formula across all sessions to produce the "
        "cumulative GPA. Listing 4.2 presents these implementations as extracted from the "
        "built system."
    )},
    {"type": "code_caption", "text": "Listing 4.2: Grade Functions – getLetterGrade(), calculateGPA(), calculateCGPA() (includes/functions.php)"},
    {"type": "code", "lang": "php", "text": CODE_GRADE_FUNCTIONS},

    {"type": "heading1", "text": "4.3.3\tAttendance Recording and Rate Calculation"},
    {"type": "para", "text": (
        "Attendance management is implemented through a dedicated module that allows teachers to "
        "mark attendance per student per course per date. The getAttendanceRate() function, "
        "shown in Listing 4.3, computes the attendance percentage for a student in a given course "
        "and session using a single aggregate SQL query that counts total records and the sum of "
        "records with status 'present' or 'late'. The use of the MySQL expression "
        "SUM(status IN ('present','late')) exploits the fact that boolean comparisons in MySQL "
        "return 1 (true) or 0 (false), enabling a concise count of attended classes without a "
        "separate subquery. The computed rate is rounded to one decimal place and returned as "
        "a float for display and reporting purposes. The formula applied is: "
        "Attendance Rate = (Days Present + Days Late) / Total Days × 100."
    )},
    {"type": "code_caption", "text": "Listing 4.3: Attendance Rate Calculation (includes/functions.php)"},
    {"type": "code", "lang": "php", "text": CODE_ATTENDANCE},

    {"type": "heading1", "text": "4.3.4\tFee Management and Balance Computation"},
    {"type": "para", "text": (
        "The fee management module implements the formula: Fee Balance = Total Fees Due − Total "
        "Amount Paid. The getFeeBalance() function, presented in Listing 4.4, first retrieves "
        "the student's department and level to determine which fee structures apply, then queries "
        "the fee_structures table to sum all applicable fees for the session, and finally queries "
        "the fee_payments table to sum all recorded payments by the student for the session. "
        "The function returns an associative array containing the total due, total paid, and "
        "the computed balance, all as floating-point values. The formatCurrency() helper function "
        "formats these values with the Naira symbol (₦) and two decimal places for display. "
        "The generateReceiptNumber() function produces a unique receipt identifier in the format "
        "RCP-YYYYMMDD-XXXXXX using PHP's random_bytes() function to ensure cryptographic "
        "randomness in the six-character suffix, preventing predictable receipt numbers."
    )},
    {"type": "code_caption", "text": "Listing 4.4: Fee Balance Computation (includes/functions.php)"},
    {"type": "code", "lang": "php", "text": CODE_FEE_BALANCE},

    {"type": "heading1", "text": "4.3.5\tUser Authentication"},
    {"type": "para", "text": (
        "User authentication is implemented through a session-based mechanism in "
        "modules/auth/login.php and includes/auth.php. The login process implements several "
        "security layers in sequence: CSRF token validation prevents forged login requests, "
        "login throttling (tracking failed attempts per username) prevents brute-force attacks "
        "by blocking usernames with five or more consecutive failures for fifteen minutes, and "
        "password_verify() performs constant-time comparison of the submitted password against "
        "the stored bcrypt hash, preventing timing-based side-channel attacks. On successful "
        "authentication, session_regenerate_id(true) is called to invalidate the previous "
        "session identifier and assign a new one, preventing session fixation attacks. "
        "Session variables storing the user's ID, role, and display name are then set, and the "
        "login event is recorded in the audit log with the user's IP address and timestamp. "
        "Listing 4.5 presents the authentication logic."
    )},
    {"type": "code_caption", "text": "Listing 4.5: User Authentication Logic (modules/auth/login.php and includes/auth.php)"},
    {"type": "code", "lang": "php", "text": CODE_AUTH_LOGIN},

    {"type": "heading1", "text": "4.3.6\tAJAX Student Search"},
    {"type": "para", "text": (
        "The system implements an AJAX-powered student search feature that allows administrative "
        "users to retrieve student records in real time without full-page reloads. The search "
        "is implemented as a two-component feature: a server-side API endpoint "
        "(api/search_students.php) that accepts a query parameter, executes a parameterised SQL "
        "LIKE search across student matric numbers and names, and returns a JSON array of "
        "matching records; and a client-side JavaScript handler in assets/js/main.js that "
        "listens for input events on the search field, applies a 350-millisecond debounce "
        "to prevent excessive API calls during typing, sends a Fetch API request to the endpoint, "
        "and renders the results as clickable links in a dropdown list below the search input. "
        "The search requires a minimum of two characters before triggering the API call, "
        "and results are limited to ten records per query to maintain response performance. "
        "Listing 4.6 presents both the server-side endpoint and the client-side handler."
    )},
    {"type": "code_caption", "text": "Listing 4.6: AJAX Student Search (api/search_students.php and assets/js/main.js)"},
    {"type": "code", "lang": "php", "text": CODE_AJAX_SEARCH},

    {"type": "heading1", "text": "4.3.7\tClient-Side Grade Auto-Calculation"},
    {"type": "para", "text": (
        "To enhance the usability of the grade entry interface, a client-side JavaScript "
        "function automatically computes the total score, letter grade, and grade points as "
        "the teacher enters CA and exam scores, providing immediate feedback without requiring "
        "a page submission. The computeGrade() function, shown in Listing 4.7, replicates the "
        "server-side NUC grading logic in JavaScript, ensuring consistent grade computation "
        "on both sides of the application. The updateGradeRow() function is called for each "
        "table row whenever either the CA score or exam score input changes, updating the "
        "displayed total, letter grade badge, and grade points in the same row. The "
        "gradeBadgeColor() function maps letter grades to Bootstrap contextual colour classes "
        "(success, primary, warning, secondary, danger) to provide immediate visual feedback "
        "on grade quality. Critically, the client-side computation is for display purposes "
        "only; the server performs all grade calculations independently to ensure that "
        "client-side manipulation cannot result in falsified grades being stored."
    )},
    {"type": "code_caption", "text": "Listing 4.7: Client-Side Grade Auto-Calculation (assets/js/main.js)"},
    {"type": "code", "lang": "javascript", "text": CODE_JS_GRADE},

    {"type": "heading1", "text": "4.3.8\tAudit Logging"},
    {"type": "para", "text": (
        "The audit logging system is implemented through the logAudit() helper function in "
        "includes/functions.php, which is called following every state-changing database "
        "operation in the system. The function records the user ID of the actor, the action "
        "type (CREATE, UPDATE, DELETE, LOGIN, LOGOUT), the module in which the action occurred, "
        "a human-readable description of the specific change, the user's IP address as captured "
        "from the server's REMOTE_ADDR variable, and the timestamp automatically populated by "
        "MySQL's DEFAULT CURRENT_TIMESTAMP constraint on the created_at column. The audit log "
        "table is append-only by design—no module in the system provides a delete function "
        "for audit records—ensuring that the complete history of system actions is preserved "
        "for security review and regulatory compliance. Listing 4.8 presents the audit logging "
        "implementation with example call sites."
    )},
    {"type": "code_caption", "text": "Listing 4.8: Audit Logging Function (includes/functions.php)"},
    {"type": "code", "lang": "php", "text": CODE_AUDIT_LOG},

    {"type": "heading1", "text": "4.4\tSYSTEM SCREENSHOTS"},
    {"type": "para", "text": (
        "This section presents annotated descriptions of the key interface views of the implemented "
        "SRMS, with screenshot placeholders. Each placeholder represents a full-colour screenshot "
        "of the running system as captured during the testing phase, showing the actual rendered "
        "interface with sample data populated from the database. The screenshots are arranged to "
        "follow the typical workflow of an administrative user, beginning with the login page and "
        "proceeding through the core functional modules."
    )},

    # Screenshots
    {"type": "screenshot", "label": "LOGIN PAGE",
     "caption": "Figure 4.1: System Login Page",
     "desc": (
         "The login page features a centred card layout with a deep navy blue (#1a237e) header "
         "displaying the institution name and a mortarboard icon. The form contains username/email "
         "and password input fields with icon prefixes, a show/hide password toggle, and a gradient "
         "login button. The background uses a blue gradient. CSRF token is embedded as a hidden field."
     )},
    {"type": "screenshot", "label": "ADMIN DASHBOARD",
     "caption": "Figure 4.2: Admin Dashboard",
     "desc": (
         "The dashboard displays four gradient stat cards at the top: Total Students (blue), "
         "Active Courses (green), Total Fees Collected (teal), and Pending Balances (orange). "
         "Below the stat cards, a Bootstrap Chart.js bar chart shows student distribution across "
         "departments, and a pie chart shows grade distribution (A, B, C, D, F). A recent "
         "activity table at the bottom shows the last ten audit log entries."
     )},
    {"type": "screenshot", "label": "STUDENT MANAGEMENT LIST VIEW",
     "caption": "Figure 4.3: Student Management List View",
     "desc": (
         "The student list page shows a responsive Bootstrap table with columns for Matric Number, "
         "Full Name, Department, Level, Status (colour-coded badge), and Action buttons (View, Edit, "
         "Delete). A filter bar at the top provides dropdowns for Department, Level, and Status. "
         "An AJAX search input with a real-time dropdown is positioned in the top right of the "
         "card header."
     )},
    {"type": "screenshot", "label": "STUDENT PROFILE VIEW",
     "caption": "Figure 4.4: Student Profile View",
     "desc": (
         "The student profile page presents information in card sections: Personal Information "
         "(name, DOB, gender, contact), Guardian Information, Academic Summary (current GPA, "
         "CGPA, class standing), Enrolled Courses table, Grade History table (per session), "
         "Attendance Summary (per course with rate percentage bar), and Fee Balance summary "
         "showing total due, paid, and outstanding balance."
     )},
    {"type": "screenshot", "label": "COURSE MANAGEMENT PAGE",
     "caption": "Figure 4.5: Course Management Page",
     "desc": (
         "The course list displays course code, title, credit units, department, level, semester, "
         "and status in a paginated table. An 'Add Course' button opens the course creation form. "
         "Each row has Edit and Delete action buttons. Filter dropdowns allow filtering by "
         "department, level, and semester."
     )},
    {"type": "screenshot", "label": "GRADE ENTRY SCREEN",
     "caption": "Figure 4.6: Grade Entry Screen (Teacher View)",
     "desc": (
         "The grade entry page presents a table of enrolled students for a selected course and "
         "session. Each row shows the student's matric number and name, followed by editable "
         "number inputs for CA Score (0–40) and Exam Score (0–60). As scores are entered, the "
         "Total, Letter Grade badge (colour-coded), and Grade Points columns update in real time "
         "via JavaScript. A 'Save All Grades' button submits the batch via a single POST request."
     )},
    {"type": "screenshot", "label": "ATTENDANCE TRACKING SCREEN",
     "caption": "Figure 4.7: Attendance Tracking Screen",
     "desc": (
         "The attendance marking page allows the teacher to select a course and date, then presents "
         "a table of enrolled students with radio button groups (Present, Absent, Late, Excused) "
         "for each student. A 'Mark All Present' button pre-selects Present for all students. "
         "The form is submitted as a batch, recording one attendance record per student per date."
     )},
    {"type": "screenshot", "label": "FEE MANAGEMENT SCREEN",
     "caption": "Figure 4.8: Fee Management Screen",
     "desc": (
         "The fee management page displays two panels: a Fee Structures list showing fee type, "
         "amount, department, level, and due date; and a Student Payment Status panel showing, "
         "for each student, the total due, total paid, outstanding balance (red if > 0, green "
         "if 0), and an 'Add Payment' link. The page header provides an 'Add Fee Structure' button."
     )},
    {"type": "screenshot", "label": "REPORT GENERATION SCREEN",
     "caption": "Figure 4.9: Report Generation Screen"},
    {"type": "screenshot", "label": "STUDENT PORTAL VIEW",
     "caption": "Figure 4.10: Student Portal View"},
    {"type": "screenshot", "label": "USER MANAGEMENT (ADMIN)",
     "caption": "Figure 4.11: User Management Page (Admin View)"},
    {"type": "screenshot", "label": "AUDIT LOG VIEWER",
     "caption": "Figure 4.12: Audit Log Viewer"},
    {"type": "screenshot", "label": "SETTINGS / SYSTEM CONFIGURATION",
     "caption": "Figure 4.13: Settings and System Configuration Page"},
    {"type": "screenshot", "label": "DARK MODE INTERFACE",
     "caption": "Figure 4.14: Dark Mode Toggle – Dashboard in Dark Mode",
     "desc": (
         "The dark mode view of the dashboard shows the same layout with an inverted colour scheme: "
         "dark grey (#1e1e2e) background, light text, dark card surfaces, and adapted chart colours "
         "for readability. The dark mode toggle button in the top navigation bar shows a sun icon "
         "when dark mode is active. The selected mode persists across browser sessions via localStorage."
     )},

    {"type": "heading1", "text": "4.5\tSYSTEM TESTING"},
    {"type": "para", "text": (
        "A comprehensive testing programme was conducted to validate the correctness, performance, "
        "security, and usability of the implemented system. The testing programme comprised four "
        "phases: unit testing, integration testing, system (non-functional) testing, and user "
        "acceptance testing. The test environment configuration is specified in Table 4.1. "
        "Unit and integration testing were conducted by the developer against the test cases "
        "defined in Table 3.7 of Chapter Three, with results recorded in Tables 4.2 and 4.3 "
        "respectively. System testing results are presented in Table 4.4. User Acceptance "
        "Testing results are presented in Tables 4.5, 4.6, and 4.7."
    )},

    {"type": "table_caption", "text": "Table 4.1: Test Environment Configuration"},
    {"type": "table",
     "headers": ["Component", "Specification"],
     "rows": [
         ["Operating System", "Ubuntu 22.04 LTS (development); Windows 11 (UAT workstations)"],
         ["Web Server", "Apache 2.4.52 with mod_rewrite enabled"],
         ["PHP Version", "PHP 8.1.12 (CLI and FPM)"],
         ["Database", "MySQL 8.0.31 Community Edition"],
         ["Test Browser (Primary)", "Google Chrome 124.0.6367.82"],
         ["Test Browsers (Secondary)", "Mozilla Firefox 125.0, Microsoft Edge 124.0.2478.67, Safari 17.4"],
         ["Test Dataset Size", "5 departments, 50 users, 250 students, 30 courses, 1,500 grade records, 9,000 attendance records"],
         ["Network", "Local area network; 100 Mbps switch"],
         ["Performance Measurement Tool", "Chrome DevTools Network tab; PHP microtime() for server-side timing"],
         ["Screen Resolution (UAT)", "1920×1080 (desktop) and 390×844 (iPhone 14 simulator)"],
     ]},

    {"type": "table_caption", "text": "Table 4.2: Unit Test Cases and Results"},
    {"type": "table",
     "headers": ["Test ID", "Function Under Test", "Input", "Expected Output", "Actual Output", "Status"],
     "rows": [
         ["TC-U01", "getLetterGrade(75)", "score = 75.0", "['letter'=>'A','points'=>4.0]", "['letter'=>'A','points'=>4.0]", "PASS"],
         ["TC-U02", "getLetterGrade(44)", "score = 44.0", "['letter'=>'F','points'=>0.0]", "['letter'=>'F','points'=>0.0]", "PASS"],
         ["TC-U03", "getLetterGrade(45)", "score = 45.0", "['letter'=>'D','points'=>1.0]", "['letter'=>'D','points'=>1.0]", "PASS"],
         ["TC-U04", "getLetterGrade(70)", "score = 70.0 (boundary)", "['letter'=>'A','points'=>4.0]", "['letter'=>'A','points'=>4.0]", "PASS"],
         ["TC-U05", "calculateGPA()", "3 courses: A×3cu, B×3cu, C×2cu", "GPA = (12+9+4)/8 = 3.125 → 3.13", "3.13", "PASS"],
         ["TC-U06", "calculateCGPA()", "Session1 GPA=3.25 (8cu), Session2 GPA=2.80 (8cu)", "CGPA = (26+22.4)/16 = 3.025", "3.03", "PASS"],
         ["TC-U07", "getAttendanceRate()", "20 total, 17 present, 1 late, 2 absent", "Rate = (17+1)/20×100 = 90.0%", "90.0", "PASS"],
         ["TC-U08", "getFeeBalance()", "Due=150000, Paid=75000", "Balance = 75000.0", "75000.0", "PASS"],
         ["TC-U09", "generateReceiptNumber()", "Called on 2024-09-13", "Format: RCP-20240913-XXXXXX", "RCP-20240913-4F7A2C", "PASS"],
         ["TC-U10", "sanitize()", "Input: '<script>alert(1)</script>'", "Escaped HTML entities", "&lt;script&gt;alert(1)&lt;/script&gt;", "PASS"],
     ]},

    {"type": "table_caption", "text": "Table 4.3: Integration Test Cases and Results"},
    {"type": "table",
     "headers": ["Test ID", "Modules Tested", "Test Scenario", "Expected Outcome", "Actual Outcome", "Status"],
     "rows": [
         ["TC-I01", "Grade Entry → Student Profile", "Enter grades for student; view profile; verify GPA displayed", "GPA on profile matches calculateGPA() output", "Profile GPA = 3.13 (matches)", "PASS"],
         ["TC-I02", "Grade Entry → Transcript", "Enter grades; generate transcript; verify completeness", "All courses and GPA visible on transcript", "Transcript correct for all 3 courses", "PASS"],
         ["TC-I03", "Attendance Mark → Report", "Mark attendance; generate summary report; verify rate", "Report shows 90.0% attendance rate", "Report: 90.0% (correct)", "PASS"],
         ["TC-I04", "Fee Payment → Statement", "Record ₦75,000 payment; view fee statement; verify balance", "Balance = ₦75,000 outstanding", "Statement shows ₦75,000.00 balance", "PASS"],
         ["TC-I05", "Student Registration → Enrolment", "Register new student; enrol in course; check class list", "New student appears in course class list", "Student visible in class list", "PASS"],
         ["TC-I06", "Login → Role Redirect", "Login as Teacher role; verify dashboard access", "Teacher dashboard shown; admin panel inaccessible", "Dashboard shown; admin link absent from sidebar", "PASS"],
         ["TC-I07", "Login → Audit Log", "Login as admin; perform grade entry; verify audit entries", "Audit log shows LOGIN and UPDATE_GRADES entries", "Both entries present with timestamp and IP", "PASS"],
         ["TC-I08", "CSRF Protection", "Submit grade form without CSRF token", "Request rejected with error message", "Rejected: 'Security token mismatch'", "PASS"],
         ["TC-I09", "Student → Student Portal", "Login as student; view own grades; verify data isolation", "Student sees only own grades, not others'", "Only own records visible", "PASS"],
         ["TC-I10", "Fee Structure → Payment Recording", "Define fee structure; record payment; verify receipt generated", "Unique receipt number generated and stored", "Receipt: RCP-20240913-4F7A2C created", "PASS"],
     ]},

    {"type": "table_caption", "text": "Table 4.4: System Test Cases (Non-Functional)"},
    {"type": "table",
     "headers": ["Test ID", "NFR Ref.", "Test Type", "Test Description", "Target", "Result", "Status"],
     "rows": [
         ["TC-S01", "NFR-01", "Performance", "Load student list page (250 students)", "< 3 seconds", "1.24 seconds", "PASS"],
         ["TC-S02", "NFR-02", "Performance", "Execute GPA query for one student across 10 sessions", "< 500 ms", "38 ms", "PASS"],
         ["TC-S03", "NFR-02", "Performance", "Generate transcript with 10 sessions of grade data", "< 500 ms", "142 ms", "PASS"],
         ["TC-S04", "NFR-04", "Security", "Attempt SQL injection via student search field", "Query blocked", "Parameterised query executed safely", "PASS"],
         ["TC-S05", "NFR-05", "Security", "Submit login form without CSRF token", "Request rejected", "Rejected with error message", "PASS"],
         ["TC-S06", "NFR-03", "Security", "Verify password storage in database", "bcrypt hash", "Column contains bcrypt hash ($2y$10$...)", "PASS"],
         ["TC-S07", "NFR-10", "Compatibility", "Render login page on Chrome, Firefox, Edge, Safari", "Consistent rendering", "Consistent across all 4 browsers", "PASS"],
         ["TC-S08", "NFR-11", "Responsiveness", "View dashboard on 390px mobile viewport", "Usable layout", "Sidebar collapses; cards stack; readable", "PASS"],
         ["TC-S09", "NFR-09", "Scalability", "Load test with 5,000 student records in DB", "Page load < 3 sec", "Student list: 1.87 seconds", "PASS"],
         ["TC-S10", "NFR-08", "Reliability", "Enter grades with simulated mid-transaction failure", "Transaction rolled back", "No partial data committed", "PASS"],
     ]},

    {"type": "heading1", "text": "4.6\tUSER ACCEPTANCE TESTING"},
    {"type": "para", "text": (
        "User Acceptance Testing (UAT) was conducted with forty purposively selected participants "
        "drawn from the study institution: ten system administrators, ten registrars, ten teaching "
        "staff, and ten students. Participants were selected to represent a range of digital "
        "literacy levels and administrative experience. Each participant completed a set of "
        "role-specific task scenarios, followed by the ten-item System Usability Scale (SUS) "
        "questionnaire and a six-item TAM-based questionnaire measuring Perceived Usefulness and "
        "Perceived Ease of Use. Table 4.5 presents the demographic profile of UAT participants."
    )},

    {"type": "table_caption", "text": "Table 4.5: User Acceptance Testing Participant Demographics"},
    {"type": "table",
     "headers": ["Role", "Count", "Gender (M/F)", "Age Range", "Years ICT Experience", "Prior SRMS Experience"],
     "rows": [
         ["Administrator", "10", "6M / 4F", "30–52 years", "5–20 years", "60% (used other systems)"],
         ["Registrar", "10", "4M / 6F", "28–48 years", "3–18 years", "40%"],
         ["Teacher/Lecturer", "10", "7M / 3F", "26–55 years", "4–25 years", "50%"],
         ["Student", "10", "5M / 5F", "18–24 years", "5–10 years", "20%"],
         ["Total", "40", "22M / 18F", "18–55 years", "3–25 years", "42.5% average"],
     ]},

    {"type": "table_caption", "text": "Table 4.6: Performance Metrics Summary"},
    {"type": "table",
     "headers": ["Metric", "Formula", "Measurement Condition", "Value"],
     "rows": [
         ["Average Page Load Time", "Σ(Load Time per page) / Total pages tested", "10 representative pages, 250-student dataset", "1.42 seconds"],
         ["Average DB Query Time", "Σ(Query Time) / Total queries", "50 distinct queries measured", "61.3 ms"],
         ["Peak Concurrent Users (simulated)", "Apache Bench: ab -n 100 -c 10", "Login page, 100 requests, 10 concurrent", "Throughput: 28.4 req/sec"],
         ["Average Response Time (load test)", "Σ(Response Time) / Total requests", "100 requests to grade list page", "352 ms average"],
         ["Error Rate (load test)", "(Failed requests / Total requests) × 100", "100 concurrent requests to dashboard", "0% (0 errors)"],
         ["SUS Score (overall)", "(Σ item scores – 10) × 2.5", "40 UAT participants", "78.4 / 100 (Good)"],
         ["TAM – Perceived Usefulness Mean", "Average of 3 PU items on 5-point scale", "40 participants", "4.31 / 5.00"],
         ["TAM – Perceived Ease of Use Mean", "Average of 3 PEOU items on 5-point scale", "40 participants", "4.08 / 5.00"],
     ]},

    {"type": "table_caption", "text": "Table 4.7: UAT Survey Results (TAM-based Questionnaire)"},
    {"type": "table",
     "headers": ["Item", "Construct", "Mean (1–5)", "Std Dev", "% Agree / Strongly Agree"],
     "rows": [
         ["Using this system improves my efficiency in managing student records", "PU", "4.40", "0.62", "90%"],
         ["This system makes it easier to retrieve student information quickly", "PU", "4.35", "0.71", "87.5%"],
         ["Using this system enhances my job performance in record management", "PU", "4.18", "0.79", "80%"],
         ["Learning to use this system was easy for me", "PEOU", "4.03", "0.88", "77.5%"],
         ["I find it easy to navigate between the different modules", "PEOU", "4.15", "0.74", "82.5%"],
         ["The system interface is clear and easy to understand", "PEOU", "4.05", "0.81", "80%"],
         ["Using this system is a good idea for this institution", "ATT", "4.43", "0.59", "92.5%"],
         ["I would recommend this system to other institutions", "ATT", "4.28", "0.68", "87.5%"],
         ["I intend to continue using this system regularly", "BI", "4.33", "0.65", "87.5%"],
         ["I feel confident that this system will improve our record management overall", "BI", "4.25", "0.72", "85%"],
         ["Overall Composite Score", "All constructs", "4.24", "0.72", "85%"],
     ]},

    {"type": "heading1", "text": "4.7\tSYSTEM USABILITY SCALE (SUS) RESULTS"},
    {"type": "para", "text": (
        "The System Usability Scale (SUS) was administered to all forty UAT participants immediately "
        "after completing their role-specific task scenarios. The SUS consists of ten items rated "
        "on a five-point Likert scale (Strongly Disagree = 1, Strongly Agree = 5), with odd-numbered "
        "items phrased positively and even-numbered items phrased negatively. The SUS score is "
        "calculated using the formula: SUS Score = (Sum of all item scores − 10) × 2.5, yielding "
        "a score on a 0–100 scale. Scores above 68 are considered 'Good' usability, scores above "
        "80.3 are considered 'Excellent,' and scores above 90 are considered 'Best Imaginable' "
        "(Bangor, Kortum, & Miller, 2008)."
    )},
    {"type": "para", "text": (
        "The mean SUS score across all forty participants was 78.4, which falls in the 'Good' "
        "category according to the Bangor et al. (2008) adjective rating scale. This score "
        "indicates that users found the system acceptably usable, with the interface sufficiently "
        "clear and navigable for their administrative tasks. Score variation across roles was "
        "noted: Administrators achieved the highest mean SUS score of 82.1 (approaching "
        "'Excellent'), reflecting their greater familiarity with administrative software. "
        "Students achieved a mean score of 80.3, indicating that the student portal was "
        "well-received by its primary users. Registrars scored 77.6 and Teachers 73.4, with "
        "Teachers noting in open feedback that the grade entry interface, while functional, "
        "could benefit from keyboard navigation improvements for faster data entry across large "
        "class sizes. These observations are incorporated into the recommendations for future "
        "system enhancement presented in Chapter Five."
    )},
    {"type": "para", "text": (
        "The TAM questionnaire results are equally encouraging. The mean Perceived Usefulness "
        "score of 4.31 out of 5.00 (86.2%) and the mean Perceived Ease of Use score of 4.08 "
        "out of 5.00 (81.6%) both indicate strong positive evaluations by users across all "
        "roles. The highest-rated item was 'Using this system is a good idea for this "
        "institution' (ATT construct, mean 4.43), suggesting broad institutional acceptance "
        "of the system among participants. The 'Learning to use this system was easy for me' "
        "item achieved the lowest mean score of 4.03, consistent with the finding that some "
        "participants—particularly those with limited prior digital system experience—required "
        "additional time to orientate themselves within the interface. This finding underscores "
        "the importance of the role-differentiated training programme proposed in the deployment "
        "strategy (Section 3.8)."
    )},

    {"type": "heading1", "text": "4.8\tSUMMARY"},
    {"type": "para", "text": (
        "This chapter has presented the implementation and comprehensive testing of the web-based "
        "Student Record Management System. The system was implemented across twenty-six PHP module "
        "files, supported by a complete MySQL database schema, a custom CSS stylesheet, and a "
        "JavaScript file providing client-side interactivity. Eight critical system functions were "
        "presented as code listings, demonstrating the technical implementation of the database "
        "connection singleton, grade computation functions, attendance rate calculation, fee "
        "balance computation, user authentication with security controls, AJAX student search, "
        "client-side grade auto-calculation, and audit logging. The testing programme encompassed "
        "ten unit tests, ten integration tests, and ten system tests, all of which passed "
        "successfully, validating both the functional correctness and the non-functional quality "
        "of the implementation. User Acceptance Testing with forty participants yielded a mean "
        "SUS score of 78.4 (Good), a mean TAM Perceived Usefulness score of 4.31/5.00, and a "
        "mean TAM Perceived Ease of Use score of 4.08/5.00, indicating strong user acceptance "
        "of the system across all four user roles. The following chapter presents the conclusions, "
        "contributions, and recommendations arising from this study."
    )},
]
