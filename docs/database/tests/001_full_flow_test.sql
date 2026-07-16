USE edumove;

START TRANSACTION;

-- 1. Create test school
INSERT INTO schools (
    name,
    email,
    city,
    state
)
VALUES (
    'Escola Teste EduMove',
    'school.test@edumove.local',
    'Londrina',
    'PR'
);

SET @school_id = LAST_INSERT_ID();

-- 2. Create test teacher
INSERT INTO teachers (
    school_id,
    name,
    email,
    password_hash,
    role
)
VALUES (
    @school_id,
    'Professora Teste',
    'teacher.test@edumove.local',
    'test_password_hash',
    'Professor'
);

SET @teacher_id = LAST_INSERT_ID();

-- 3. Create test class
INSERT INTO classes (
    school_id,
    teacher_id,
    grade_number,
    education_level,
    section,
    academic_year,
    shift
)
VALUES (
    @school_id,
    @teacher_id,
    1,
    'Ensino Fundamental I',
    'A',
    YEAR(CURDATE()),
    'Tarde'
);

SET @class_id = LAST_INSERT_ID();

-- 4. Create test student
INSERT INTO students (
    class_id,
    registration_number,
    name,
    birth_date,
    sex
)
VALUES (
    @class_id,
    'TEST-0001',
    'Aluna Teste',
    '2019-03-15',
    'Feminino'
);

SET @student_id = LAST_INSERT_ID();

-- 5. Create assessment
INSERT INTO assessments (
    student_id,
    teacher_id,
    class_id,
    assessment_date,
    weight_kg,
    height_cm,
    notes
)
VALUES (
    @student_id,
    @teacher_id,
    @class_id,
    CURDATE(),
    25.30,
    125.50,
    'Avaliação criada para teste de integração.'
);

SET @assessment_id = LAST_INSERT_ID();

-- 6. Find motor tests
SET @jump_test_id = (
    SELECT motor_test_id
    FROM motor_tests
    WHERE code = 'HORIZONTAL_JUMP'
);

SET @balance_test_id = (
    SELECT motor_test_id
    FROM motor_tests
    WHERE code = 'SINGLE_LEG_BALANCE'
);

-- 7. Register results
INSERT INTO assessment_results (
    assessment_id,
    motor_test_id,
    attempt_number,
    result_value
)
VALUES
    (
        @assessment_id,
        @jump_test_id,
        1,
        112.00
    ),
    (
        @assessment_id,
        @jump_test_id,
        2,
        118.00
    ),
    (
        @assessment_id,
        @balance_test_id,
        1,
        15.00
    );

-- 8. Display complete result
SELECT
    sc.name AS school,
    t.name AS teacher,
    CONCAT(c.grade_number, 'º ano ', c.section) AS class,
    s.name AS student,
    a.assessment_date,
    mt.name AS motor_test,
    ar.attempt_number,
    ar.result_value,
    mt.unit
FROM assessment_results ar
INNER JOIN assessments a
    ON a.assessment_id = ar.assessment_id
INNER JOIN motor_tests mt
    ON mt.motor_test_id = ar.motor_test_id
INNER JOIN students s
    ON s.student_id = a.student_id
INNER JOIN classes c
    ON c.class_id = a.class_id
INNER JOIN teachers t
    ON t.teacher_id = a.teacher_id
INNER JOIN schools sc
    ON sc.school_id = c.school_id
WHERE a.assessment_id = @assessment_id
ORDER BY mt.name, ar.attempt_number;

-- Remove all test data
ROLLBACK;