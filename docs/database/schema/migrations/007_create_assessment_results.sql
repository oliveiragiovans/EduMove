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
