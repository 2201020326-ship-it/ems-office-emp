# EMS Frontend

React frontend integrated with FastAPI backend at `http://127.0.0.1:8000`.

## Setup

1. Install dependencies:

```bash
npm install
```

2. Run development server:

```bash
npm run dev
```

3. Build for production:

```bash
npm run build
```

## Features Implemented

- Login via `POST /login` with JWT token storage in localStorage
- Role-based redirect to admin or employee dashboard
- Axios API client with base URL and Authorization interceptor
- Admin register employee via `POST /register`
- Admin add work details via `POST /work-details`
- Employee timesheets via `GET /timesheets/{employee_id}`
- Employee attendance via `GET /attendance/report/{employee_id}`
- `useEffect` based data loading and alert-based error handling
