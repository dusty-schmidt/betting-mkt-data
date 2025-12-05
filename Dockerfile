# Placeholder Dockerfile for the betting‑markets project
# Add your base image, dependencies, and entrypoint here.

FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install uv && uv sync
CMD ["python", "run.py"]
