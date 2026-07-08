"""Chapter 3 content blocks."""

CH3 = [
    {"type": "chapter_title", "text": "CHAPTER THREE"},
    {"type": "chapter_subtitle", "text": "SYSTEM ANALYSIS AND DESIGN"},

    {"type": "heading1", "text": "3.0\tINTRODUCTION"},
    {"type": "para", "text": (
        "This chapter presents the system analysis and design for the web-based Student Record "
        "Management System (SRMS). The chapter begins by documenting the results of the requirements "
        "analysis, distinguishing functional requirements that describe what the system must do from "
        "non-functional requirements that describe the quality attributes the system must exhibit. "
        "The three-tier system architecture is then presented and justified, followed by a detailed "
        "database design comprising the Entity-Relationship Diagram, relational schema, data "
        "dictionary, and database table structure summary. The user interface design philosophy is "
        "discussed with reference to the UI/UX principles identified in Chapter Two. The development "
        "tools and technology stack are formally specified and justified. The chapter concludes with "
        "presentations of the implementation plan, testing strategy, and data migration and "
        "deployment strategy."
    )},

    {"type": "heading1", "text": "3.1\tREQUIREMENT SPECIFICATION"},
    {"type": "para", "text": (
        "The requirements for the proposed SRMS were elicited through a structured process combining "
        "a review of existing literature on SRMS functionality, an examination of the Nigerian "
        "educational regulatory framework as prescribed by the National Universities Commission (NUC), "
        "informal interviews with administrative staff and students at the study institution, and an "
        "analysis of the operational limitations of the current manual record-keeping process. "
        "The requirements are organised into two categories: functional requirements, which specify "
        "the behaviours and capabilities the system must provide, and non-functional requirements, "
        "which specify the performance, security, usability, and other quality constraints that "
        "govern how the system performs its functions."
    )},

    {"type": "table_caption", "text": "Table 3.1: Functional Requirements Specification"},
    {"type": "table",
     "headers": ["Req. ID", "Module", "Requirement Description", "Priority"],
     "rows": [
         ["FR-01", "Authentication", "The system shall authenticate all users with a username and password before granting access", "Must Have"],
         ["FR-02", "Authentication", "The system shall support four user roles: Admin, Registrar, Teacher, Student", "Must Have"],
         ["FR-03", "Authentication", "The system shall log all failed login attempts and lock accounts after 5 consecutive failures", "Must Have"],
         ["FR-04", "Student Mgmt", "The system shall allow Registrars to create, read, update, and delete student profiles", "Must Have"],
         ["FR-05", "Student Mgmt", "Student profiles shall include personal, guardian, academic, and admission information", "Must Have"],
         ["FR-06", "Student Mgmt", "The system shall allow AJAX-powered search of students by name or matric number", "Must Have"],
         ["FR-07", "Course Mgmt", "The system shall allow creation and management of courses with credit units, level, and semester", "Must Have"],
         ["FR-08", "Course Mgmt", "The system shall support assignment of teachers to courses per academic session", "Must Have"],
         ["FR-09", "Grades", "The system shall allow teachers to enter CA scores and exam scores per student per course", "Must Have"],
         ["FR-10", "Grades", "The system shall automatically compute total score, letter grade, and grade points from entered scores", "Must Have"],
         ["FR-11", "Grades", "The system shall compute GPA per student per session using: GPA = Σ(GP×CU)/Σ(CU)", "Must Have"],
         ["FR-12", "Grades", "The system shall compute CGPA across all completed sessions", "Must Have"],
         ["FR-13", "Attendance", "The system shall allow teachers to record attendance per student per course per date", "Must Have"],
         ["FR-14", "Attendance", "The system shall compute attendance rate as (Present+Late)/Total×100", "Must Have"],
         ["FR-15", "Fees", "The system shall allow definition of fee structures per session, department, and level", "Must Have"],
         ["FR-16", "Fees", "The system shall record fee payments and compute outstanding balance", "Must Have"],
         ["FR-17", "Fees", "The system shall generate payment receipts with unique receipt numbers", "Must Have"],
         ["FR-18", "Reports", "The system shall generate printable academic transcripts per student", "Must Have"],
         ["FR-19", "Reports", "The system shall generate class lists per course per session", "Must Have"],
         ["FR-20", "Reports", "The system shall generate attendance summary reports per course", "Must Have"],
         ["FR-21", "Dashboard", "The system shall display a dashboard with total students, courses, fees collected, and pending fees", "Must Have"],
         ["FR-22", "Dashboard", "The dashboard shall display a bar chart of student distribution per department", "Should Have"],
         ["FR-23", "Dashboard", "The dashboard shall display a pie chart of grade distribution", "Should Have"],
         ["FR-24", "Audit", "The system shall log all data creation, modification, and deletion events with user ID and timestamp", "Must Have"],
         ["FR-25", "Users", "Admins shall be able to create, activate, deactivate, and assign roles to user accounts", "Must Have"],
         ["FR-26", "Student Portal", "Students shall be able to view their own grades, GPA, attendance, and fee balance", "Must Have"],
         ["FR-27", "Settings", "Admins shall be able to configure institutional name, session, and grade scale settings", "Should Have"],
     ]},

    {"type": "table_caption", "text": "Table 3.2: Non-Functional Requirements Specification"},
    {"type": "table",
     "headers": ["Req. ID", "Category", "Requirement Description", "Metric/Target"],
     "rows": [
         ["NFR-01", "Performance", "Page load time for standard views shall not exceed 3 seconds on a 10 Mbps connection", "< 3 seconds"],
         ["NFR-02", "Performance", "Database queries shall complete in under 500 milliseconds for datasets up to 10,000 students", "< 500 ms"],
         ["NFR-03", "Security", "All passwords shall be hashed using bcrypt with a minimum cost factor of 10", "bcrypt cost ≥ 10"],
         ["NFR-04", "Security", "All database interactions shall use PDO prepared statements to prevent SQL injection", "Zero raw queries"],
         ["NFR-05", "Security", "All POST forms shall include a CSRF token validated server-side", "100% form coverage"],
         ["NFR-06", "Usability", "The system shall achieve a System Usability Scale (SUS) score of at least 70 (Good)", "SUS ≥ 70"],
         ["NFR-07", "Usability", "The system shall be navigable by a new user within 30 minutes without formal training", "< 30 min onboarding"],
         ["NFR-08", "Reliability", "The system shall maintain data integrity through ACID-compliant transactions for grade entry", "100% ACID compliance"],
         ["NFR-09", "Scalability", "The system architecture shall support up to 5,000 concurrent student records without redesign", "5,000+ records"],
         ["NFR-10", "Compatibility", "The system shall function correctly on Chrome 100+, Firefox 100+, Edge 100+, and Safari 15+", "4 major browsers"],
         ["NFR-11", "Responsiveness", "All pages shall be responsive and usable on devices with viewport widths from 320px to 2560px", "Mobile + desktop"],
         ["NFR-12", "Maintainability", "The codebase shall follow a modular MVC-like structure with separation of concerns", "Modular architecture"],
         ["NFR-13", "Availability", "The system shall target 99% uptime during the academic year", "99% uptime"],
     ]},

    {"type": "heading1", "text": "3.2\tSYSTEM ARCHITECTURE"},
    {"type": "para", "text": (
        "The proposed SRMS adopts a three-tier client-server architecture, which provides a clear "
        "separation of concerns among the presentation layer (client), the application logic layer "
        "(web server), and the data management layer (database server). This architectural pattern "
        "is the standard for web-based information systems and is particularly well-suited to the "
        "deployment context of Nigerian educational institutions, where thin-client web browsers are "
        "the primary access interface and server-side processing enables centralised data management "
        "accessible to multiple concurrent users (O'Brien & Marakas, 2011). The three-tier "
        "architecture is depicted in Figure 3.2."
    )},

    {"type": "mermaid_caption", "text": "Figure 3.2: Three-Tier System Architecture Diagram"},
    {"type": "mermaid", "code": """graph TB
    subgraph Presentation["Presentation Layer (Client)"]
        B1[Web Browser\\nChrome / Firefox / Edge / Safari]
        B2[Mobile Browser\\nResponsive Bootstrap 5 UI]
    end

    subgraph Application["Application Layer (Web Server - Apache / PHP 8.1)"]
        A1[Authentication Module]
        A2[Student Management Module]
        A3[Course Management Module]
        A4[Grade & GPA Module]
        A5[Attendance Module]
        A6[Fee Management Module]
        A7[Report Generation Module]
        A8[Dashboard & Analytics Module]
        A9[User Management Module]
        A10[Audit Log Module]
        API[REST-like API Endpoints\\nJSON Responses for AJAX]
    end

    subgraph Data["Data Layer (MySQL 8.0 Database Server)"]
        D1[(users)]
        D2[(students)]
        D3[(courses)]
        D4[(grades)]
        D5[(attendance)]
        D6[(fee_payments)]
        D7[(audit_logs)]
        D8[(departments)]
        D9[(academic_sessions)]
    end

    Presentation <-->|HTTPS / HTML / JSON| Application
    Application <-->|PDO Prepared Statements| Data"""},

    {"type": "para", "text": (
        "In this architecture, the Presentation Layer consists of the web browser interface rendered "
        "using Bootstrap 5, HTML5, CSS3, and JavaScript. The browser communicates with the Application "
        "Layer over HTTPS using standard HTTP request-response cycles for page navigation and AJAX "
        "requests for asynchronous data operations such as student search and grade auto-calculation. "
        "The Application Layer, running on an Apache HTTP Server with PHP 8.1, hosts the business "
        "logic of the system, including all data validation, computation (GPA/CGPA, fee balances, "
        "attendance rates), access control enforcement, and report generation. The Data Layer, "
        "implemented in MySQL 8.0, stores all persistent data in a normalised relational schema "
        "and is accessed exclusively through PHP PDO prepared statements, ensuring both security "
        "against SQL injection and efficient parameterised query execution."
    )},

    # Use Case Diagram
    {"type": "para", "text": (
        "The interactions between the four user roles and the system's functional modules are "
        "captured in the Use Case Diagram presented in Figure 3.1. This diagram illustrates the "
        "scope of accessible functionality for each role, reflecting the role-based access control "
        "model implemented throughout the system."
    )},
    {"type": "mermaid_caption", "text": "Figure 3.1: Use Case Diagram for the Student Record Management System"},
    {"type": "mermaid", "code": """graph LR
    Admin((Admin))
    Registrar((Registrar))
    Teacher((Teacher))
    Student((Student))

    Admin --> UC1[Manage Users]
    Admin --> UC2[Configure System Settings]
    Admin --> UC3[View Audit Logs]
    Admin --> UC4[Manage Departments]
    Admin --> UC5[View All Reports]
    Admin --> UC6[Manage Academic Sessions]

    Registrar --> UC7[Manage Student Profiles]
    Registrar --> UC8[Manage Course Enrolment]
    Registrar --> UC9[Generate Transcripts]
    Registrar --> UC10[Generate Class Lists]
    Registrar --> UC11[Manage Fee Structures]
    Registrar --> UC12[Record Fee Payments]

    Teacher --> UC13[Enter Grades]
    Teacher --> UC14[Mark Attendance]
    Teacher --> UC15[View Class List]
    Teacher --> UC16[View Grade Summary]
    Teacher --> UC17[View Attendance Report]

    Student --> UC18[View Own Grades & GPA/CGPA]
    Student --> UC19[View Own Attendance]
    Student --> UC20[View Fee Balance]
    Student --> UC21[Download Transcript]
    Student --> UC22[Update Contact Info]"""},

    {"type": "heading1", "text": "3.3\tDATABASE DESIGN"},
    {"type": "para", "text": (
        "The database design is central to the SRMS, as all system functionality depends on the "
        "efficient storage and retrieval of student-related data. The database was designed according "
        "to the principles of relational database normalisation, targeting Third Normal Form (3NF) "
        "to eliminate redundancy and ensure data integrity. The design process began with the "
        "identification of entities and their attributes from the requirements specification, "
        "followed by the definition of relationships between entities, and culminated in the "
        "construction of the Entity-Relationship Diagram (ERD) shown in Figure 3.3 and the detailed "
        "Data Flow Diagram at context level (DFD Level 0) shown in Figure 3.4."
    )},

    {"type": "mermaid_caption", "text": "Figure 3.3: Entity-Relationship Diagram (ERD) for the SRMS"},
    {"type": "mermaid", "code": """erDiagram
    USERS {
        int id PK
        varchar username UK
        varchar email UK
        varchar password_hash
        enum role
        varchar full_name
        varchar phone
        enum status
        datetime created_at
    }
    DEPARTMENTS {
        int id PK
        varchar name
        varchar code UK
        varchar faculty
        varchar head_of_dept
    }
    ACADEMIC_SESSIONS {
        int id PK
        varchar session_name
        date start_date
        date end_date
        tinyint is_current
        enum semester
    }
    STUDENTS {
        int id PK
        varchar matric_number UK
        varchar first_name
        varchar last_name
        date date_of_birth
        enum gender
        varchar email
        int department_id FK
        enum level
        date admission_date
        enum status
        varchar guardian_name
        varchar guardian_phone
        int user_id FK
    }
    COURSES {
        int id PK
        varchar course_code UK
        varchar course_title
        int credit_units
        int department_id FK
        enum level
        enum semester
    }
    COURSE_ASSIGNMENTS {
        int id PK
        int course_id FK
        int teacher_user_id FK
        int session_id FK
    }
    STUDENT_COURSES {
        int id PK
        int student_id FK
        int course_id FK
        int session_id FK
    }
    GRADES {
        int id PK
        int student_id FK
        int course_id FK
        int session_id FK
        decimal ca_score
        decimal exam_score
        decimal total_score
        varchar letter_grade
        decimal grade_points
        int credit_units
        int entered_by FK
    }
    ATTENDANCE {
        int id PK
        int student_id FK
        int course_id FK
        int session_id FK
        date date
        enum status
        int marked_by FK
    }
    FEE_STRUCTURES {
        int id PK
        int session_id FK
        int department_id FK
        enum level
        varchar fee_type
        decimal amount
        date due_date
    }
    FEE_PAYMENTS {
        int id PK
        int student_id FK
        int session_id FK
        int fee_structure_id FK
        decimal amount_paid
        date payment_date
        enum payment_method
        varchar receipt_number UK
        int received_by FK
    }
    AUDIT_LOGS {
        int id PK
        int user_id FK
        varchar action
        varchar module
        text description
        varchar ip_address
        datetime created_at
    }

    USERS ||--o{ STUDENTS : "has student profile"
    DEPARTMENTS ||--o{ STUDENTS : "enrolled in"
    DEPARTMENTS ||--o{ COURSES : "offers"
    ACADEMIC_SESSIONS ||--o{ COURSE_ASSIGNMENTS : "in session"
    COURSES ||--o{ COURSE_ASSIGNMENTS : "assigned"
    USERS ||--o{ COURSE_ASSIGNMENTS : "teaches"
    STUDENTS ||--o{ STUDENT_COURSES : "enrolled"
    COURSES ||--o{ STUDENT_COURSES : "taken by"
    ACADEMIC_SESSIONS ||--o{ STUDENT_COURSES : "during"
    STUDENTS ||--o{ GRADES : "receives"
    COURSES ||--o{ GRADES : "graded in"
    ACADEMIC_SESSIONS ||--o{ GRADES : "for session"
    STUDENTS ||--o{ ATTENDANCE : "tracked"
    COURSES ||--o{ ATTENDANCE : "for course"
    ACADEMIC_SESSIONS ||--o{ FEE_STRUCTURES : "applies in"
    DEPARTMENTS ||--o{ FEE_STRUCTURES : "charged to"
    STUDENTS ||--o{ FEE_PAYMENTS : "makes"
    FEE_STRUCTURES ||--o{ FEE_PAYMENTS : "for"
    USERS ||--o{ AUDIT_LOGS : "generates"
"""},

    {"type": "mermaid_caption", "text": "Figure 3.4: System Data Flow Diagram – Level 0 (Context Diagram)"},
    {"type": "mermaid", "code": """graph LR
    Admin([Admin])
    Registrar([Registrar])
    Teacher([Teacher])
    Student([Student])

    SRMS[("SRMS\n(Web Application)")]

    Admin -->|User management commands\nSystem configuration| SRMS
    SRMS -->|Audit logs\nSystem reports\nUser accounts| Admin

    Registrar -->|Student data\nEnrolment data\nFee payment records| SRMS
    SRMS -->|Transcripts\nClass lists\nFee statements| Registrar

    Teacher -->|Grade entries\nAttendance records| SRMS
    SRMS -->|Grade summary\nAttendance reports\nClass roster| Teacher

    Student -->|Login credentials\nProfile update| SRMS
    SRMS -->|Grade results\nGPA/CGPA\nAttendance record\nFee balance| Student"""},

    {"type": "table_caption", "text": "Table 3.3: Database Table Structures Summary"},
    {"type": "table",
     "headers": ["Table Name", "Primary Key", "Key Foreign Keys", "Record Count (Sample)", "Purpose"],
     "rows": [
         ["users", "id (INT, AI)", "—", "~50", "Stores all system user accounts across all roles"],
         ["departments", "id (INT, AI)", "—", "~10", "Stores academic departments/faculties"],
         ["academic_sessions", "id (INT, AI)", "—", "~10", "Stores academic year and semester information"],
         ["students", "id (INT, AI)", "department_id, user_id", "~5,000", "Stores comprehensive student profile data"],
         ["courses", "id (INT, AI)", "department_id", "~200", "Stores course/subject definitions"],
         ["course_assignments", "id (INT, AI)", "course_id, teacher_user_id, session_id", "~500", "Maps teachers to courses per session"],
         ["student_courses", "id (INT, AI)", "student_id, course_id, session_id", "~15,000", "Records student course enrolment"],
         ["grades", "id (INT, AI)", "student_id, course_id, session_id, entered_by", "~15,000", "Stores CA, exam, total, grade, and grade points"],
         ["attendance", "id (INT, AI)", "student_id, course_id, session_id, marked_by", "~90,000", "Records daily attendance status"],
         ["fee_structures", "id (INT, AI)", "session_id, department_id", "~100", "Defines fee amounts per category"],
         ["fee_payments", "id (INT, AI)", "student_id, session_id, fee_structure_id, received_by", "~8,000", "Records individual payment transactions"],
         ["audit_logs", "id (INT, AI)", "user_id", "Unlimited", "Immutable record of all system actions"],
     ]},

    {"type": "table_caption", "text": "Table 3.6: Data Dictionary for Core Tables"},
    {"type": "table",
     "headers": ["Table", "Column", "Data Type", "Constraints", "Description"],
     "rows": [
         ["students", "matric_number", "VARCHAR(20)", "NOT NULL, UNIQUE", "Unique institutional student identifier e.g. CSC/2020/001"],
         ["students", "level", "ENUM('100','200','300','400','500')", "NOT NULL", "Current academic level of the student"],
         ["students", "status", "ENUM('active','suspended','graduated','withdrawn')", "DEFAULT 'active'", "Current enrolment status"],
         ["grades", "ca_score", "DECIMAL(5,2)", "NOT NULL, CHECK(0–40)", "Continuous Assessment score out of 40"],
         ["grades", "exam_score", "DECIMAL(5,2)", "NOT NULL, CHECK(0–60)", "Examination score out of 60"],
         ["grades", "total_score", "DECIMAL(5,2)", "GENERATED ALWAYS AS (ca_score+exam_score)", "Computed total; not stored separately"],
         ["grades", "letter_grade", "VARCHAR(2)", "NOT NULL", "A, B, C, D, or F per NUC scale"],
         ["grades", "grade_points", "DECIMAL(3,1)", "NOT NULL", "4.0, 3.0, 2.0, 1.0, or 0.0"],
         ["attendance", "status", "ENUM('present','absent','late','excused')", "NOT NULL", "Attendance status for the record date"],
         ["fee_payments", "receipt_number", "VARCHAR(30)", "NOT NULL, UNIQUE", "System-generated receipt e.g. RCP-20240913-7842"],
         ["fee_payments", "payment_method", "ENUM('bank_transfer','cash','online')", "NOT NULL", "Method by which payment was received"],
         ["users", "role", "ENUM('admin','registrar','teacher','student')", "NOT NULL", "Determines system access permissions"],
         ["users", "password_hash", "VARCHAR(255)", "NOT NULL", "bcrypt hash of user password"],
         ["academic_sessions", "is_current", "TINYINT(1)", "DEFAULT 0", "Flag identifying the active academic session"],
     ]},

    {"type": "table_caption", "text": "Table 3.5: Entity Relationship Mapping Summary"},
    {"type": "table",
     "headers": ["Entity A", "Relationship", "Entity B", "Cardinality", "Notes"],
     "rows": [
         ["Department", "has many", "Students", "1:N", "A student belongs to one department"],
         ["Department", "offers many", "Courses", "1:N", "A course belongs to one department"],
         ["Student", "enrolled in many", "Courses", "M:N", "Via student_courses junction table"],
         ["Course", "assigned to one", "Teacher", "M:N per session", "Via course_assignments; one teacher per course per session"],
         ["Student", "has many", "Grades", "1:N", "One grade record per course per session"],
         ["Student", "has many", "Attendance Records", "1:N", "One record per course per date"],
         ["Student", "makes many", "Fee Payments", "1:N", "Multiple payments per session per fee type"],
         ["Academic Session", "frames", "Grades, Attendance, Fees", "1:N each", "All transactional records are session-scoped"],
         ["User", "generates", "Audit Logs", "1:N", "Every user action produces an audit entry"],
     ]},

    {"type": "heading1", "text": "3.4\tUSER INTERFACE DESIGN"},
    {"type": "para", "text": (
        "The user interface design of the SRMS was guided by the UI/UX best practices identified "
        "in Chapter Two, with particular emphasis on Nielsen's (1994) usability heuristics, the "
        "principle of role-appropriate information presentation, and the practical accessibility "
        "needs of Nigerian institutional users with varying levels of digital literacy. The "
        "interface employs a fixed left sidebar navigation layout that provides persistent access "
        "to all authorised modules without requiring the user to return to a home screen. "
        "The sidebar uses a deep navy blue colour scheme (#1a237e) consistent with an academic "
        "professional aesthetic, with white text and icon labels for high contrast readability. "
        "The main content area uses a white background with Bootstrap's card components to "
        "segment information into clearly bounded visual groups."
    )},
    {"type": "para", "text": (
        "The system implements a consistent two-column responsive layout: the sidebar occupies "
        "approximately 250 pixels on desktop viewports and collapses to an off-canvas drawer on "
        "mobile viewports below 768 pixels, activated by a hamburger menu icon. The top navigation "
        "bar displays the current user's name, role, and a notification bell icon alongside a "
        "dark mode toggle. The dark mode, which persists across sessions via localStorage, inverts "
        "the colour scheme to a dark background with light text, reducing eye strain during "
        "extended administrative sessions. Flash notification messages, implemented as dismissible "
        "Bootstrap alerts in green (success), red (error), and yellow (warning), appear at the "
        "top of the main content area immediately after any state-changing operation, providing "
        "the immediate feedback prescribed by Nielsen's visibility of system status heuristic."
    )},

    {"type": "heading1", "text": "3.5\tDEVELOPMENT TOOLS AND TECHNOLOGIES"},
    {"type": "table_caption", "text": "Table 3.4: Technology Stack Selection and Justification"},
    {"type": "table",
     "headers": ["Technology", "Version", "Role in System", "Justification"],
     "rows": [
         ["PHP", "8.1", "Server-side application logic", "Most widely supported on Nigerian shared hosting; JIT performance improvements; strong PDO support"],
         ["MySQL", "8.0", "Relational database management", "ACID-compliant; native PHP integration; generated columns for computed fields; JSON support"],
         ["Apache HTTP Server", "2.4", "Web server", "Standard LAMP stack component; .htaccess rewrite rules supported; widely available"],
         ["Bootstrap", "5.3", "Frontend CSS framework", "Responsive grid; extensive pre-built components; no jQuery dependency; mobile-first"],
         ["jQuery", "3.7", "AJAX and DOM manipulation", "Simplified AJAX calls; wide developer familiarity; compact CDN delivery"],
         ["Chart.js", "4.4", "Dashboard data visualisation", "Lightweight; responsive canvas charts; no build tools required; simple API"],
         ["HTML5", "—", "Markup structure", "Semantic elements; form validation attributes; canvas support for Chart.js"],
         ["CSS3", "—", "Presentation and styling", "Flexbox/Grid layouts; media queries for responsiveness; custom properties for theming"],
         ["JavaScript (ES6+)", "—", "Client-side interactivity", "Grade auto-calculation; AJAX search; dark mode toggle; modal confirmations"],
         ["XAMPP / LAMP", "—", "Development environment", "Cross-platform local development stack replicating production environment"],
         ["Git", "2.x", "Version control", "Track changes; branch-based development; documentation of implementation history"],
         ["Visual Studio Code", "Latest", "IDE", "PHP/HTML/CSS/JS syntax highlighting; integrated terminal; live server extension"],
     ]},

    {"type": "heading1", "text": "3.6\tPROCESS FLOWCHARTS"},
    {"type": "para", "text": (
        "The key operational processes within the SRMS are documented as process flowcharts to "
        "illustrate the logical flow of control and data through each module. These diagrams serve "
        "both as design documentation and as a reference for implementation. Five core process "
        "flows are presented: the login process, student registration, grade entry, fee payment "
        "recording, and report generation."
    )},

    {"type": "mermaid_caption", "text": "Figure 3.5: Login Process Flowchart"},
    {"type": "mermaid", "code": """flowchart TD
    A([Start]) --> B[Display Login Form]
    B --> C[User Enters Username & Password]
    C --> D[Validate CSRF Token]
    D --> E{CSRF Valid?}
    E -- No --> F[Return 403 Error]
    E -- Yes --> G[Query Database for Username]
    G --> H{User Found?}
    H -- No --> I[Increment Failed Attempts]
    I --> J{Attempts >= 5?}
    J -- Yes --> K[Lock Account for 30 min]
    J -- No --> L[Show: Invalid credentials]
    L --> B
    H -- Yes --> M[Verify Password with password_verify]
    M --> N{Password Correct?}
    N -- No --> I
    N -- Yes --> O[Regenerate Session ID]
    O --> P[Set Session Variables: user_id, role, name]
    P --> Q[Log Successful Login to Audit Log]
    Q --> R{What is User Role?}
    R -- admin/registrar/teacher --> S[Redirect to Dashboard]
    R -- student --> T[Redirect to Student Portal]
    S --> U([End])
    T --> U"""},

    {"type": "mermaid_caption", "text": "Figure 3.6: Student Registration Process Flowchart"},
    {"type": "mermaid", "code": """flowchart TD
    A([Start]) --> B[Registrar Opens Add Student Form]
    B --> C[Enter Student Personal Information]
    C --> D[Enter Guardian Information]
    D --> E[Enter Academic Information\\nDept, Level, Admission Date]
    E --> F[Submit Form]
    F --> G[Server: Validate CSRF Token]
    G --> H{Valid?}
    H -- No --> I[Reject: 403 Forbidden]
    H -- Yes --> J[Server: Validate Required Fields]
    J --> K{All Fields Valid?}
    K -- No --> L[Return Form with Inline Error Messages]
    L --> C
    K -- Yes --> M[Check Matric Number Uniqueness]
    M --> N{Unique?}
    N -- No --> O[Error: Matric Number Already Exists]
    O --> C
    N -- Yes --> P[Begin Database Transaction]
    P --> Q[INSERT into students table]
    Q --> R[Optionally Create User Account\\nif student portal access granted]
    R --> S[COMMIT Transaction]
    S --> T[Log Action to Audit Log]
    T --> U[Show Success Flash Message]
    U --> V[Redirect to Student List]
    V --> W([End])"""},

    {"type": "mermaid_caption", "text": "Figure 3.7: Grade Entry Process Flowchart"},
    {"type": "mermaid", "code": """flowchart TD
    A([Start]) --> B[Teacher Selects Course and Session]
    B --> C[System Loads Enrolled Students for Course]
    C --> D[Display Grade Entry Table with Student Names]
    D --> E[Teacher Enters CA Score 0-40 and Exam Score 0-60]
    E --> F[JavaScript Auto-Calculates:\\nTotal = CA + Exam\\nLetter Grade\\nGrade Points]
    F --> G[Teacher Reviews and Submits Form]
    G --> H[Server: Validate CSRF Token]
    H --> I{Valid?}
    I -- No --> J[Reject: 403]
    I -- Yes --> K[Validate Score Ranges]
    K --> L{Scores Valid?}
    L -- No --> M[Return Errors]
    M --> E
    L -- Yes --> N[Begin Transaction]
    N --> O[For Each Student:\\nUPSERT grades record]
    O --> P[COMMIT]
    P --> Q[Log to Audit Log]
    Q --> R[Show Success]
    R --> S([End])"""},

    {"type": "mermaid_caption", "text": "Figure 3.8: Fee Payment Recording Process Flowchart"},
    {"type": "mermaid", "code": """flowchart TD
    A([Start]) --> B[Registrar Opens Add Payment Form]
    B --> C[Select Student via AJAX Search]
    C --> D[Select Session and Fee Structure]
    D --> E[System Displays Fee Amount and Current Balance]
    E --> F[Enter Amount Paid and Payment Method]
    F --> G[System Auto-Generates Receipt Number]
    G --> H[Submit Form]
    H --> I[Server: Validate CSRF and Required Fields]
    I --> J{Valid?}
    J -- No --> K[Return Error]
    K --> F
    J -- Yes --> L[INSERT fee_payment record]
    L --> M[Update Balance Computation View]
    M --> N[Log to Audit Log]
    N --> O[Display Receipt Page]
    O --> P([End])"""},

    {"type": "mermaid_caption", "text": "Figure 3.9: Report Generation Process Flowchart"},
    {"type": "mermaid", "code": """flowchart TD
    A([Start]) --> B[User Selects Report Type]
    B --> C{Report Type?}
    C -- Transcript --> D[Select Student]
    C -- Class List --> E[Select Course and Session]
    C -- Attendance Summary --> F[Select Course and Session]
    C -- Fee Statement --> G[Select Student and Session]
    D --> H[Query: Grades, GPA, CGPA per session]
    E --> I[Query: Enrolled students + grades]
    F --> J[Query: Attendance records + rate]
    G --> K[Query: Fee structures + payments + balance]
    H --> L[Render Report View with Print CSS]
    I --> L
    J --> L
    K --> L
    L --> M[Browser Print Dialog]
    M --> N[Physical or PDF Output]
    N --> O([End])"""},

    {"type": "mermaid_caption", "text": "Figure 3.10: Database Schema Diagram"},
    {"type": "mermaid", "code": """graph TB
    U[users\\nPK: id] --> |entered_by| G[grades\\nPK: id]
    U --> |marked_by| AT[attendance\\nPK: id]
    U --> |received_by| FP[fee_payments\\nPK: id]
    U --> |user_id| S[students\\nPK: id]
    U --> |user_id| AL[audit_logs\\nPK: id]
    U --> |teacher_user_id| CA[course_assignments\\nPK: id]
    D[departments\\nPK: id] --> S
    D --> C[courses\\nPK: id]
    D --> FS[fee_structures\\nPK: id]
    AS[academic_sessions\\nPK: id] --> CA
    AS --> SC[student_courses\\nPK: id]
    AS --> G
    AS --> AT
    AS --> FS
    AS --> FP
    S --> SC
    S --> G
    S --> AT
    S --> FP
    C --> CA
    C --> SC
    C --> G
    C --> AT
    FS --> FP"""},

    {"type": "mermaid_caption", "text": "Figure 3.11: Deployment Architecture Diagram"},
    {"type": "mermaid", "code": """graph TB
    subgraph Client["Client Devices"]
        PC[Desktop/Laptop\\nWeb Browser]
        MB[Mobile Phone\\nMobile Browser]
    end

    subgraph Internet["Internet / Intranet"]
        CDN[CDN\\nBootstrap CSS\\nJQuery JS\\nChart.js]
    end

    subgraph Server["Web Server (LAMP Stack)"]
        direction TB
        NX[Apache 2.4\\nHTTPS/TLS]
        PHP[PHP 8.1 FPM]
        NX --> PHP
    end

    subgraph DB["Database Server"]
        MySQL[(MySQL 8.0\\nSRMS Database)]
    end

    subgraph Backup["Backup"]
        BK[Automated Daily\\nMySQL Dump\\nCloud Storage]
    end

    PC -->|HTTPS| NX
    MB -->|HTTPS| NX
    PC -.->|CDN Assets| CDN
    MB -.->|CDN Assets| CDN
    PHP <-->|PDO / TCP 3306| MySQL
    MySQL -->|mysqldump cron| BK"""},

    {"type": "heading1", "text": "3.7\tTESTING STRATEGY"},
    {"type": "para", "text": (
        "The testing strategy for the SRMS encompasses four distinct levels: unit testing, integration "
        "testing, system testing, and user acceptance testing. Unit testing is performed on individual "
        "PHP functions—particularly the GPA/CGPA computation functions, the grade-letter conversion "
        "function, the attendance rate calculator, and the fee balance computation function—to verify "
        "that each function produces correct outputs for a comprehensive set of known inputs, including "
        "boundary cases and invalid inputs. Integration testing verifies that the interactions between "
        "system modules produce correct end-to-end outcomes, for example, that a grade entered through "
        "the grade entry module is correctly reflected in the GPA displayed on the student profile "
        "view and in the generated transcript."
    )},
    {"type": "para", "text": (
        "System testing evaluates the non-functional requirements of the system including performance, "
        "security, and cross-browser compatibility. Performance testing measures page load times and "
        "database query execution times under normal operating conditions with a dataset of five "
        "thousand student records. Security testing includes manual verification of SQL injection "
        "prevention through prepared statement inspection, CSRF protection testing by submitting "
        "forged requests, and session security testing by examining session ID regeneration behaviour "
        "and cookie attributes. Cross-browser testing is conducted on Google Chrome, Mozilla Firefox, "
        "Microsoft Edge, and Safari to verify consistent rendering and functionality across all "
        "target browsers."
    )},
    {"type": "para", "text": (
        "User Acceptance Testing (UAT) is conducted with forty purposively selected participants "
        "comprising ten administrators, ten registrars, ten teachers, and ten students. Participants "
        "complete a set of defined test scenarios corresponding to their role and then complete a "
        "combined System Usability Scale (SUS) and TAM-based questionnaire. The SUS provides a "
        "validated overall usability score, while the TAM items specifically measure Perceived "
        "Usefulness and Perceived Ease of Use as predictors of continued adoption intention. The "
        "summary of planned test cases is presented in Table 3.7."
    )},
    {"type": "table_caption", "text": "Table 3.7: Test Cases Summary (Unit and Integration)"},
    {"type": "table",
     "headers": ["Test ID", "Test Type", "Module Under Test", "Test Description", "Expected Result"],
     "rows": [
         ["TC-U01", "Unit", "functions.php: getLetterGrade()", "Input: score=75 → Expected: 'A', grade_points=4.0", "Return ['grade'=>'A','points'=>4.0]"],
         ["TC-U02", "Unit", "functions.php: getLetterGrade()", "Input: score=44 (boundary F/D) → Expected: 'F', 0.0", "Return ['grade'=>'F','points'=>0.0]"],
         ["TC-U03", "Unit", "functions.php: getLetterGrade()", "Input: score=45 (boundary D) → Expected: 'D', 1.0", "Return ['grade'=>'D','points'=>1.0]"],
         ["TC-U04", "Unit", "functions.php: calculateGPA()", "Student with 3 courses: (4×3+3×3+2×2)/(3+3+2)=3.25", "GPA = 3.25"],
         ["TC-U05", "Unit", "functions.php: calculateCGPA()", "Two sessions with GPA 3.25 and 2.80, equal credit units", "CGPA = 3.025"],
         ["TC-U06", "Unit", "functions.php: getAttendanceRate()", "20 classes, 17 present, 1 late: (17+1)/20×100=90%", "Rate = 90.00%"],
         ["TC-U07", "Unit", "functions.php: getFeeBalance()", "Fee=150000, Paid=75000: Balance=75000", "Balance = ₦75,000.00"],
         ["TC-I01", "Integration", "Grade Entry → Student Profile", "Enter grades; verify GPA displayed on student view matches calculation", "GPA matches TC-U04"],
         ["TC-I02", "Integration", "Grade Entry → Transcript", "Enter grades; generate transcript; verify all scores and GPA present", "Transcript matches entered data"],
         ["TC-I03", "Integration", "Attendance Mark → Attendance Report", "Mark attendance; generate report; verify rate computation", "Report matches TC-U06"],
         ["TC-I04", "Integration", "Fee Payment → Fee Statement", "Record payment; view statement; verify balance", "Balance matches TC-U07"],
         ["TC-I05", "Integration", "Student Registration → Enrolment", "Register student; enrol in course; verify appearance in class list", "Student in class list"],
         ["TC-I06", "Integration", "Login → Role Redirect", "Login as teacher; verify redirect to dashboard, not admin panel", "Teacher dashboard shown"],
         ["TC-I07", "Integration", "Audit Log", "Perform grade entry; verify audit log records action, user, timestamp", "Audit entry created"],
     ]},

    {"type": "heading1", "text": "3.8\tDATA MIGRATION AND SYSTEM DEPLOYMENT STRATEGY"},
    {"type": "para", "text": (
        "The deployment of the SRMS in an institution that currently manages student records manually "
        "requires a carefully planned data migration strategy to transfer existing student data into "
        "the new system's database without data loss, corruption, or excessive disruption to ongoing "
        "administrative activities. The data migration process is conceived in five sequential phases, "
        "designed to be executed incrementally over a period of eight to twelve weeks prior to "
        "go-live, in coordination with the institution's academic calendar to minimise operational "
        "impact."
    )},
    {"type": "para", "text": (
        "Phase One is data inventory and audit, in which all existing student records are catalogued "
        "and assessed for completeness, accuracy, and consistency. This phase typically reveals "
        "discrepancies, duplicate records, missing data fields, and inconsistent naming conventions "
        "that must be resolved before migration. Phase Two is data cleaning and standardisation, "
        "in which the inventoried data is cleansed—duplicates are removed, missing fields are "
        "populated where possible from secondary sources, and data formats are standardised to match "
        "the column constraints of the new database schema. Matric numbers, in particular, must be "
        "validated for uniqueness and format consistency before serving as primary identifiers in "
        "the new system."
    )},
    {"type": "para", "text": (
        "Phase Three is data transformation and loading, in which the cleansed data is transformed "
        "from its source format (typically Excel spreadsheets or scanned paper records) into SQL "
        "INSERT statements compatible with the SRMS database schema, and loaded into a staging "
        "database for validation. Phase Four is validation and parallel running, in which both the "
        "legacy manual system and the new SRMS are operated in parallel for a period of four to "
        "six weeks to verify that data in the new system is consistent with the legacy records and "
        "that all system functions produce correct outputs with real institutional data. Phase Five "
        "is go-live and legacy system decommissioning, in which the SRMS becomes the sole "
        "authoritative system for student records, and physical records are archived rather than "
        "destroyed, to provide a historical reference for records predating the system's deployment."
    )},
    {"type": "para", "text": (
        "The system is designed for deployment on a standard LAMP stack hosted either on a "
        "dedicated server within the institution's local network or on a cloud-based virtual "
        "private server (VPS), depending on the institution's infrastructure capacity and internet "
        "reliability. For institutions with stable internet connectivity, a cloud-hosted deployment "
        "on providers such as DigitalOcean, Contabo, or AWS Lightsail is recommended for its "
        "superior reliability, automatic backup capabilities, and geographic redundancy. For "
        "institutions in areas with unreliable internet connectivity, a local network deployment "
        "with a dedicated on-premises server and a UPS (Uninterruptible Power Supply) provides "
        "offline availability within the campus network. Staff training is proposed as a three-day "
        "workshop programme, differentiated by role, covering system navigation, core module "
        "operations, report generation, and basic troubleshooting, supplemented by a printed user "
        "manual and video tutorial resources."
    )},

    {"type": "heading1", "text": "3.9\tSUMMARY"},
    {"type": "para", "text": (
        "This chapter has presented a comprehensive system analysis and design for the web-based "
        "Student Record Management System. The functional and non-functional requirements were "
        "systematically identified and documented, providing a clear specification against which "
        "the implementation and testing efforts in subsequent chapters are benchmarked. The "
        "three-tier architecture was presented and justified as the appropriate structural framework "
        "for the system. A normalised relational database schema was designed and documented through "
        "the ERD, data dictionary, and table structure summary. Key process flows were documented "
        "through seven process flowcharts covering login, student registration, grade entry, fee "
        "payment, and report generation. The technology stack was formally specified and justified, "
        "and a testing strategy encompassing unit, integration, system, and user acceptance testing "
        "was defined. Finally, a five-phase data migration strategy and a deployment architecture "
        "were presented to guide the practical deployment of the system in an institutional context. "
        "The following chapter presents the implementation of the designed system and the results "
        "of all testing activities."
    )},
]
