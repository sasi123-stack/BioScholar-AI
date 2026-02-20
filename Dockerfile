FROM python:3.11

# Set up environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860 \
    HOME=/home/user

# Create user
RUN useradd -m -u 1000 user
WORKDIR $HOME/app

# Install system dependencies (including potential DB clients)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY --chown=user . .

# Ensure entrypoint is executable
RUN chmod +x entrypoint.sh

# Change to user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Expose port (HF looks for 7860)
EXPOSE 7860

# Run both Backend and Bot
CMD ["./entrypoint.sh"]
