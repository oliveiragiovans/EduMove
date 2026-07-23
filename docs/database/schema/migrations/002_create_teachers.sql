
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
