# 🗄️ EduMove - Database Documentation

## Overview

The EduMove database manages schools, teachers, classes, students, motor assessments, motor test definitions, and assessment results.

The database was designed to preserve assessment history, support multiple attempts for each motor test, and allow new tests and protocols to be added without changing the table structure.

Its main design goals are:

* Data integrity
* Historical preservation
* Separation between registration and assessment data
* Flexible motor test registration
* Support for future reports and performance analysis

---

# Database Management System

* **DBMS:** MySQL
* **Storage engine:** InnoDB
* **Language:** SQL
* **ORM:** SQLAlchemy 2.0
* **Naming convention:** English, plural table names, and `snake_case`

---

# Database Structure

## Schools

Stores educational institutions registered in the system.

| Field | Type | Description |
| --- | --- | --- |
| `school_id` | INT | Primary key |
| `name` | VARCHAR(150) | School name |
| `cnpj` | CHAR(14) | Optional unique CNPJ |
| `email` | VARCHAR(100) | School email |
| `phone` | VARCHAR(20) | School phone number |
| `city` | VARCHAR(100) | City |
| `state` | CHAR(2) | Brazilian state code |
| `is_active` | BOOLEAN | Active record indicator |
| `created_at` | TIMESTAMP | Registration date |
| `updated_at` | TIMESTAMP | Last update date |

---

## Teachers

Stores teachers and their school access profile.

| Field | Type | Description |
| --- | --- | --- |
| `teacher_id` | INT | Primary key |
| `school_id` | INT | Foreign key → `schools.school_id` |
| `name` | VARCHAR(100) | Teacher's full name |
| `email` | VARCHAR(100) | Unique login email |
| `password_hash` | VARCHAR(255) | Password hash |
| `role` | ENUM | `Administrador`, `Professor`, or `Coordenador` |
| `is_active` | BOOLEAN | Active record indicator |
| `created_at` | TIMESTAMP | Registration date |
| `updated_at` | TIMESTAMP | Last update date |

Every teacher must belong to a school. Deactivating a teacher must not remove previously registered assessments.

---

## Classes

Stores school classes and their responsible teacher.

| Field | Type | Description |
| --- | --- | --- |
| `class_id` | INT | Primary key |
| `school_id` | INT | Foreign key → `schools.school_id` |
| `teacher_id` | INT | Optional foreign key → `teachers.teacher_id` |
| `grade_number` | TINYINT | Grade number |
| `education_level` | ENUM | Education level |
| `section` | CHAR(1) | Class section, such as `A` or `B` |
| `academic_year` | YEAR | Academic year |
| `shift` | ENUM | `Manhã`, `Tarde`, `Integral`, or `Noite` |
| `is_active` | BOOLEAN | Active class indicator |
| `created_at` | TIMESTAMP | Registration date |
| `updated_at` | TIMESTAMP | Last update date |

A class is unique by school, grade number, section, and academic year. A class may temporarily exist without a responsible teacher.

---

## Students

Stores student identification and current class information.

| Field | Type | Description |
| --- | --- | --- |
| `student_id` | INT | Primary key |
| `class_id` | INT | Foreign key → `classes.class_id` |
| `registration_number` | VARCHAR(20) | Optional unique registration number |
| `name` | VARCHAR(100) | Student's full name |
| `birth_date` | DATE | Date of birth |
| `sex` | ENUM | `Masculino` or `Feminino` |
| `is_active` | BOOLEAN | Active student indicator |
| `created_at` | TIMESTAMP | Registration date |
| `updated_at` | TIMESTAMP | Last update date |

The student table stores only registration information. Measurements and motor results are stored in assessment-related tables to preserve historical data.

---

## Assessments

Stores each assessment event performed with a student.

| Field | Type | Description |
| --- | --- | --- |
| `assessment_id` | INT | Primary key |
| `student_id` | INT | Foreign key → `students.student_id` |
| `teacher_id` | INT | Foreign key → `teachers.teacher_id` |
| `class_id` | INT | Foreign key → `classes.class_id` |
| `assessment_date` | DATE | Assessment date |
| `weight_kg` | DECIMAL(5,2) | Optional weight in kilograms |
| `height_cm` | DECIMAL(5,2) | Optional height in centimeters |
| `notes` | TEXT | Teacher observations |
| `is_active` | BOOLEAN | Active assessment indicator |
| `created_at` | TIMESTAMP | Registration date |
| `updated_at` | TIMESTAMP | Last update date |

The `teacher_id` and `class_id` fields preserve who performed the assessment and the student's class at that time. Therefore, historical context remains available even if the student later changes classes.

