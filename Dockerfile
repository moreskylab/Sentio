# syntax=docker/dockerfile:1
# === Stage 1: Builder ===
# Use a Python base image
FROM python:3.12-slim-bookworm AS builder

# Copy the uv binary from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment variables for the virtual environment
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create the virtual environment and install dependencies from a locked file
WORKDIR /app
COPY pyproject.toml uv.lock ./
# Use a cache mount for faster rebuilds
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen

# === Stage 2: Runtime ===
# Start from a clean base image
FROM python:3.12-slim-bookworm

# Set environment variables
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy the created virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
# Copy your Django project code
COPY . .

# Copy the entrypoint script into the container and make it executable
# Note: The chmod +x may not be needed if the script was already executable on the host and source control preserved the permission
RUN chmod +x entrypoint.sh

# Set the script as the default command to run when the container starts
CMD ["./entrypoint.sh"]

# Run your Django application (e.g., using 'uv run' for convenience during development, 
# or a production server like Gunicorn)
# CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"] # For local dev with uv run
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"] # For production
