# Banking Project API

Production-style fintech backend built with FastAPI and clean layered architecture.

## Architecture
- `app/api`: routers/controllers
- `app/services`: business logic
- `app/db/models`: SQLAlchemy entities
- `app/db/repositories`: repository layer (extensible)
- `app/schemas`: DTOs
- `app/core`: config/security/logging/aws/redis helpers

## Local setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[test]
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

## Docker setup
```bash
docker compose up --build
```

## Environment variables
See `.env.example` for all variables (DB, JWT, Redis, S3, fraud threshold).

## Migrations
```bash
alembic upgrade head
alembic downgrade -1
```

## Seed data
```bash
python scripts/seed_data.py
```

## API examples
```bash
curl -X POST localhost:8000/api/v1/auth/register -H 'content-type: application/json' -d '{"email":"user@example.com","full_name":"User","password":"Password123!"}'
```

## Security notes
- bcrypt password hashing
- JWT access + refresh tokens
- refresh token rotation + revoke
- ownership checks and admin check
- Redis-backed login rate limiting

## AWS notes
- Statement export uploads CSV to S3 via boto3.
- IAM-role credentials are used automatically on EC2 when static keys are not set.
- If S3 bucket is not configured, endpoint returns HTTP 503.

## Testing
```bash
pytest -q
```

## CI
GitHub Actions runs install, `pip check`, compile checks, and tests.
