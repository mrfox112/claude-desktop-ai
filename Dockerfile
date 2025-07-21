# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    tkinter \
    python3-tk \
    xvfb \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements*.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install optional dependencies if available
RUN pip install --no-cache-dir -r requirements-optional.txt || true

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p logs data backups

# Set environment variables
ENV PYTHONPATH=/app
ENV DISPLAY=:99

# Create non-root user for security
RUN useradd -m -u 1000 etheruser && chown -R etheruser:etheruser /app
USER etheruser

# Expose port for future web interface
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sqlite3; conn = sqlite3.connect('conversations.db'); conn.close()" || exit 1

# Default command
CMD ["python", "claude_desktop.py"]
