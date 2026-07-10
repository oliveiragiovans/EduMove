
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
);