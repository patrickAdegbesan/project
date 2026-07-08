-- ============================================================
-- Student Record Management System (SRMS)
-- Database Schema
-- MySQL 8.0
-- ============================================================

CREATE DATABASE IF NOT EXISTS srms CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE srms;

SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- TABLE: users
-- ============================================================
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `email` VARCHAR(100) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` ENUM('admin','registrar','teacher','student') NOT NULL DEFAULT 'student',
    `full_name` VARCHAR(150) NOT NULL,
    `phone` VARCHAR(20) DEFAULT NULL,
    `status` ENUM('active','inactive') NOT NULL DEFAULT 'active',
    `last_login` DATETIME DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLE: departments
-- ============================================================
CREATE TABLE IF NOT EXISTS `departments` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(150) NOT NULL,
    `code` VARCHAR(20) NOT NULL UNIQUE,
    `faculty` VARCHAR(150) DEFAULT NULL,
    `head_of_dept` VARCHAR(150) DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLE: academic_sessions
-- ============================================================
CREATE TABLE IF NOT EXISTS `academic_sessions` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `session_name` VARCHAR(20) NOT NULL,
    `start_date` DATE NOT NULL,
    `end_date` DATE NOT NULL,
    `is_current` TINYINT(1) NOT NULL DEFAULT 0,
    `semester` ENUM('first','second') NOT NULL DEFAULT 'first',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLE: students
-- ============================================================
CREATE TABLE IF NOT EXISTS `students` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `matric_number` VARCHAR(20) NOT NULL UNIQUE,
    `first_name` VARCHAR(80) NOT NULL,
    `last_name` VARCHAR(80) NOT NULL,
    `middle_name` VARCHAR(80) DEFAULT NULL,
    `date_of_birth` DATE DEFAULT NULL,
    `gender` ENUM('male','female','other') NOT NULL,
    `email` VARCHAR(100) DEFAULT NULL,
    `phone` VARCHAR(20) DEFAULT NULL,
    `address` TEXT DEFAULT NULL,
    `state_of_origin` VARCHAR(50) DEFAULT NULL,
    `nationality` VARCHAR(50) DEFAULT 'Nigerian',
    `religion` VARCHAR(50) DEFAULT NULL,
    `department_id` INT UNSIGNED NOT NULL,
    `level` ENUM('100','200','300','400','500') NOT NULL DEFAULT '100',
    `admission_date` DATE DEFAULT NULL,
    `graduation_date` DATE DEFAULT NULL,
    `status` ENUM('active','suspended','graduated','withdrawn') NOT NULL DEFAULT 'active',
    `photo` VARCHAR(255) DEFAULT NULL,
    `guardian_name` VARCHAR(150) DEFAULT NULL,
    `guardian_phone` VARCHAR(20) DEFAULT NULL,
    `guardian_email` VARCHAR(100) DEFAULT NULL,
    `guardian_relationship` VARCHAR(50) DEFAULT NULL,
    `guardian_address` TEXT DEFAULT NULL,
    `user_id` INT UNSIGNED DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_student_dept` FOREIGN KEY (`department_id`) REFERENCES `departments`(`id`) ON UPDATE CASCADE,
    CONSTRAINT `fk_student_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLE: courses
-- ============================================================
CREATE TABLE IF NOT EXISTS `courses` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `course_code` VARCHAR(20) NOT NULL UNIQUE,
    `course_title` VARCHAR(200) NOT NULL,
    `credit_units` TINYINT UNSIGNED NOT NULL DEFAULT 2,
    `department_id` INT UNSIGNED NOT NULL,
    `level` ENUM('100','200','300','400','500') NOT NULL,
    `semester` ENUM('first','second') NOT NULL DEFAULT 'first',
    `description` TEXT DEFAULT NULL,
    `status` ENUM('active','inactive') NOT NULL DEFAULT 'active',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_course_dept` FOREIGN KEY (`department_id`) REFERENCES `departments`(`id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLE: course_assignments
-- ============================================================
CREATE TABLE IF NOT EXISTS `course_assignments` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `course_id` INT UNSIGNED NOT NULL,
    `teacher_user_id` INT UNSIGNED NOT NULL,
    `session_id` INT UNSIGNED NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uq_assignment` (`course_id`,`teacher_user_id`,`session_id`),
    CONSTRAINT `fk_ca_course` FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_ca_teacher` FOREIGN KEY (`teacher_user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_ca_session` FOREIGN KEY (`session_id`) REFERENCES `academic_sessions`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLE: student_courses (enrollment)
-- ============================================================
CREATE TABLE IF NOT EXISTS `student_courses` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT UNSIGNED NOT NULL,
    `course_id` INT UNSIGNED NOT NULL,
    `session_id` INT UNSIGNED NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uq_enrollment` (`student_id`,`course_id`,`session_id`),
    CONSTRAINT `fk_sc_student` FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_sc_course` FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_sc_session` FOREIGN KEY (`session_id`) REFERENCES `academic_sessions`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLE: grades
-- ============================================================
CREATE TABLE IF NOT EXISTS `grades` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT UNSIGNED NOT NULL,
    `course_id` INT UNSIGNED NOT NULL,
    `session_id` INT UNSIGNED NOT NULL,
    `ca_score` DECIMAL(5,2) DEFAULT 0.00,
    `exam_score` DECIMAL(5,2) DEFAULT 0.00,
    `total_score` DECIMAL(5,2) AS (ca_score + exam_score) STORED,
    `letter_grade` VARCHAR(2) DEFAULT NULL,
    `grade_points` DECIMAL(3,1) DEFAULT 0.0,
    `credit_units` TINYINT UNSIGNED NOT NULL DEFAULT 2,
    `entered_by` INT UNSIGNED DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY `uq_grade` (`student_id`,`course_id`,`session_id`),
    CONSTRAINT `fk_grade_student` FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_grade_course` FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_grade_session` FOREIGN KEY (`session_id`) REFERENCES `academic_sessions`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_grade_user` FOREIGN KEY (`entered_by`) REFERENCES `users`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLE: attendance
-- ============================================================
CREATE TABLE IF NOT EXISTS `attendance` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT UNSIGNED NOT NULL,
    `course_id` INT UNSIGNED NOT NULL,
    `session_id` INT UNSIGNED NOT NULL,
    `date` DATE NOT NULL,
    `status` ENUM('present','absent','late','excused') NOT NULL DEFAULT 'present',
    `remarks` VARCHAR(255) DEFAULT NULL,
    `marked_by` INT UNSIGNED DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uq_attendance` (`student_id`,`course_id`,`session_id`,`date`),
    CONSTRAINT `fk_att_student` FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_att_course` FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_att_session` FOREIGN KEY (`session_id`) REFERENCES `academic_sessions`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_att_marker` FOREIGN KEY (`marked_by`) REFERENCES `users`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLE: fee_structures
-- ============================================================
CREATE TABLE IF NOT EXISTS `fee_structures` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `session_id` INT UNSIGNED NOT NULL,
    `department_id` INT UNSIGNED DEFAULT NULL,
    `level` ENUM('100','200','300','400','500','all') NOT NULL DEFAULT 'all',
    `fee_type` VARCHAR(100) NOT NULL,
    `amount` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    `due_date` DATE DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_fs_session` FOREIGN KEY (`session_id`) REFERENCES `academic_sessions`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_fs_dept` FOREIGN KEY (`department_id`) REFERENCES `departments`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLE: fee_payments
-- ============================================================
CREATE TABLE IF NOT EXISTS `fee_payments` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT UNSIGNED NOT NULL,
    `session_id` INT UNSIGNED NOT NULL,
    `fee_structure_id` INT UNSIGNED NOT NULL,
    `amount_paid` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    `payment_date` DATE NOT NULL,
    `payment_method` ENUM('bank_transfer','cash','online') NOT NULL DEFAULT 'cash',
    `receipt_number` VARCHAR(50) NOT NULL UNIQUE,
    `remarks` TEXT DEFAULT NULL,
    `received_by` INT UNSIGNED DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_fp_student` FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_fp_session` FOREIGN KEY (`session_id`) REFERENCES `academic_sessions`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_fp_structure` FOREIGN KEY (`fee_structure_id`) REFERENCES `fee_structures`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_fp_receiver` FOREIGN KEY (`received_by`) REFERENCES `users`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLE: audit_logs
-- ============================================================
CREATE TABLE IF NOT EXISTS `audit_logs` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT UNSIGNED DEFAULT NULL,
    `action` VARCHAR(100) NOT NULL,
    `module` VARCHAR(50) NOT NULL,
    `description` TEXT DEFAULT NULL,
    `ip_address` VARCHAR(45) DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_audit_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLE: system_settings
-- ============================================================
CREATE TABLE IF NOT EXISTS `system_settings` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `setting_key` VARCHAR(100) NOT NULL UNIQUE,
    `setting_value` TEXT DEFAULT NULL,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- SEED DATA
-- ============================================================

-- Default admin user: password = Admin@1234
INSERT INTO `users` (`username`, `email`, `password_hash`, `role`, `full_name`, `phone`, `status`) VALUES
('admin', 'admin@srms.edu.ng', '$2y$12$6pBEVAnQF5s7L4Yv9qJVueTW/EkSoGiXcmJJRXQFUoAi0Gxl4aTeq', 'admin', 'System Administrator', '08000000000', 'active'),
('registrar1', 'registrar@srms.edu.ng', '$2y$12$6pBEVAnQF5s7L4Yv9qJVueTW/EkSoGiXcmJJRXQFUoAi0Gxl4aTeq', 'registrar', 'Mrs. Grace Okonkwo', '08011111111', 'active'),
('dr_eze', 'eze@srms.edu.ng', '$2y$12$6pBEVAnQF5s7L4Yv9qJVueTW/EkSoGiXcmJJRXQFUoAi0Gxl4aTeq', 'teacher', 'Dr. Chukwuemeka Eze', '08022222222', 'active'),
('mr_adeyemi', 'adeyemi@srms.edu.ng', '$2y$12$6pBEVAnQF5s7L4Yv9qJVueTW/EkSoGiXcmJJRXQFUoAi0Gxl4aTeq', 'teacher', 'Mr. Babatunde Adeyemi', '08033333333', 'active');

-- Departments
INSERT INTO `departments` (`name`, `code`, `faculty`, `head_of_dept`) VALUES
('Computer Science', 'CSC', 'Faculty of Science', 'Prof. Ngozi Adaeze'),
('Business Administration', 'BUS', 'Faculty of Management Sciences', 'Prof. Emeka Obi'),
('Electrical Engineering', 'EEE', 'Faculty of Engineering', 'Prof. Tunde Bakare');

-- Academic Sessions
INSERT INTO `academic_sessions` (`session_name`, `start_date`, `end_date`, `is_current`, `semester`) VALUES
('2022/2023', '2022-09-01', '2023-06-30', 0, 'first'),
('2023/2024', '2023-09-01', '2024-06-30', 0, 'first'),
('2024/2025', '2024-09-01', '2025-06-30', 1, 'first');

-- Sample Students
INSERT INTO `students` (`matric_number`, `first_name`, `last_name`, `middle_name`, `date_of_birth`, `gender`, `email`, `phone`, `address`, `state_of_origin`, `nationality`, `religion`, `department_id`, `level`, `admission_date`, `status`, `guardian_name`, `guardian_phone`, `guardian_email`, `guardian_relationship`, `guardian_address`) VALUES
('CSC/2021/001', 'Adaeze', 'Nwosu', 'Chioma', '2001-03-15', 'female', 'adaeze.nwosu@student.srms.edu.ng', '08100000001', '12 Lagos Street, Enugu', 'Enugu', 'Nigerian', 'Christianity', 1, '400', '2021-09-01', 'active', 'Mr. Nwosu Emmanuel', '08100000099', 'nwosu.e@gmail.com', 'Father', '12 Lagos Street, Enugu'),
('CSC/2022/002', 'Emeka', 'Okafor', 'Chidi', '2002-07-22', 'male', 'emeka.okafor@student.srms.edu.ng', '08100000002', '5 Aba Road, Port Harcourt', 'Rivers', 'Nigerian', 'Christianity', 1, '300', '2022-09-01', 'active', 'Mrs. Okafor Ngozi', '08100000098', 'okafor.n@gmail.com', 'Mother', '5 Aba Road, Port Harcourt'),
('BUS/2021/003', 'Fatima', 'Aliyu', NULL, '2001-11-08', 'female', 'fatima.aliyu@student.srms.edu.ng', '08100000003', '22 Sultan Road, Sokoto', 'Sokoto', 'Nigerian', 'Islam', 2, '400', '2021-09-01', 'active', 'Alhaji Aliyu Musa', '08100000097', 'aliyu.m@yahoo.com', 'Father', '22 Sultan Road, Sokoto'),
('EEE/2023/004', 'Tunde', 'Bakare', 'Segun', '2003-05-30', 'male', 'tunde.bakare@student.srms.edu.ng', '08100000004', '7 Awolowo Avenue, Ibadan', 'Oyo', 'Nigerian', 'Christianity', 3, '200', '2023-09-01', 'active', 'Mrs. Bakare Folake', '08100000096', 'bakare.f@gmail.com', 'Mother', '7 Awolowo Avenue, Ibadan'),
('BUS/2022/005', 'Zainab', 'Mohammed', 'Hauwa', '2002-01-19', 'female', 'zainab.mohammed@student.srms.edu.ng', '08100000005', '3 Ahmadu Bello Way, Kano', 'Kano', 'Nigerian', 'Islam', 2, '300', '2022-09-01', 'active', 'Mallam Mohammed Usman', '08100000095', 'moh.usman@yahoo.com', 'Father', '3 Ahmadu Bello Way, Kano');

-- Courses
INSERT INTO `courses` (`course_code`, `course_title`, `credit_units`, `department_id`, `level`, `semester`, `description`, `status`) VALUES
('CSC301', 'Data Structures and Algorithms', 3, 1, '300', 'first', 'Study of fundamental data structures and algorithm design', 'active'),
('CSC401', 'Artificial Intelligence', 3, 1, '400', 'first', 'Introduction to AI concepts, machine learning and neural networks', 'active'),
('CSC402', 'Software Engineering', 2, 1, '400', 'first', 'Principles and practices of software engineering', 'active'),
('BUS301', 'Business Statistics', 3, 2, '300', 'first', 'Statistical methods for business decision making', 'active'),
('BUS401', 'Strategic Management', 3, 2, '400', 'first', 'Strategic planning and management principles', 'active'),
('EEE201', 'Circuit Theory', 3, 3, '200', 'first', 'Fundamentals of electrical circuit analysis', 'active');

-- Course Assignments (teacher to course for current session)
INSERT INTO `course_assignments` (`course_id`, `teacher_user_id`, `session_id`) VALUES
(1, 3, 3), (2, 3, 3), (3, 3, 3),
(4, 4, 3), (5, 4, 3), (6, 4, 3);

-- Student Enrollments (current session 3 = 2024/2025)
INSERT INTO `student_courses` (`student_id`, `course_id`, `session_id`) VALUES
(1, 2, 3), (1, 3, 3),
(2, 1, 3),
(3, 4, 3),
(4, 6, 3),
(5, 4, 3);

-- Previous session enrollments (session 2 = 2023/2024)
INSERT INTO `student_courses` (`student_id`, `course_id`, `session_id`) VALUES
(1, 1, 2),
(2, 1, 2),
(3, 4, 2),
(5, 4, 2);

-- Sample Grades (session 3)
INSERT INTO `grades` (`student_id`, `course_id`, `session_id`, `ca_score`, `exam_score`, `letter_grade`, `grade_points`, `credit_units`, `entered_by`) VALUES
(1, 2, 3, 28.00, 47.00, 'B', 3.0, 3, 3),
(1, 3, 3, 25.00, 50.00, 'A', 4.0, 2, 3),
(2, 1, 3, 22.00, 38.00, 'C', 2.0, 3, 3),
(3, 4, 3, 27.00, 48.00, 'B', 3.0, 3, 4),
(4, 6, 3, 20.00, 35.00, 'D', 1.0, 3, 4),
(5, 4, 3, 29.00, 50.00, 'A', 4.0, 3, 4);

-- Grades for previous session
INSERT INTO `grades` (`student_id`, `course_id`, `session_id`, `ca_score`, `exam_score`, `letter_grade`, `grade_points`, `credit_units`, `entered_by`) VALUES
(1, 1, 2, 26.00, 49.00, 'B', 3.0, 3, 3),
(2, 1, 2, 20.00, 32.00, 'D', 1.0, 3, 3),
(3, 4, 2, 25.00, 45.00, 'B', 3.0, 3, 4),
(5, 4, 2, 28.00, 50.00, 'A', 4.0, 3, 4);

-- Sample Attendance
INSERT INTO `attendance` (`student_id`, `course_id`, `session_id`, `date`, `status`, `marked_by`) VALUES
(1, 2, 3, '2024-09-10', 'present', 3),
(1, 2, 3, '2024-09-17', 'present', 3),
(1, 2, 3, '2024-09-24', 'absent', 3),
(1, 2, 3, '2024-10-01', 'present', 3),
(1, 3, 3, '2024-09-11', 'present', 3),
(1, 3, 3, '2024-09-18', 'late', 3),
(1, 3, 3, '2024-09-25', 'present', 3),
(2, 1, 3, '2024-09-10', 'present', 3),
(2, 1, 3, '2024-09-17', 'absent', 3),
(2, 1, 3, '2024-09-24', 'present', 3),
(3, 4, 3, '2024-09-11', 'present', 4),
(3, 4, 3, '2024-09-18', 'present', 4),
(4, 6, 3, '2024-09-10', 'present', 4),
(4, 6, 3, '2024-09-17', 'absent', 4),
(5, 4, 3, '2024-09-11', 'present', 4),
(5, 4, 3, '2024-09-18', 'present', 4);

-- Fee Structures
INSERT INTO `fee_structures` (`session_id`, `department_id`, `level`, `fee_type`, `amount`, `due_date`) VALUES
(3, NULL, 'all', 'School Fees', 150000.00, '2024-10-31'),
(3, NULL, 'all', 'Development Levy', 25000.00, '2024-10-31'),
(3, 1, 'all', 'Laboratory Fees', 15000.00, '2024-10-31'),
(3, 3, 'all', 'Laboratory Fees', 20000.00, '2024-10-31');

-- Sample Fee Payments
INSERT INTO `fee_payments` (`student_id`, `session_id`, `fee_structure_id`, `amount_paid`, `payment_date`, `payment_method`, `receipt_number`, `remarks`, `received_by`) VALUES
(1, 3, 1, 150000.00, '2024-09-05', 'bank_transfer', 'RCP-20240905-001', 'Full payment', 2),
(1, 3, 2, 25000.00, '2024-09-05', 'bank_transfer', 'RCP-20240905-002', 'Full payment', 2),
(2, 3, 1, 100000.00, '2024-09-10', 'cash', 'RCP-20240910-001', 'Partial payment', 2),
(3, 3, 1, 150000.00, '2024-09-06', 'online', 'RCP-20240906-001', 'Full payment', 2),
(3, 3, 2, 25000.00, '2024-09-06', 'online', 'RCP-20240906-002', 'Full payment', 2);

-- System Settings
INSERT INTO `system_settings` (`setting_key`, `setting_value`) VALUES
('site_name', 'Student Record Management System'),
('site_short_name', 'SRMS'),
('institution_name', 'Federal University of Technology'),
('institution_address', 'Minna, Niger State, Nigeria'),
('current_session_id', '3'),
('admin_email', 'admin@srms.edu.ng'),
('logo_path', 'assets/img/logo.png'),
('max_ca_score', '30'),
('max_exam_score', '70');

-- Audit Logs
INSERT INTO `audit_logs` (`user_id`, `action`, `module`, `description`, `ip_address`) VALUES
(1, 'LOGIN', 'auth', 'Admin logged in successfully', '127.0.0.1'),
(2, 'ADD_PAYMENT', 'fees', 'Recorded fee payment for CSC/2021/001', '127.0.0.1'),
(3, 'GRADE_ENTRY', 'grades', 'Entered grades for CSC401 - 2024/2025 session', '127.0.0.1');
