# EMS Office Employee Management System

A full-stack Employee Management System for attendance tracking, leave management, payroll processing, and employee support chatbot workflows.

## Tech Stack

- Backend: FastAPI (Python)
- Frontend: React + Vite
- Database: MySQL (via mysql-connector-python)
- Auth: JWT-based authentication and role authorization

## Core Features

- Role-based login for admin and employee users
- Attendance leave application and attendance reporting
- Work detail slot logging and timesheet history
- Payroll generation (admin) and payroll history view
- Employee support chatbot and FAQ endpoints

## Project Structure

- main.py: FastAPI app entry point
- run_ems.bat: One-click local startup for backend + frontend
- requirements.txt: Python dependencies
- routes/: Attendance, payroll, and chatbot APIs
- services/: Business logic for attendance, payroll, timesheet, employee
- frontend/: React application
- database/: Database initialization and connectivity
- schemas/ and schema/: Request/response and model definitions

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm
- MySQL server

## Environment Setup

Create a .env file in the project root with your database and JWT settings used by the backend.

Example variables (names may vary based on your local config):

- DB_HOST
- DB_PORT
- DB_USER
- DB_PASSWORD
- DB_NAME
- JWT_SECRET_KEY
- JWT_ALGORITHM

## Installation

### 1) Backend

1. Create and activate virtual environment
2. Install dependencies from requirements.txt

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2) Frontend

```powershell
cd frontend
npm install
cd ..
```

## Run the Application

### Option A: One-click startup (recommended)

```powershell
.\run_ems.bat
```

This starts:

- Frontend: http://127.0.0.1:5173
- Backend Swagger docs: http://127.0.0.1:8000/docs
- Chatbot FAQ endpoint: http://127.0.0.1:8000/chatbot/faqs

### Option B: Start manually

Backend:

```powershell
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

## API Overview

### Auth and Employee

- POST /login
- POST /register (admin only)

### Work Details and Timesheets

- POST /work-details
- GET /timesheets/{employee_id}
- DELETE /work-details/{employee_id}/{work_date} (admin only)

### Attendance

- POST /attendance/leave
- GET /attendance/report/{employee_id}

### Payroll

- POST /payroll/generate/{employee_id} (admin only)
- GET /payroll/{employee_id}

### Chatbot

- GET /chatbot/faqs
- POST /chatbot/support

## Frontend Build

```powershell
cd frontend
npm run build
npm run preview
```

## Notes

- Keep .env, virtual environments, node_modules, and build artifacts out of version control.
- Use role-based routes and JWT token flow for protected API access.

## License

This repository currently has no explicit license file.
