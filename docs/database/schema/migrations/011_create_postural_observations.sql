-- =====================================================
-- Migration 011 - Create educational postural observations
--
-- Adds a configurable option catalog and preserves every
-- postural choice made within a student assessment.
-- =====================================================

CREATE TABLE postural_observation_options (
    postural_option_id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(80) NOT NULL UNIQUE,
    region ENUM(
        'shoulders',
        'spine',
        'knees',
        'feet'
    ) NOT NULL,
    view_position ENUM(
        'frontal',
        'lateral',
        'reference'
    ) NOT NULL,
    label VARCHAR(120) NOT NULL,
    description VARCHAR(255),
    reference_image_path VARCHAR(255),
    sort_order TINYINT UNSIGNED NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT chk_postural_option_sort_order
        CHECK (sort_order > 0)
) ENGINE=InnoDB;

CREATE TABLE assessment_postural_observations (
    postural_observation_id INT AUTO_INCREMENT PRIMARY KEY,
    assessment_id INT NOT NULL,
    postural_option_id INT NOT NULL,
    notes VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_postural_observation_assessment
        FOREIGN KEY (assessment_id)
        REFERENCES assessments(assessment_id),

    CONSTRAINT fk_postural_observation_option
        FOREIGN KEY (postural_option_id)
        REFERENCES postural_observation_options(postural_option_id),

    CONSTRAINT uq_assessment_postural_option UNIQUE (
        assessment_id,
        postural_option_id
    )
) ENGINE=InnoDB;
