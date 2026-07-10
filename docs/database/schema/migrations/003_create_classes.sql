

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
);