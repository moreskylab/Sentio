# syntax=docker/dockerfile:1
# === Stage 1: Builder ===
FROM python:3.12-slim-bookworm AS builder



# Copy uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Environment settings for build performance
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

# Install dependencies using mandatory id in cache mount
RUN --mount=type=cache,id=s/c2cf75a2-3467-4e04-b406-dfa42183ec4c-uv,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# === Stage 2: Runtime ===
FROM python:3.12-slim-bookworm

ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy the virtual environment from the builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY . .

RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
