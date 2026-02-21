# syntax=docker/dockerfile:1
# (The above line enables Docker BuildKit features)

# ==========================================
# STAGE 1: Builder
# ==========================================
FROM python:3.12-slim AS builder

# 1. Copy uv directly from the official Astral image (fastest installation method)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 2. uv Configuration
# Byte-compiling (.pyc) speeds up application startup time
ENV UV_COMPILE_BYTECODE=1
# 'copy' avoids symlink issues when moving the venv between Docker stages
ENV UV_LINK_MODE=copy

WORKDIR /app

# 3. Install dependencies utilizing Docker BuildKit caching
# We copy ONLY the lock files first to maximize Docker layer caching
COPY pyproject.toml uv.lock ./

# Use cache mount to completely speed up repeated builds
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# 4. Copy project and install it
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# 5. Pre-download the ML Model
# If we don't do this, Django will download it on startup, slowing down boots.
# We set a custom HuggingFace cache directory so we can easily copy it to the final stage.
ENV HF_HOME=/app/.huggingface
RUN .venv/bin/python -c "\
from sentence_transformers import SentenceTransformer; \
SentenceTransformer('all-MiniLM-L6-v2')\
"

# ==========================================
# STAGE 2: Final Production Image
# ==========================================
FROM python:3.12-slim

# Install system runtime dependencies
# libgomp1 is often required by the rust/c++ tokenizers inside sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Point HuggingFace to the directory we are about to copy
ENV HF_HOME=/app/.huggingface
# Put the virtual environment on the PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy the venv and baked ML model from the builder stage
# (This keeps the final image tiny by leaving behind build dependencies)
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/.huggingface /app/.huggingface

# Copy the actual application code
COPY . .

# Ensure the script is executable
RUN chmod +x /app/entrypoint.sh

# Run the pre-seeder script
RUN /app/entrypoint.sh

# Security: Run as a non-root user
RUN useradd -m django_user \
    && chown -R django_user:django_user /app
USER django_user

EXPOSE 8000

# Run via Gunicorn (Adjust 'myproject.wsgi' to your actual project name)
# Using multiple threads is recommended for CPU-bound ML tasks in Django
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4"]