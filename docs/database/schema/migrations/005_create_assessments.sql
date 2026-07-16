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
);