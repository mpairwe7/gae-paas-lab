FROM python:3.13-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (layer caching)
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ .

# Non-root user for security
RUN adduser --disabled-password --no-create-home appuser
USER appuser

EXPOSE ${PORT:-7860}

# Railway sets PORT dynamically; fall back to 7860 for local dev
CMD gunicorn -b 0.0.0.0:${PORT:-7860} main:app --workers 2 --threads 4 --timeout 120
