# Use a multi-stage build for smaller final image
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
# Install dependencies into a virtual environment
RUN uv sync --frozen --no-dev

FROM python:3.12-slim
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY . /app

# Create directories for volumes
RUN mkdir -p /app/data /app/logs

# Expose port
EXPOSE 5000

# Define volumes
VOLUME ["/app/data", "/app/logs"]

# Set environment variables for persistence
ENV DB_PATH="/app/data/betting_markets.db"
ENV LOG_DIR="/app/logs"

# Run the application
CMD ["python", "run.py"]