Weight and height are optional because an assessment may contain only motor tests.

---

## Motor Tests

Stores the catalog of motor tests available in EduMove.

| Field | Type | Description |
| --- | --- | --- |
| `motor_test_id` | INT | Primary key |
| `code` | VARCHAR(50) | Unique internal test code |
| `name` | VARCHAR(150) | Test name |
| `unit` | VARCHAR(30) | Measurement unit, such as `cm`, `s`, or `acertos` |
| `result_direction` | ENUM | `higher`, `lower`, or `neutral` |
| `result_type` | ENUM | `measurement` or `binary` |
| `aggregation_method` | ENUM | `maximum`, `minimum`, `sum`, or `average` |
| `default_attempts` | TINYINT UNSIGNED | Default attempt count |
| `min_attempts` | TINYINT UNSIGNED | Minimum allowed attempt count |
| `max_attempts` | TINYINT UNSIGNED | Maximum allowed attempt count |
| `protocol_name` | VARCHAR(100) | Optional protocol name |
| `protocol_version` | VARCHAR(50) | Optional protocol version |
| `protocol_source` | VARCHAR(255) | Optional protocol source |
| `protocol_description` | TEXT | Optional application instructions |
| `is_active` | BOOLEAN | Active test indicator |
| `created_at` | TIMESTAMP | Registration date |
| `updated_at` | TIMESTAMP | Last update date |

The `result_direction` field defines how a result is interpreted:

* `higher`: a higher value represents better performance;
* `lower`: a lower value represents better performance;
* `neutral`: the value has no direct performance direction.

Motor tests are registered as rows instead of fixed columns. This allows new tests and protocols to be added without altering the database structure.

`result_type` distinguishes continuous measurements from binary success/failure
trials. `aggregation_method` defines how multiple attempts produce the displayed
result. Attempt limits support both fixed protocols and configurable tests such as
ball reception.

---

## Assessment Results

Stores individual attempts and results for each motor test performed during an assessment.

| Field | Type | Description |
| --- | --- | --- |
| `assessment_result_id` | INT | Primary key |
| `assessment_id` | INT | Foreign key → `assessments.assessment_id` |
| `motor_test_id` | INT | Foreign key → `motor_tests.motor_test_id` |
| `attempt_number` | TINYINT UNSIGNED | Attempt number, starting at 1 |
| `result_value` | DECIMAL(10,2) | Numeric result |
| `notes` | VARCHAR(255) | Optional result observations |
| `is_active` | BOOLEAN | Active result indicator |
| `created_at` | TIMESTAMP | Registration date |
| `updated_at` | TIMESTAMP | Last update date |

The combination of assessment, motor test, and attempt number must be unique. This prevents the same attempt from being registered twice while allowing multiple attempts for the same test.

The service layer saves a complete attempt set for each test. Corrections reuse the
same attempt numbers, reactivate previously retained rows when needed, and logically
deactivate attempts beyond the newly selected total. Aggregated values are calculated
from active attempts and are not stored in an additional column.

---

## Postural Observation Options

Stores the configurable educational posture catalog used by the assessment form.

| Field | Type | Description |
| --- | --- | --- |
| `postural_option_id` | INT | Primary key |
| `code` | VARCHAR(80) | Unique internal option code |
| `region` | ENUM | `shoulders`, `spine`, `knees`, or `feet` |
| `view_position` | ENUM | `frontal`, `lateral`, or `reference` |
| `label` | VARCHAR(120) | Pedagogical display label |
| `description` | VARCHAR(255) | Optional explanatory text |
| `reference_image_path` | VARCHAR(255) | Optional application-asset path |
| `sort_order` | TINYINT UNSIGNED | Display order within the group |
| `is_active` | BOOLEAN | Active catalog option indicator |
| `created_at` | TIMESTAMP | Registration date |
| `updated_at` | TIMESTAMP | Last update date |

The initial seed contains 20 options across shoulders, spine, knees, and feet. The
wording records visible appearances for educational screening and does not represent
a clinical diagnosis.

---

## Assessment Postural Observations

Stores each postural choice and its optional note within an assessment.

| Field | Type | Description |
| --- | --- | --- |
| `postural_observation_id` | INT | Primary key |
| `assessment_id` | INT | Foreign key → `assessments.assessment_id` |
| `postural_option_id` | INT | Foreign key → `postural_observation_options.postural_option_id` |
| `notes` | VARCHAR(255) | Optional teacher observation |
| `is_active` | BOOLEAN | Current or historical selection indicator |
| `created_at` | TIMESTAMP | Registration date |
| `updated_at` | TIMESTAMP | Last update date |

