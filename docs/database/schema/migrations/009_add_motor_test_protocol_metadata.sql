-- =====================================================
-- Migration 009 - Add motor-test protocol metadata
--
-- Adds the information required to configure how attempts
-- are recorded and how their results are aggregated.
-- =====================================================

ALTER TABLE motor_tests
    ADD COLUMN result_type ENUM(
        'measurement',
        'binary'
    ) NOT NULL DEFAULT 'measurement'
        AFTER result_direction,

    ADD COLUMN aggregation_method ENUM(
        'maximum',
        'minimum',
        'sum',
        'average'
    ) NOT NULL DEFAULT 'maximum'
        AFTER result_type,

    ADD COLUMN default_attempts TINYINT UNSIGNED NOT NULL DEFAULT 2
        AFTER aggregation_method,

    ADD COLUMN min_attempts TINYINT UNSIGNED NOT NULL DEFAULT 2
        AFTER default_attempts,

    ADD COLUMN max_attempts TINYINT UNSIGNED NOT NULL DEFAULT 2
        AFTER min_attempts,

    ADD COLUMN protocol_version VARCHAR(50)
        AFTER protocol_name,

    ADD COLUMN protocol_source VARCHAR(255)
        AFTER protocol_version,

    ADD CONSTRAINT chk_motor_test_attempts
        CHECK (
            min_attempts > 0
            AND max_attempts >= min_attempts
            AND default_attempts BETWEEN min_attempts AND max_attempts
        );
