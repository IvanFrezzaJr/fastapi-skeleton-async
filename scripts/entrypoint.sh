#!/bin/sh

# evita iniciar a palicacao se a migracao falhar
set -e

# Executa as migrações do banco de dados
uv run alembic upgrade head

# Inicia a aplicação
exec uv run uvicorn --host 0.0.0.0 --port 8000 app.main:app --reload