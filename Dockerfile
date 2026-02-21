# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# FIX: Added required Railway prefix "s/" and consistent ID format
RUN uv sync --locked --no-install-project

COPY . /app

# FIX: Every cache mount must use the hardcoded Service ID prefix on Railway
RUN uv sync --locked

ENV PATH="/app/.venv/bin:$PATH"

# Ensure entrypoint is executable before switching users
RUN chmod +x entrypoint.sh

USER nonroot
ENTRYPOINT ["./entrypoint.sh"]
