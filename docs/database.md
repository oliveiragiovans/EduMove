# 🗄️ EduMove - Database Documentation

## Overview

The EduMove database was designed to manage information related to schools, teachers, classes, students, and motor assessments.

The main objective is to provide a structured database capable of storing student development data, supporting physical education assessments, generating reports, and enabling future analysis of motor development progress.

The database was designed considering scalability, data integrity, and future expansion of the platform.

---

# Database Management System

* **DBMS:** MySQL
* **Language:** SQL
* **ORM:** SQLAlchemy (planned)

---

# Database Structure

## School

Stores information about educational institutions registered in the system.

| Field      | Type         | Description       |
| ---------- | ------------ | ----------------- |
| id         | INT          | Primary Key       |
| name       | VARCHAR(100) | School name       |
| created_at | TIMESTAMP    | Registration date |

---

## Teacher

Stores information about teachers responsible for managing classes and assessments.

| Field     | Type         | Description          |
| --------- | ------------ | -------------------- |
| id        | INT          | Primary Key          |
| name      | VARCHAR(100) | Teacher's full name  |
| email     | VARCHAR(100) | Unique email         |
| password  | VARCHAR(255) | Encrypted password   |
| school_id | INT          | Foreign Key → School |

---

## Class

Stores school classes and their relationship with teachers.

| Field       | Type        | Description           |
| ----------- | ----------- | --------------------- |
| id          | INT         | Primary Key           |
| name        | VARCHAR(50) | Class name            |
| school_year | VARCHAR(20) | Academic year         |
| teacher_id  | INT         | Foreign Key → Teacher |

---

## Student

Stores student registration information.

The student table contains only identification and classification data. Anthropometric information and assessment results are stored separately to maintain historical records.

| Field      | Type         | Description         |
| ---------- | ------------ | ------------------- |
| id         | INT          | Primary Key         |
| name       | VARCHAR(100) | Student's full name |
| birth_date | DATE         | Date of birth       |
| gender     | VARCHAR(20)  | Gender information  |
| class_id   | INT          | Foreign Key → Class |

---

## Assessment

Stores each physical education assessment performed with students.

Each assessment represents a specific evaluation moment, allowing the system to track student development over time.

| Field           | Type         | Description             |
| --------------- | ------------ | ----------------------- |
| id              | INT          | Primary Key             |
| student_id      | INT          | Foreign Key → Student   |
| assessment_date | DATE         | Date of assessment      |
| weight          | DECIMAL(5,2) | Weight measurement (kg) |
| height          | DECIMAL(4,2) | Height measurement (m)  |
| notes           | TEXT         | Teacher observations    |

---

## Motor Test

Stores results from motor skill tests performed during an assessment.

| Field              | Type         | Description              |
| ------------------ | ------------ | ------------------------ |
| id                 | INT          | Primary Key              |
| assessment_id      | INT          | Foreign Key → Assessment |
| horizontal_jump    | DECIMAL(5,2) | Horizontal jump distance |
| single_leg_balance | INT          | Balance time (seconds)   |
| ball_reception     | INT          | Successful receptions    |
| throwing_accuracy  | INT          | Successful throws        |
| agility            | DECIMAL(5,2) | Agility test result      |

---

# Entity Relationships

```
School (1) ───────── (N) Teacher

Teacher (1) ──────── (N) Class

Class (1) ────────── (N) Student

Student (1) ──────── (N) Assessment

Assessment (1) ───── (1) Motor Test
```

---

# Database Design Decisions

## Student Data Separation

Student registration data and assessment data are intentionally separated.

Information such as height and weight changes over time, therefore it belongs to the assessment record instead of the student profile.

This approach allows historical analysis of student development.

## Gender Information

The student's gender is stored because several motor assessment protocols use gender-specific reference values for analysis and comparison.

## Assessment History

The database allows multiple assessments for the same student, supporting longitudinal monitoring of motor development.

---

# Future Tables

The following tables may be added in future versions:

* User Roles
* Attendance
* BNCC Skills
* Assessment Templates
* Notifications
* Reports
* Performance Indicators

---

# Next Step

The next phase of the project includes:

* Creating the Entity Relationship Diagram (ERD);
* Implementing the database schema in MySQL;
* Creating migration scripts;
* Connecting the database with the application backend.
