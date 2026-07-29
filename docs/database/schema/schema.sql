-- =====================================================
-- EduMove - Complete Database Schema
-- DBMS: MySQL
--
-- Use this file to initialize a new EduMove database.
-- Existing databases should be updated through migrations.
-- =====================================================

CREATE DATABASE IF NOT EXISTS edumove
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE edumove;

-- ==========================================
-- Table: schools
-- Description: Stores registered schools.
-- ==========================================

CREATE TABLE schools (
    school_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    cnpj CHAR(14) UNIQUE,
    email VARCHAR(100),
    phone VARCHAR(20),
    city VARCHAR(100) NOT NULL,
    state CHAR(2) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ==========================================
-- Table: teachers
-- Description: Stores registered teachers.
-- ==========================================

CREATE TABLE teachers (
    teacher_id INT AUTO_INCREMENT PRIMARY KEY,
    school_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM(
        'Administrador',
        'Professor',
        'Coordenador'
    ) NOT NULL DEFAULT 'Professor',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_teacher_school
        FOREIGN KEY (school_id)
        REFERENCES schools(school_id)
) ENGINE=InnoDB;

-- ==========================================
-- Table: classes
-- Description: Stores school classes.
-- ==========================================

CREATE TABLE classes (
    class_id INT AUTO_INCREMENT PRIMARY KEY,
    school_id INT NOT NULL,
    teacher_id INT,
    grade_number TINYINT NOT NULL,
    education_level ENUM(
        'Educação Infantil',
        'Ensino Fundamental I',
        'Ensino Fundamental II',
        'Ensino Médio'
    ) NOT NULL,
    section CHAR(1) NOT NULL,
    academic_year YEAR NOT NULL,
    shift ENUM(
        'Manhã',
        'Tarde',
        'Integral',
        'Noite'
    ) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_class_school
        FOREIGN KEY (school_id)
        REFERENCES schools(school_id),

    CONSTRAINT fk_class_teacher
        FOREIGN KEY (teacher_id)
        REFERENCES teachers(teacher_id),

    CONSTRAINT uq_class UNIQUE (
        school_id,
        grade_number,
        section,
        academic_year
    )
) ENGINE=InnoDB;

-- ==========================================
-- Table: students
-- Description: Stores registered students.
-- ==========================================

CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    class_id INT NOT NULL,
    registration_number VARCHAR(20) UNIQUE,
    name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    sex ENUM(
        'Masculino',
        'Feminino'
    ) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_student_class
        FOREIGN KEY (class_id)
        REFERENCES classes(class_id)
) ENGINE=InnoDB;

-- ==========================================
-- Table: assessments
-- Description: Stores student assessments.
-- ==========================================

CREATE TABLE assessments (
    assessment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    teacher_id INT NOT NULL,
    class_id INT NOT NULL,
    assessment_date DATE NOT NULL,
    weight_kg DECIMAL(5,2),
    height_cm DECIMAL(5,2),
    notes TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_assessment_student
        FOREIGN KEY (student_id)
        REFERENCES students(student_id),

    CONSTRAINT fk_assessment_teacher
        FOREIGN KEY (teacher_id)
        REFERENCES teachers(teacher_id),

    CONSTRAINT fk_assessment_class
        FOREIGN KEY (class_id)
        REFERENCES classes(class_id),

    CONSTRAINT chk_assessment_weight
        CHECK (weight_kg IS NULL OR weight_kg > 0),

    CONSTRAINT chk_assessment_height
        CHECK (height_cm IS NULL OR height_cm > 0)
) ENGINE=InnoDB;

-- ==========================================
-- Table: motor_tests
-- Description: Stores available motor tests.
-- ==========================================

CREATE TABLE motor_tests (
    motor_test_id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    unit VARCHAR(30) NOT NULL,
    result_direction ENUM(
        'higher',
        'lower',
        'neutral'
    ) NOT NULL DEFAULT 'higher',

    result_type ENUM(
        'measurement',
        'binary'
    ) NOT NULL DEFAULT 'measurement',

    aggregation_method ENUM(
        'maximum',
        'minimum',
        'sum',
        'average'
    ) NOT NULL DEFAULT 'maximum',

    default_attempts TINYINT UNSIGNED NOT NULL DEFAULT 2,
    min_attempts TINYINT UNSIGNED NOT NULL DEFAULT 2,
    max_attempts TINYINT UNSIGNED NOT NULL DEFAULT 2,

    protocol_name VARCHAR(100),
    protocol_version VARCHAR(50),
    protocol_source VARCHAR(255),
    protocol_description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT chk_motor_test_attempts
        CHECK (
            min_attempts > 0
            AND max_attempts >= min_attempts
            AND default_attempts BETWEEN min_attempts AND max_attempts
        )
) ENGINE=InnoDB;

-- ==========================================
-- Table: assessment_results
-- Description: Stores motor test attempts and results.
-- ==========================================

CREATE TABLE assessment_results (
    assessment_result_id INT AUTO_INCREMENT PRIMARY KEY,
    assessment_id INT NOT NULL,
    motor_test_id INT NOT NULL,
    attempt_number TINYINT UNSIGNED NOT NULL DEFAULT 1,
    result_value DECIMAL(10,2) NOT NULL,
    notes VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_result_assessment
        FOREIGN KEY (assessment_id)
        REFERENCES assessments(assessment_id),

    CONSTRAINT fk_result_motor_test
        FOREIGN KEY (motor_test_id)
        REFERENCES motor_tests(motor_test_id),

    CONSTRAINT uq_assessment_test_attempt UNIQUE (
        assessment_id,
        motor_test_id,
        attempt_number
    ),

    CONSTRAINT chk_result_value
        CHECK (result_value >= 0),

    CONSTRAINT chk_attempt_number
        CHECK (attempt_number > 0)
) ENGINE=InnoDB;
