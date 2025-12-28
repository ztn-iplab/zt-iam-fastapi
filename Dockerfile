# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (e.g., for psycopg2, mail, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    libssl-dev \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Optional: If you want to use gunicorn for prod
RUN pip install gunicorn

# Expose API port
EXPOSE 8000

# Default command: can be overridden in docker-compose
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "fastapi_app:app"]
