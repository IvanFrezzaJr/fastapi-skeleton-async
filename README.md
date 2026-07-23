# FastAPI Skeleton

A production-ready skeleton application for building FastAPI microservices with async support, JWT authentication, and PostgreSQL database integration.

## Prerequisites

### System Requirements

- Docker (version 20.10 or later)
- Docker Compose (version 2.0 or later)
- Python 3.12+ (for local development without Docker)
- UV (for local development)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd fastapi-skeleton-async
```

### 2. Set Environment Variables
Create a `.env` file in the project root:

```bash
DATABASE_URL=postgresql+asyncpg://app_user:app_password@localhost:5432/app_db
SECRET_KEY=your-secret-key-min-32-chars-long
```

### 3. Install Dependencies

```bash
uv sync
```

### 4. Install precommit
```bash
uv run pre-commit install
```


### 5. Start with Docker Compose

The easiest way to run the project locally:

```bash
docker compose up -d
```

> migrations will be run through the scripts/entrypoint.sh

Access the application at `http://localhost:8000`.

API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 3. Stop the Application

```bash
docker compose down
```


## Database Migrations

Migrations are managed with Alembic. The application runs migrations automatically on startup via the entrypoint script.

### Create a New Migration
Update `DATABASE_URL` from `.env` file to access the `localhost` host rather than the `database` host.

> DATABASE_URL="postgresql+asyncpg://app_user:app_password@localhost:5432/app_db"

```bash
uv run alembic revision --autogenerate -m "description of changes"
```

### Apply Migrations

```bash
uv run alembic upgrade head
```

### Rollback to Previous Migration

```bash
uv run alembic downgrade -1
```


## Testing

### Run All Tests

```bash
uv run task test
```

### Run Tests Only

```bash
pytest -vv --cov=app
```

### Generate Coverage Report

```bash
pytest --cov=app --cov-report=html
```

Coverage report will be available at `htmlcov/index.html`.

### Run Specific Test File

```bash
pytest tests/routes/test_user.py -v
```

### Run Specific Test Function

```bash
pytest tests/routes/test_user.py::test_create_user -v
```

## Code Quality

### Linting

Check code style with Ruff:

```bash
task lint
```

### Formatting

Automatically fix style issues:

```bash
task format
```


## API Endpoints
Run the project using `docker-compose` and access:
```
GET /docs
```


## Production Deployment

### Build Production Image

```bash
docker build --target production -t app:latest .
```

### Run Production Container

```bash
docker run -d \
  --name fastapi-app \
  -e DATABASE_URL="postgresql+asyncpg://user:password@db:5432/app_db" \
  -e SECRET_KEY="your-secret-key" \
  -p 8000:8000 \
  app:latest
```


### Environment Variables for Production

Create a `.env.prod` file:

```bash
DB_PASSWORD=secure-db-password
SECRET_KEY=your-production-secret-key-minimum-32-chars
```


## Troubleshooting

### Database Connection Issues

Ensure PostgreSQL is running and accessible:

```bash
docker compose logs database
```

Check connection string in environment variables.

### Port Already in Use

If port 8000 is already in use:

```bash
docker compose down
docker compose up -d
```

Or use a different port in `docker-compose.yaml`.

### Permission Denied with Docker

Add your user to the docker group:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Tests Failing with 401 Unauthorized

Ensure JWT token scope is correctly configured in `app/services/security.py`. The access token must include `scope: 'access'`.


## License

This project is provided as a skeleton template for building FastAPI applications.

## Support

For issues, questions, or improvements, please open an issue in the repository.
