#########################
# Base
#########################

FROM python:3.12-slim AS base

WORKDIR /app



# avoid to create __pycache__
ENV PYTHONDONTWRITEBYTECODE=1

# show python logs in real time
ENV PYTHONUNBUFFERED=1

# add python bin path to global linux path
ENV PATH="/app/.venv/bin:$PATH"


#########################
# Builder
#########################

FROM base AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:$PATH"

COPY pyproject.toml uv.lock ./

# Instala apenas as dependências de produção
RUN uv sync \
    --frozen \
    --no-dev \
    --no-install-project

COPY . .

# Instala o projeto na venv
RUN uv sync \
    --frozen \
    --no-dev


#########################
# Development
#########################

FROM builder AS development

# Reinstala incluindo dependências de desenvolvimento
RUN uv sync --frozen

CMD ["uv", \
    "run", \
    "uvicorn", \
    "app.main:app", \
    "--host", \
    "0.0.0.0", \
    "--port", \
    "8000", \
    "--reload"]


#########################
# Production
#########################

FROM base AS production

COPY --from=builder /app/.venv /app/.venv
COPY . .

CMD ["gunicorn", \
    "app.main:app", \
    "-k", \
    "uvicorn.workers.UvicornWorker", \
    "--workers", \
    "2", \
    "--bind", \
    "0.0.0.0:8000", \
    "--graceful-timeout", \
    "30", \
    "--timeout", \
    "120", \
    "--access-logfile", \
    "-", \
    "--error-logfile", \
    "-", \
    "--log-level", \
    "info"]