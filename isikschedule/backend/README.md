# IşıkSchedule Backend

Enterprise-grade course scheduling API powered by FastAPI.

## Tech Stack
- **FastAPI** - Async API framework
- **PostgreSQL** - Primary database
- **Redis** - Caching & job queue
- **Celery** - Background task processing
- **SQLAlchemy** - ORM

## Quick Start

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env

# CRITICAL: Generate and set a strong SECRET_KEY
# Option 1: Generate with openssl (recommended)
openssl rand -hex 32
# Copy the output and paste it as SECRET_KEY value in .env

# Option 2: Generate with Python
python -c "import secrets; print(secrets.token_hex(32))"
# Copy the output and paste it as SECRET_KEY value in .env

# Edit .env and replace SECRET_KEY with the generated value
# Example: SECRET_KEY=a7f3d9e2b8c4a1f6e9d3c7b5a2f8e4d1c9b7a5f3e1d9c7b5a3f1e9d7c5b3a1f9

# Run development server
uvicorn app.main:app --reload
```

## Environment Setup

### Required Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `SECRET_KEY` | JWT token signing key (min 32 chars) | **Yes** | `openssl rand -hex 32` |
| `DATABASE_URL` | PostgreSQL connection string | Yes | `postgresql+asyncpg://user:pass@localhost:5432/db` |
| `REDIS_URL` | Redis connection string | Yes | `redis://localhost:6379/0` |

⚠️ **Security Note**: The application will **fail to start** if `SECRET_KEY` is not set or is too weak (< 32 characters). This is a security feature to prevent accidental deployment with weak credentials.

## Project Structure
```
backend/
├── app/
│   ├── main.py          # FastAPI application
│   ├── config.py        # Settings
│   ├── api/routes/      # API endpoints
│   ├── core/            # Business logic (from PyQt6)
│   ├── algorithms/      # Scheduling algorithms
│   ├── services/        # Service layer
│   ├── tasks/           # Celery tasks
│   └── db/              # Database models
├── tests/               # Test suite
├── requirements.txt
└── Dockerfile
```

## API Documentation
Available at `/docs` (Swagger) or `/redoc` when running.
