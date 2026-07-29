# 🗺️ EduMove - Project Roadmap

## Overview

This roadmap describes the planned development stages of EduMove, organizing features and improvements into progressive versions.

The development strategy focuses on delivering a functional MVP first, while maintaining an architecture prepared for scalability and future educational features.

---

# 🚧 Version 1.0 - Minimum Viable Product (MVP)

**Goal:** Develop the core platform for managing students and motor assessments in physical education environments.

---

## Planning & Documentation

* [x] Project creation
* [x] Repository setup
* [x] Software documentation
* [x] Database modeling
* [x] Software architecture definition
* [x] Initial wireframes and navigation flow
* [x] Entity Relationship Diagram (ERD)

---

## Database

* [x] Define database entities
* [x] Create initial relational model
* [x] Implement the initial MySQL schema
* [x] Create migration scripts
* [x] Create the initial motor test seed
* [x] Validate the complete database relationship flow
* [x] Consolidate migrations into `schema.sql`
* [x] Validate the consolidated schema in a temporary database
* [x] Standardize all tables on InnoDB
* [x] Restore and validate all foreign keys
* [x] Add configurable motor-test protocol metadata
* [x] Configure SQLAlchemy models
* [ ] Implement an automated migration runner

---

## Backend

* [x] Configure project structure
* [x] Configure environment variables
* [x] Connect application to MySQL
* [x] Implement SQLAlchemy ORM
* [x] Map all nine current database entities
* [x] Configure motor-test attempts and aggregation rules
* [x] Establish the business-rules layer with school validation
* [ ] Implement the remaining domain validation rules
* [ ] Implement user authentication
* [x] CRUD operations for schools
* [x] CRUD operations for teachers
* [x] CRUD operations for classes
* [x] CRUD operations for students
* [x] CRUD operations for assessments
* [x] Motor test result management
* [x] Categorical postural observation management

---

## Frontend

* [ ] Login page
* [ ] Dashboard
* [ ] School and class management
* [ ] Student management
* [ ] Assessment registration form
* [ ] Assessment history visualization

---

## Testing

* [x] Initial database integration test
* [x] Foreign key and constraint validation tests
* [x] ORM model unit tests
* [x] Service and business-rule unit tests
* [ ] Application integration tests

---

# 📊 Version 1.1 - Reports & Analytics

**Goal:** Transform assessment data into useful insights for teachers.

Features:

* [ ] Student progress charts
* [ ] Class performance dashboard
* [ ] PDF report generation
* [ ] Excel export
* [ ] Search and filtering system
* [ ] Performance indicators
* [ ] Assessment comparison over time

---

# ☁️ Version 2.0 - Scalability & Platform Features

**Goal:** Expand EduMove into a complete educational platform.

Features:

* [ ] Multi-school account management
* [ ] Advanced user roles and permissions
* [ ] Password recovery
* [ ] Email notifications
* [ ] Responsive interface
* [ ] Cloud deployment
* [ ] Database optimization

---

# 🤖 Version 3.0 - Intelligent Features

**Goal:** Support decision-making through data analysis and automation.

Features:

* [ ] AI-assisted assessment analysis
* [ ] Personalized recommendations
* [ ] BNCC skills tracking
* [ ] Automatic student performance reports
* [ ] Predictive analytics
* [ ] REST API development

---

# 📱 Long-Term Vision

Future possibilities for EduMove include:

* Mobile application
* Offline mode
* Integration with school management systems
* Parent portal
* Teacher community
* Advanced educational analytics

---

# 📈 Project Timeline

| Phase | Status |
| --- | --- |
| Planning | ✅ Completed |
| Documentation | ✅ Completed |
| Database Design | ✅ Completed |
| Initial Database Implementation | ✅ Completed |
| Database Automation | 🔄 In Progress |
| Backend Development | 🔄 In Progress |
| Frontend Development | ⏳ Planned |
| Testing | 🔄 In Progress |
| Deployment | ⏳ Planned |

---

# 📌 Current Sprint

## Sprint 2 — Backend Foundation

### Completed

* [x] Configure environment loading and MySQL sessions
* [x] Implement the SQLAlchemy declarative base
* [x] Implement all current ORM models and relationships
* [x] Convert the database from MyISAM to InnoDB
* [x] Restore and validate nine foreign keys
* [x] Define the initial assessment MVP
* [x] Configure motor-test attempt and aggregation metadata
* [x] Add the adapted sit-and-reach test to the MVP seed
* [x] Add logical deactivation to schools with migration 010
* [x] Implement the first CRUD workflow for schools
* [x] Implement the teacher CRUD with school isolation
* [x] Enforce one active administrator per school
* [x] Implement the class CRUD with school and responsible-teacher validation
* [x] Validate the class CRUD transactionally against MySQL
* [x] Implement the student CRUD with class transfer and name search
* [x] Prevent class deactivation while active students remain enrolled
* [x] Validate the student CRUD transactionally against MySQL
* [x] Implement the assessment CRUD with historical class snapshots
* [x] Validate anthropometric measurements and assessment chronology
* [x] Validate the assessment CRUD transactionally against MySQL
* [x] Implement protocol-aware motor-test attempt management
* [x] Preserve binary results as successes over total attempts
* [x] Validate motor-result aggregation transactionally against MySQL
* [x] Create original reference boards for shoulders, spine, knees, and footprints
* [x] Add the 20-option educational posture catalog
* [x] Preserve replaced postural choices as inactive history
* [x] Validate the postural workflow transactionally against MySQL
* [x] Reach 322 passing automated tests

### Remaining

* [ ] Implement the automated migration runner
* [ ] Implement user authentication

---

# 🎯 Next Milestone

Implement authentication and begin the Streamlit management interface, including
the guided postural-observation form.
