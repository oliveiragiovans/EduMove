# 📋 EduMove - Software Requirements Specification (SRS)

## 1. Project Overview

### 1.1 Purpose

EduMove is a software application designed to assist Physical Education teachers in managing students, classes, and motor assessments. The platform aims to replace paper-based records with a digital solution that allows efficient data management and monitoring of students' motor development over time.

### 1.2 Target Users

* Physical Education teachers
* School administrators (future version)

---

# 2. Functional Requirements

## Authentication

### RF01

The system shall allow teachers to create an account.

### RF02

The system shall allow teachers to log in securely.

### RF03

The system shall allow teachers to log out.

---

## Class Management

### RF04

The system shall allow teachers to create classes.

### RF05

The system shall allow teachers to edit class information.

### RF06

The system shall allow teachers to deactivate classes without deleting their history.

### RF07

The system shall display a list of all registered classes.

---

## Student Management

### RF08

The system shall allow teachers to register students.

### RF09

The system shall allow teachers to edit student information.

### RF10

The system shall allow teachers to deactivate students without deleting their history.

### RF11

The system shall allow teachers to search students by name.

### RF12

The system shall display the students of each class.

---

## Motor Assessments

### RF13

The system shall allow teachers to create a motor assessment for a student.

### RF14

The system shall store the assessment date.

### RF15

The system shall allow multiple assessments for the same student.

### RF16

The system shall display the complete assessment history.

### RF17

The system shall allow the teacher to record optional body mass and height for an
assessment.

### RF18

The system shall calculate BMI from body mass and height without duplicating it as a
source measurement.

### RF19

The system shall record multiple attempts for each motor test.

### RF20

The system shall support measurement results and binary success/failure trials.

### RF21

The system shall aggregate attempts according to the motor-test protocol.

### RF22

The system shall allow 3 to 10 ball-reception throws, selected by the teacher.

### RF23

The system shall record educational postural observations for shoulders, spine,
knees, and feet with visual references.

---

## Reports

### RF24

The system shall allow teachers to view student progress.

### RF25

The system shall generate reports (future version).

---

# 3. Non-Functional Requirements

### RNF01

The application shall be developed using Python.

### RNF02

The user interface shall be developed using Streamlit.

### RNF03

The database shall use MySQL.

### RNF04

The project shall use Git and GitHub for version control.

### RNF05

The application shall provide a simple and intuitive interface.

### RNF06

The system shall ensure secure authentication.

### RNF07

Postural observations shall be presented as educational screening records and not as
medical diagnoses.

### RNF08

Protocol source and version information shall remain available so historical results
can be interpreted correctly.

---

# 4. Future Features

* Dashboard with statistics
* PDF report generation
* Excel export
* Import students from spreadsheets
* Data visualization charts
* BNCC skills tracking
* Artificial Intelligence support
* Mobile version

---

# 5. Project Status

Current Version: Backend Foundation

Next Step:

* User authentication
* Initial Streamlit management interface with guided postural observations
