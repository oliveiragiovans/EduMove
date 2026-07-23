-- =====================================================
-- Migration 008 - Convert tables to InnoDB
--
-- MyISAM ignores FOREIGN KEY constraints. This migration
-- converts the existing tables to InnoDB and restores all
-- relationships declared in the consolidated schema.
--
-- Validate that there are no orphan records before running
-- this migration. MySQL DDL statements commit automatically.
-- =====================================================

ALTER TABLE schools ENGINE=InnoDB;
ALTER TABLE teachers ENGINE=InnoDB;
ALTER TABLE classes ENGINE=InnoDB;
ALTER TABLE students ENGINE=InnoDB;
ALTER TABLE assessments ENGINE=InnoDB;
ALTER TABLE motor_tests ENGINE=InnoDB;
ALTER TABLE assessment_results ENGINE=InnoDB;

ALTER TABLE teachers
    ADD CONSTRAINT fk_teacher_school
        FOREIGN KEY (school_id)
        REFERENCES schools(school_id);

ALTER TABLE classes
    ADD CONSTRAINT fk_class_school
        FOREIGN KEY (school_id)
        REFERENCES schools(school_id),
    ADD CONSTRAINT fk_class_teacher
        FOREIGN KEY (teacher_id)
        REFERENCES teachers(teacher_id);

ALTER TABLE students
    ADD CONSTRAINT fk_student_class
        FOREIGN KEY (class_id)
        REFERENCES classes(class_id);

ALTER TABLE assessments
    ADD CONSTRAINT fk_assessment_student
        FOREIGN KEY (student_id)
        REFERENCES students(student_id),
    ADD CONSTRAINT fk_assessment_teacher
        FOREIGN KEY (teacher_id)
        REFERENCES teachers(teacher_id),
    ADD CONSTRAINT fk_assessment_class
        FOREIGN KEY (class_id)
        REFERENCES classes(class_id);

ALTER TABLE assessment_results
    ADD CONSTRAINT fk_result_assessment
        FOREIGN KEY (assessment_id)
        REFERENCES assessments(assessment_id),
    ADD CONSTRAINT fk_result_motor_test
        FOREIGN KEY (motor_test_id)
        REFERENCES motor_tests(motor_test_id);
