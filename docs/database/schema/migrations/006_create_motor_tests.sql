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

    protocol_name VARCHAR(100),

    protocol_description TEXT,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);