# Multi-stage build for PersonaSay Backend
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies (production only)
COPY config/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Note: requirements-dev.txt is NOT installed in production

# Final stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder (system-wide installation)
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs

# Create non-root user for security
RUN useradd -m -u 1000 personasay && \
    chown -R personasay:personasay /app

USER personasay

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run the application with production settings
# Using single process for better stability (adjust workers via env if needed)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--timeout-keep-alive", "75"]

