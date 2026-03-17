FROM python:3.11-slim

# Set up environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860 \
    HOME=/home/user \
    OLLAMA_HOST=127.0.0.1:11434

# Create user
RUN useradd -m -u 1000 user
WORKDIR $HOME/app

# Install system dependencies (minimal - no chromium, no nodejs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama binary directly (no systemd service registration)
RUN curl -L https://ollama.com/download/ollama-linux-amd64 -o /usr/local/bin/ollama \
    && chmod +x /usr/local/bin/ollama

# Copy slim requirements and install
COPY --chown=user requirements_bot.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements_bot.txt

# Copy the rest of the application
COPY --chown=user . .

# Ensure entrypoint is executable
RUN chmod +x entrypoint.sh

# Change to user
USER user
ENV PATH="/home/user/.local/bin:/usr/local/bin:$PATH"

# Expose port (HF looks for 7860)
EXPOSE 7860

# Run following the entrypoint configuration
CMD ["./entrypoint.sh"]
