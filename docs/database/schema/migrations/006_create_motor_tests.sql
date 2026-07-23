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
