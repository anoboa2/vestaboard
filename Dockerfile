# Dockerfile for Vestaboard API
# Uses uv for fast dependency installation

FROM python:3.13-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev --no-install-project

# Copy application code
COPY . .

# Install project
RUN uv sync --frozen --no-dev

# Production stage
FROM python:3.13-slim

WORKDIR /app

# Copy virtual environment and application
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
