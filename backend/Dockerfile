FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder

WORKDIR /app

COPY backend/pyproject.toml backend/uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

FROM python:3.12-alpine

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY backend/ .

ENV PATH="/app/.venv/bin:$PATH"

ENV PYTHONPATH="/app"

CMD ["python", "main.py"]
