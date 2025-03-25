FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir uv && \
    uv pip install --system -e .

# Copy project
COPY . .


ENV PYTHONUNBUFFERED=1
EXPOSE 8000
ENV PYTHONPATH=/app:$PYTHONPATH

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Run as non-root user
RUN useradd -m appuser
USER appuser

ENTRYPOINT ["/entrypoint.sh"]