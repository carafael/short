FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app/

# Run installation script
RUN chmod +x install.sh && ./install.sh

# Create data directory
RUN mkdir -p /root/.nexus

# Set environment variable
ENV PATH="/app/venv/bin:$PATH"

# Expose any necessary ports (if adding web interface later)
# EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD pgrep -f nexus || exit 1

# Run Nexus in forever mode
CMD ["venv/bin/nexus-daemon", "start", "--max-restarts", "-1"]
