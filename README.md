# ServiceDeskAI Backend

This is the FastAPI backend for the ServiceDeskAI enterprise service desk application.

## Features
- **Role-based Authentication**: Secure login for Admins, Managers, Employees, and Service Agents using JWT.
- **Ticketing System**: Complete CRUD APIs for creating, assigning, and resolving tickets.
- **Knowledge Base**: Endpoints for managing knowledge articles.
- **Notifications & Audit**: Track system actions and alert users.
- **Chat & Reports**: Base structures for AI chat sessions and reporting.

## Project Structure
```
service_desk_ai_backend/
├── main.py             # FastAPI entrypoint
├── database.py         # SQLAlchemy async setup
├── models.py           # Database models
├── schemas.py          # Pydantic schemas
├── auth.py             # JWT & Password Hashing
├── routers/            # API Endpoints
├── .env.example        # Example environment variables
└── Dockerfile          # Multi-stage Docker build
```

## Running Locally

1. Set up a virtual environment and install dependencies (or use Poetry):
   ```bash
   pip install -r pyproject.toml
   # or
   poetry install
   ```

2. Configure your environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your `SUPABASE_DB_URL` and generate a `JWT_SECRET_KEY`.

3. Run the development server:
   ```bash
   uvicorn service_desk_ai_backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. View API Documentation:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Deployment to Render
This project includes a `render.yaml` configuration and a `Dockerfile` tailored for Render.com.
Follow the "Connect a Repository" flow in the Render dashboard and all configuration will be applied automatically.