# 🏗️ EduMove - Software Architecture

## Overview

EduMove follows the **Model-View-Controller (MVC)** architectural pattern, which separates the application into independent layers, improving code organization, scalability, and maintainability.

This architecture allows each component of the system to have a clear responsibility, making future updates and testing easier.

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
        ┌─────────┴─────────┐
        ▼                   ▼
 Business Rules         Utilities
   (Services)            (Utils)
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

Responsible for the graphical interface of the application.

### Technologies

* Streamlit

### Responsibilities

* Display pages
* Receive user input
* Display reports
* Display dashboards

---

## Controller

Acts as the communication layer between the interface and the business logic.

### Responsibilities

* Receive requests from the View
* Validate data
* Call the appropriate services
* Return responses to the interface

---

## Service

Contains the business rules of the application.

Examples:

* Register students
* Register assessments
* Generate reports
* Validate business rules

---

## Model

Represents the entities stored in the database.

Main entities:

* Teacher
* Class
* Student
* Assessment
* Motor Test

The Model layer communicates with the database through SQLAlchemy.

---

## Database

Database Management System:

* MySQL

Responsible for storing all application data.

---

# Project Structure

```text
src/
│
├── config/
├── controllers/
├── models/
├── services/
├── utils/
└── views/
```

---

# Technologies

| Layer         | Technology          |
| ------------- | ------------------- |
| Interface     | Streamlit           |
| Backend       | Python              |
| ORM           | SQLAlchemy          |
| Database      | MySQL               |
| Data Analysis | Pandas              |
| Charts        | Matplotlib / Plotly |
| Reports       | ReportLab           |

---

# Design Principles

The project follows the following software engineering principles:

* Separation of Concerns (SoC)
* Single Responsibility Principle (SRP)
* Modularity
* Code Reusability
* Scalability

---

# Future Improvements

Future versions of EduMove may include:

* REST API
* User authentication with JWT
* Docker deployment
* Cloud database
* Automated testing
* Continuous Integration (CI/CD)

---

# Current Status

Architecture defined.

Next step:

* Database modeling
* User interface prototyping
* Backend implementation
