# Multi-stage build for production optimization
# Stage 1: Build stage with Python 3.12
FROM python:3.12-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.12-slim as runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DJANGO_SETTINGS_MODULE=fayvad_rentals.settings
ENV PATH="/opt/venv/bin:$PATH"

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create app user for security
RUN groupadd -r app && useradd --no-log-init -r -g app app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set work directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R app:app /app

# Copy project files
COPY --chown=app:app . .

# Collect static files (run as app user)
USER app
RUN python manage.py collectstatic --noinput --clear

# Switch back to root for health check
USER root

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Switch to app user for runtime
USER app

# Run the application with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "fayvad_rentals.wsgi:application"]

# Development target (optional)
FROM runtime as development

# Switch to root for development
USER root

# Install development tools
RUN apt-get update && apt-get install -y \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Switch back to app user
USER app

# Run development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Production target (default)
FROM runtime as production