The assessment and option pair is unique. The service additionally keeps only one
active choice per region and viewing position, logically deactivating a replaced
choice so its history remains available.

---

# Entity Relationship Diagram

```mermaid
erDiagram
    SCHOOLS ||--o{ TEACHERS : has
    SCHOOLS ||--o{ CLASSES : has
    TEACHERS o|--o{ CLASSES : manages
    CLASSES ||--o{ STUDENTS : contains
    STUDENTS ||--o{ ASSESSMENTS : receives
    TEACHERS ||--o{ ASSESSMENTS : performs
    CLASSES ||--o{ ASSESSMENTS : contextualizes
    ASSESSMENTS ||--o{ ASSESSMENT_RESULTS : contains
    MOTOR_TESTS ||--o{ ASSESSMENT_RESULTS : measures
    ASSESSMENTS ||--o{ ASSESSMENT_POSTURAL_OBSERVATIONS : contains
    POSTURAL_OBSERVATION_OPTIONS ||--o{ ASSESSMENT_POSTURAL_OBSERVATIONS : classifies
```

The `assessment_results` table creates a flexible many-to-many relationship between assessments and motor tests. Multiple rows may exist for the same assessment and test when the protocol allows more than one attempt.

---

# Data Integrity Rules

The current schema includes the following protections:

* Unique teacher email
* Unique optional school CNPJ
* Unique motor test code
* Unique class by school, grade, section, and academic year
* Unique assessment result by assessment, motor test, and attempt number
* Unique postural option by internal code
* Unique postural selection by assessment and option
* Foreign keys between all dependent entities
* Positive values for weight, height, result value, and attempt number
* Valid motor-test attempt ranges
* Record deactivation through `is_active` instead of permanent deletion
* Automatic `created_at` and `updated_at` timestamps

The service layer must also validate that teachers, classes, students, and assessments belong to the same school. A database-level composite constraint may be added in a future migration.

---

# Initial Motor Tests

The initial seed registers the following motor tests:

| Code | Test | Type | Attempts | Aggregation | Active |
| --- | --- | --- | --- | --- | --- |
| `ADAPTED_SIT_AND_REACH` | Adapted sit-and-reach | measurement | 2 | maximum | Yes |
| `HORIZONTAL_JUMP` | Horizontal jump | measurement | 2 | maximum | Yes |
| `SINGLE_LEG_BALANCE` | Single-leg balance | measurement | 2 | maximum | Yes |
| `BALL_RECEPTION` | Ball reception | binary | 3-10 | sum | Yes |
| `THROWING_ACCURACY` | Throwing accuracy | measurement | 2 | maximum | No |
| `AGILITY` | Agility | measurement | 2 | minimum | No |

The flexibility reference source remains pending. Tests without a selected protocol
are retained as inactive records.

---

# Migration Status

| Migration | Description | Status |
| --- | --- | --- |
| `001_create_schools.sql` | Creates schools | Completed |
| `002_create_teachers.sql` | Creates teachers | Completed |
| `003_create_classes.sql` | Creates classes | Completed |
| `004_create_students.sql` | Creates students | Completed |
| `005_create_assessments.sql` | Creates assessments | Completed |
| `006_create_motor_tests.sql` | Creates the motor test catalog | Completed |
| `007_create_assessment_results.sql` | Creates attempts and results | Completed |
| `008_convert_tables_to_innodb.sql` | Converts tables and restores nine foreign keys | Completed |
| `009_add_motor_test_protocol_metadata.sql` | Adds result, aggregation, and attempt metadata | Completed |
| `010_add_school_active_status.sql` | Adds logical deactivation for schools | Completed |
| `011_create_postural_observations.sql` | Adds the posture catalog and assessment selections | Completed |

The migration files preserve the incremental database history. The consolidated `schema.sql` can initialize a new EduMove database and has been successfully validated in a temporary MySQL database.

---

# Database Testing

The database integration flow validates:

```text
School → Teacher → Class → Student → Assessment → Result / Postural Observation
```

Transactional checks use `ROLLBACK`, allowing relationships and constraints to be
validated without keeping fictitious data. The automated project suite currently
contains 322 passing tests, every ORM model has been compared with the live MySQL
schema, and the class, student, assessment, motor-result, and postural-observation
workflows have been validated transactionally against MySQL.

---

# Next Steps

The next database tasks are:

* Implement an automated migration runner with safe SQL parsing and migration history;
* Confirm the scientific source for adapted flexibility reference ranges;
* Evaluate a class enrollment history table for future versions.
