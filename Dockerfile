# Gunicorn Docker config
FROM python:3.11-slim-bullseye AS builder

# Template config
# ENV MU_SPARQL_ENDPOINT 'http://database:8890/sparql'
# ENV MU_SPARQL_UPDATEPOINT 'http://database:8890/sparql'
# ENV MU_APPLICATION_GRAPH 'http://mu.semte.ch/application'

# Run dependencies
RUN apt-get update && apt-get install build-essential -y

RUN pip install --upgrade pip && pip install poetry==1.8.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Build over the application directory
WORKDIR /app
COPY poetry.lock pyproject.toml ./

# Install dependencies using Poetry
RUN poetry install 

FROM python:3.11-slim-bullseye AS base

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY ./app ./app

EXPOSE 9090

HEALTHCHECK CMD curl --fail http://localhost:9090/health

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9090"]
