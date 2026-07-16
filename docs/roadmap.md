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
* [ ] Consolidate migrations into `schema.sql` or implement a migration runner
* [ ] Configure SQLAlchemy models

---

## Backend

* [ ] Configure project structure
* [ ] Configure environment variables
* [ ] Connect application to MySQL
* [ ] Implement SQLAlchemy ORM
* [ ] Create business rules layer
* [ ] Implement user authentication
* [ ] CRUD operations for schools
* [ ] CRUD operations for teachers
* [ ] CRUD operations for classes
* [ ] CRUD operations for students
* [ ] CRUD operations for assessments
* [ ] Motor test result management

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
* [ ] Foreign key and constraint validation tests
* [ ] Unit tests
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
| Database Automation | ⏳ Planned |
| Backend Development | ⏳ Planned |
| Frontend Development | ⏳ Planned |
| Testing | 🔄 In Progress |
| Deployment | ⏳ Planned |

---

# 📌 Current Sprint

## Sprint 1 — Project Foundation

### Completed

* [x] Complete project documentation
* [x] Finalize the initial database structure
* [x] Create the ERD diagram
* [x] Prepare the MySQL environment
* [x] Define the application architecture
* [x] Create migrations for the seven main tables
* [x] Create the initial motor test seed
* [x] Validate the complete database flow with `ROLLBACK`

### Remaining

* [ ] Consolidate schema execution
* [ ] Add negative database tests
* [ ] Prepare the backend project structure

---

# 🎯 Next Milestone

Complete database automation and begin backend development by configuring the Python project structure, MySQL connection, and SQLAlchemy models.