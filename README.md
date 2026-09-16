# Hospital Management System

A full-stack Hospital Management System built with **FastAPI, PostgreSQL, SQLAlchemy Async, JWT Authentication, HTML, CSS, and JavaScript**.

The system provides management functionality for patients, doctors, doctor working hours, and appointments, including appointment validation, cancellation, rescheduling, and protection against overlapping bookings.

---

## Features

### Authentication

* User registration
* JWT-based login
* Bearer token authentication
* Password hashing
* Protected API endpoints

### Patient Management

* Create patient
* View all patients
* View individual patient
* Update patient
* Delete patient

### Doctor Management

* Create doctor
* View all doctors
* View individual doctor
* Update doctor
* Delete doctor

### Doctor Working Hours

* Add working hours for a doctor
* View working hours
* Update working hours
* Delete working hours
* Day-based working-hour management

### Appointment Management

* Create appointment
* View appointments
* View individual appointment
* Update appointment
* Delete appointment
* Cancel appointment
* Reschedule appointment
* Appointment duration support

### Appointment Validation

The system validates appointments against important business rules:

* Appointments cannot be scheduled in the past.
* Appointments must fall within the doctor's working hours.
* Overlapping appointments for the same doctor are prevented.
* Invalid rescheduling does not modify the original appointment.
* Database transaction locking is used to handle concurrent appointment requests.

### Dashboard

* Patient count
* Doctor count
* Appointment count
* Navigation to major management sections

---

## Tech Stack

### Backend

* Python 3.13
* FastAPI
* Uvicorn
* SQLAlchemy 2.x
* Async SQLAlchemy
* asyncpg
* Pydantic v2
* JWT Authentication

### Database

* PostgreSQL

### Frontend

* HTML
* CSS
* JavaScript

### Development Tools

* Swagger / OpenAPI
* pgAdmin 4
* Git / GitHub

---

## Project Architecture

The application follows a simple layered structure separating API routes, database models, schemas, authentication, and frontend files.

```text
hospital-api/
│
├── app/
│   ├── main.py
│   │
│   ├── models/
│   │   ├── patient.py
│   │   ├── doctor.py
│   │   ├── appointment.py
│   │   ├── working_hours.py
│   │   └── user.py
│   │
│   ├── routers/
│   │   ├── patient.py
│   │   ├── doctor.py
│   │   ├── appointment.py
│   │   ├── working_hours.py
│   │   └── auth.py
│   │
│   ├── schema.py
│   ├── database.py
│   └── ...
│
├── frontend/
│   ├── index.html
│   ├── dashboard.html
│   ├── patients.html
│   ├── doctors.html
│   ├── working_hours.html
│   ├── appointments.html
│   │
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       └── app.js
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

> The exact filenames may vary slightly depending on the current project structure.

---

## Database

The application uses **PostgreSQL** as its relational database.

Main entities:

```text
User
 │
 └── Authentication

Patient
 │
 └──────────────┐
                │
                ▼
           Appointment
                ▲
                │
Doctor ─────────┘
  │
  └── Working Hours
```

### Main Relationships

* A patient can have multiple appointments.
* A doctor can have multiple appointments.
* A doctor can have multiple working-hours records.
* An appointment references both a patient and a doctor.
* Foreign keys maintain database relationships.

---

## Authentication

The application uses **JWT (JSON Web Token)** authentication.

Authentication flow:

```text
User
 │
 ▼
Login
 │
 ▼
Username + Password
 │
 ▼
Password Verification
 │
 ▼
JWT Token
 │
 ▼
Frontend stores token
 │
 ▼
Authorization: Bearer <token>
 │
 ▼
Protected API
```

Passwords are not stored as plain text.

The `User` model stores:

```text
id
username
hashed_password
status
```

The database column is `hashed_password`, not `password`.

---

## Appointment Scheduling Logic

Appointment scheduling contains the main business logic of the application.

Before creating or rescheduling an appointment, the backend validates the requested slot.

### 1. Past Appointment Check

Appointments cannot be created for a time that has already passed.

```text
Requested time
      │
      ▼
