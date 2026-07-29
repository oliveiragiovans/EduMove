# 🏗️ EduMove - Software Architecture

## Overview

EduMove follows an architectural approach based on the **Model-View-Controller (MVC)** pattern, combined with a service-oriented structure to separate presentation, business logic, and data persistence.

The main goal of this architecture is to improve maintainability, scalability, and organization by defining clear responsibilities between application components.

This structure allows future expansion of the system, including multiple schools, automated reports, dashboards, and integration with external services.

---

# Architecture Diagram

```text
                         User
                           │
                           ▼
                 Streamlit Interface
                       (View)
                           │
                           ▼
                  Controllers Layer
                           │
                           ▼
                 Services Layer
                           │
          ┌────────────────┴────────────────┐
          ▼                                 ▼
   Business Rules                        Utils
          │
          ▼
        Models
          │
          ▼
      SQLAlchemy ORM
          │
          ▼
        MySQL
```

---

# Architecture Layers

## View

Responsible for the user interface and interaction with the application.

### Technology

* Streamlit

### Responsibilities

* Display application pages
* Receive user inputs
* Present dashboards and reports
* Show assessment results

---

## Controller

Responsible for managing communication between the interface and application services.

### Responsibilities

* Receive requests from the View
* Validate input data
* Call appropriate services
* Return processed information to the interface

Controllers should not contain business logic.

---

## Service

Contains application workflows and coordinates business operations.

### Responsibilities

* Manage student registration
* Process assessments
* Generate reports
* Coordinate interactions between models and business rules

---

## Business Rules

Contains specific domain rules related to physical education assessments.

### Examples:

* Validate assessment requirements
* Apply evaluation criteria
* Consider gender-specific assessment parameters
* Calculate performance indicators

This layer keeps domain knowledge independent from the interface and database.

---

## Model

Represents the entities and relationships of the system.

Main entities:

* School
* Teacher
* School Class
* Student
* Assessment
* Motor Test
* Assessment Result

The Model layer communicates with the database through SQLAlchemy ORM.

---

## Database

Database Management System:

* MySQL
* InnoDB storage engine

Responsible for data persistence and maintaining relationships between entities.

The database structure supports:

* School management
* Student records
* Assessment history
* Motor development analysis

---

# Project Structure

```text
src/
│
├── config/
│
├── controllers/
│
├── models/
│
├── services/
│
├── business_rules/
│
├── utils/
│
└── views/
```

---

# Technologies

| Layer              | Technology          |
| ------------------ | ------------------- |
| Interface          | Streamlit           |
| Backend            | Python              |
| ORM                | SQLAlchemy          |
| Database           | MySQL               |
| Data Analysis      | Pandas              |
| Data Visualization | Matplotlib / Plotly |
| Reports            | ReportLab           |

---

# Design Principles

EduMove follows software engineering principles focused on maintainability and scalability:

* Separation of Concerns (SoC)
* Single Responsibility Principle (SRP)
* Modularity
* Code Reusability
* Domain-driven organization
* Scalability

---

# Future Improvements

Future versions of EduMove may include:

* REST API development
* User authentication with JWT
* Docker deployment
* Cloud database migration
* Automated testing
* Continuous Integration and Continuous Deployment (CI/CD)
* Mobile application integration

---

# Current Status

The database and ORM foundations are implemented. The application currently includes:

* Environment-based configuration
* SQLAlchemy engine and transactional session management
* Seven mapped database entities
* Bidirectional ORM relationships
* Configurable motor-test protocols and attempt limits
* InnoDB foreign-key enforcement
* School validation and normalization rules
* Transaction-aware school management service
* School-scoped teacher management service
* Active-administrator uniqueness validation
* School-scoped class management service
* Class normalization and responsible-teacher validation
* School-scoped student management and name search
* Safe student transfer between active classes
* School-scoped assessment management with historical class snapshots
* Anthropometric normalization and calculated BMI
* Automated model, business-rule, and service tests

Current development priorities:

* Assessment-result validation and aggregation
* Categorical postural-observation modeling
* User authentication
* Streamlit interface implementation
