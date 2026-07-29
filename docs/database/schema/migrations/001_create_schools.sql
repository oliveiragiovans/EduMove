
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