Is it in the past?
   │          │
  YES         NO
   │          │
 Reject     Continue
```

### 2. Working Hours Check

The requested appointment must fall within the doctor's configured working hours.

Example:

```text
Doctor Working Hours
09:00 ───────────────── 17:00

Valid:
10:00 → 10:30

Invalid:
08:30 → 09:00
16:45 → 17:30
```

### 3. Overlap Check

The backend prevents two active appointments from occupying the same doctor's time slot.

Example:

```text
Existing:
10:00 ───── 10:30

New:
10:15 ───── 10:45

Result:
Rejected
```

But:

```text
Existing:
10:00 ───── 10:30

New:
10:30 ───── 11:00

Result:
Allowed
```

### 4. Rescheduling

When an appointment is rescheduled, the new slot goes through the same validation rules.

If validation fails, the original appointment remains unchanged.

---

## Concurrency Handling

Appointment booking can have a race-condition problem.

For example:

```text
Request A ──┐
            ├── Same doctor + same time
Request B ──┘
```

If both requests check availability at the same time, both could potentially see the slot as available before either transaction finishes.

To handle this, the application uses a **PostgreSQL advisory transaction lock** around the relevant appointment operation.

Conceptually:

```text
Request
   │
   ▼
Begin Transaction
   │
   ▼
Acquire PostgreSQL Advisory Lock
   │
   ▼
Check Appointment Availability
   │
   ▼
Validate Working Hours / Overlap
   │
   ▼
Create or Reschedule
   │
   ▼
Commit / Rollback
```

This helps serialize competing operations for the relevant scheduling resource and reduces the risk of race-condition-based double booking.

---

## API Endpoints

### Authentication

| Method | Endpoint         | Purpose              |
| ------ | ---------------- | -------------------- |
| POST   | `/auth/register` | Register user        |
| POST   | `/auth/login`    | Login and obtain JWT |

### Patients

| Method | Endpoint                 | Purpose          |
| ------ | ------------------------ | ---------------- |
| POST   | `/patients`              | Create patient   |
| GET    | `/patients`              | Get all patients |
| GET    | `/patients/{patient_id}` | Get one patient  |
| PUT    | `/patients/{patient_id}` | Update patient   |
| DELETE | `/patients/{patient_id}` | Delete patient   |

### Doctors

| Method | Endpoint               | Purpose         |
| ------ | ---------------------- | --------------- |
| POST   | `/doctors`             | Create doctor   |
| GET    | `/doctors`             | Get all doctors |
| GET    | `/doctors/{doctor_id}` | Get one doctor  |
| PUT    | `/doctors/{doctor_id}` | Update doctor   |
| DELETE | `/doctors/{doctor_id}` | Delete doctor   |

### Working Hours

| Method | Endpoint                                                | Purpose              |
| ------ | ------------------------------------------------------- | -------------------- |
| POST   | `/doctors/{doctor_id}/working-hours`                    | Create working hours |
| GET    | `/doctors/{doctor_id}/working-hours`                    | Get working hours    |
| PUT    | `/doctors/{doctor_id}/working-hours/{working_hours_id}` | Update working hours |
| DELETE | `/doctors/{doctor_id}/working-hours/{working_hours_id}` | Delete working hours |

### Appointments

| Method | Endpoint                                    | Purpose                |
| ------ | ------------------------------------------- | ---------------------- |
| POST   | `/appointments/`                            | Create appointment     |
| GET    | `/appointments/`                            | Get appointments       |
| GET    | `/appointments/{appointment_id}`            | Get one appointment    |
| PUT    | `/appointments/{appointment_id}`            | Update appointment     |
| DELETE | `/appointments/{appointment_id}`            | Delete appointment     |
| PUT    | `/appointments/{appointment_id}/cancel`     | Cancel appointment     |
| PUT    | `/appointments/{appointment_id}/reschedule` | Reschedule appointment |

---

## Working Hours Day Mapping

The application uses the following day mapping:

| Number | Day       |
| -----: | --------- |
|      1 | Monday    |
|      2 | Tuesday   |
|      3 | Wednesday |
|      4 | Thursday  |
|      5 | Friday    |
|      6 | Saturday  |
|      7 | Sunday    |

---

## Environment Variables

Create a `.env` file in the project root.

Example:

```env
DATABASE_URL=your_postgresql_connection_string
SECRET_KEY=your_secret_key
```

Do **not** commit the real `.env` file to GitHub.

Use `.env.example` for documenting required environment variables without exposing secrets.

---

## Installation

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd hospital-api
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Windows:

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create:

```text
.env
```

and add the required PostgreSQL database URL and application secret.

### 6. Start PostgreSQL

Make sure PostgreSQL is running and the required database exists.

### 7. Start FastAPI

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## API Documentation

FastAPI automatically provides Swagger UI.

Open:

```text
http://127.0.0.1:8000/docs
```

Swagger can be used to:

* View API endpoints
* Send requests
* Test request bodies
* Test authentication
* Inspect responses
* Verify validation errors

---

## Frontend

The project includes a basic HTML/CSS/JavaScript administrative frontend.

Main flow:

```text
Login
  ↓
