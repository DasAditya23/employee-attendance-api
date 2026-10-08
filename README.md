# Employee Attendance API

FastAPI backend for tracking employee attendance with JWT auth and role-based access.

## Live Demo
🔗 https://your-app.onrender.com/docs

## Features
- JWT auth with admin/employee roles
- Check-in/check-out with automatic late detection
- Attendance history with date filtering
- Auto-generated OpenAPI docs

## Tech Stack
FastAPI · SQLAlchemy · PostgreSQL · JWT · Docker

## API Endpoints
| Method | Endpoint | Auth | Description |
...

## Running Locally
\`\`\`bash
git clone ...
cp .env.example .env
docker compose up
\`\`\`

## Tests
\`\`\`bash
pytest --cov=app
\`\`\`
