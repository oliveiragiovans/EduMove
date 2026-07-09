# 🗄️ EduMove - Database Documentation

## Overview

The EduMove database is designed to store information about teachers, classes, students, and motor assessments. The goal is to maintain data integrity while supporting future features such as reports, dashboards, and student progress analysis.

---

# Database Management System

* DBMS: MySQL
* Language: SQL
* ORM: SQLAlchemy (planned)

---

# Database Structure

## Teacher

Stores information about registered teachers.

| Field    | Type         | Description         |
| -------- | ------------ | ------------------- |
| id       | INT          | Primary Key         |
| name     | VARCHAR(100) | Teacher's full name |
| email    | VARCHAR(100) | Unique email        |
| password | VARCHAR(255) | Encrypted password  |

---

## Class

Stores school classes.

| Field       | Type        | Description           |
| ----------- | ----------- | --------------------- |
| id          | INT         | Primary Key           |
| name        | VARCHAR(50) | Class name            |
| school_year | VARCHAR(20) | School year           |
| teacher_id  | INT         | Foreign Key → Teacher |

---

## Student

Stores student information.

| Field      | Type         | Description         |
| ---------- | ------------ | ------------------- |
| id         | INT          | Primary Key         |
| name       | VARCHAR(100) | Student name        |
| birth_date | DATE         | Birth date          |
| gender     | VARCHAR(20)  | Gender              |
| class_id   | INT          | Foreign Key → Class |

---

## Assessment

Stores each assessment performed.

| Field           | Type         | Description           |
| --------------- | ------------ | --------------------- |
| id              | INT          | Primary Key           |
| student_id      | INT          | Foreign Key → Student |
| assessment_date | DATE         | Assessment date       |
| weight          | DECIMAL(5,2) | Weight (kg)           |
| height          | DECIMAL(4,2) | Height (m)            |
| notes           | TEXT         | Teacher observations  |

---

## Motor Test

Stores motor performance results.

| Field              | Type         | Description              |
| ------------------ | ------------ | ------------------------ |
| id                 | INT          | Primary Key              |
| assessment_id      | INT          | Foreign Key → Assessment |
| horizontal_jump    | DECIMAL(5,2) | Horizontal jump          |
| single_leg_balance | INT          | Balance time (seconds)   |
| ball_reception     | INT          | Successful catches       |
| throwing_accuracy  | INT          | Successful throws        |
| agility            | DECIMAL(5,2) | Agility test result      |

---

# Entity Relationships

Teacher (1) ──────── (N) Class

Class (1) ────────── (N) Student

Student (1) ──────── (N) Assessment

Assessment (1) ───── (1) Motor Test

---

# Future Tables

The following tables may be added in future versions:

* School
* User Roles
* Attendance
* BNCC Skills
* Assessment Templates
* Notifications

---

# Next Step

The next phase of the project is creating the Entity Relationship Diagram (ERD) and implementing the database schema in MySQL.