Dashboard
  ├── Patients
  ├── Doctors
  ├── Working Hours
  └── Appointments
```

The frontend communicates with the FastAPI backend using HTTP requests.

JWT authentication is used when accessing protected endpoints.

---

## Testing

The completed application has been manually tested for the following functionality:

* Patient CRUD
* Doctor CRUD
* Doctor Working Hours CRUD
* Appointment CRUD
* Appointment duration
* Past appointment validation
* Working-hours validation
* Appointment overlap prevention
* Appointment cancellation
* Appointment rescheduling
* Failed reschedule rollback
* JWT login protection
* Dashboard counts
* Dashboard navigation
* Frontend appointment scheduling
* Frontend cancellation and rescheduling

---

## Project Development Approach

The project was developed incrementally:

```text
FastAPI Fundamentals
        ↓
Pydantic & Request Validation
        ↓
Response Handling
        ↓
Dependency Injection
        ↓
PostgreSQL
        ↓
SQLAlchemy Async
        ↓
Authentication
        ↓
Appointment Business Logic
        ↓
Concurrency Handling
        ↓
Frontend Integration
        ↓
Testing
        ↓
Deployment
```

The focus was on building a functional backend first and then integrating it with the frontend.

---

## Important Design Decisions

### Why FastAPI?

FastAPI provides:

* Automatic OpenAPI documentation
* Request/response validation
* Type hints
* Async support
* Dependency injection
* Good developer productivity

### Why PostgreSQL?

PostgreSQL provides:

* Relational data modelling
* Foreign keys
* Transactions
* Strong data integrity
* Concurrency features
* Production-grade database capabilities

### Why SQLAlchemy Async?

SQLAlchemy provides ORM capabilities while its async API allows database operations to work naturally with FastAPI's asynchronous request handling.

### Why JWT?

JWT provides a stateless mechanism for authenticating API requests.

### Why Password Hashing?

Plain-text passwords should never be stored in a database. Password hashing allows the application to verify passwords without storing the original password.

---

## Security Notes

For a production deployment, the following should be configured carefully:

* Strong secret key
* Secure environment variables
* HTTPS
* Proper CORS configuration
* Secure JWT configuration
* Database credentials outside source control
* Production database configuration
* Appropriate logging and monitoring

---

## Future Improvements

Possible future improvements include:

* Role-based authorization
* Admin/Doctor/Receptionist roles
* Automated test suite with pytest
* Database migrations with Alembic
* Pagination and filtering
* Better frontend UX
* React frontend
* Docker containerization
* Production logging
* Monitoring
* CI/CD pipeline
* Cloud deployment

---

## Current Status

**Functional development: Complete**

**Frontend development: Complete**

**Final testing: Complete**

The project is ready for GitHub preparation and deployment.
