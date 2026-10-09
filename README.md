# Employee Attendance API

A RESTful backend for tracking employee attendance, built with **FastAPI**, **SQLAlchemy**, and **JWT authentication**. Supports role-based access control (admin vs employee), automatic late detection, and date-range attendance queries.
## 🔗 Live Demo

**Try it:** [https://employee-attendance-api-cb2j.onrender.com/docs](https://employee-attendance-api-cb2j.onrender.com/docs)

> ⚠️ Free tier: the service sleeps after 15 minutes of inactivity. First request takes 30–50 seconds to wake up.

## Features

- 🔐 **JWT authentication** with role-based access (admin / employee)
- 👥 **Employee management** — create, list, update, delete (admin only)
- ⏰ **Check-in / check-out** with duplicate prevention and automatic late detection (after 9:30 AM)
- 📅 **Attendance history** with optional date-range filtering
- 📖 **Auto-generated OpenAPI docs** at `/docs`

## Tech Stack

- **Framework:** FastAPI
- **ORM:** SQLAlchemy 2.x
- **Database:** SQLite (dev)
- **Auth:** JWT (`python-jose`) + bcrypt password hashing
- **Validation:** Pydantic v2
- **Server:** Uvicorn

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET    | `/`                               | –        | Health check |
| POST   | `/auth/register`                  | –        | Register a new user |
| POST   | `/auth/login`                     | –        | Obtain a JWT token |
| POST   | `/employees`                      | admin    | Create an employee |
| GET    | `/employees`                      | any user | List all employees |
| GET    | `/employees/{id}`                 | any user | Get one employee |
| PUT    | `/employees/{id}`                 | admin    | Update an employee |
| DELETE | `/employees/{id}`                 | admin    | Delete an employee |
| POST   | `/attendance/check-in/{id}`       | any user | Check in for today |
| POST   | `/attendance/check-out/{id}`      | any user | Check out for today |
| GET    | `/attendance/{id}`                | any user | Attendance history (with `from_date`, `to_date`) |

## Running Locally

### Prerequisites

- Python 3.11+
- Git

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/DasAditya23/employee-attendance-api.git
cd employee-attendance-api

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
uvicorn app.main:app --reload