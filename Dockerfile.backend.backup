
# Use the official Python 3.10 slim image (newer, better support)
FROM python:3.10-slim

# Set up environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860 \
    APP_HOME=/app \
    MODEL_CACHE_DIR=/app/models

WORKDIR $APP_HOME

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create the user carefully
RUN useradd -m -u 1000 user

# Switch to directory ownership
RUN chown -R user:user $APP_HOME

# Install python dependencies as user (best practice)
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Copy requirements First (Cache optimization)
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir uvicorn

# Copy application code
COPY --chown=user:user . .

# Create model directory again just to be safe about permissions
RUN mkdir -p $MODEL_CACHE_DIR

# Expose port
EXPOSE 7860

# Simple run command (No gunicorn to reduce complexity for now)
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "2", "--timeout-keep-alive", "300"]
