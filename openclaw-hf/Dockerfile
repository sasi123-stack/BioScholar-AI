FROM node:24-slim

# Set environment variables
ENV HOME=/home/node
ENV OPENCLAW_HOME=/home/node/.openclaw
ENV OPENCLAW_GATEWAY_PORT=7860
ENV OPENCLAW_GATEWAY_BIND=0.0.0.0
ENV NODE_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
  procps \
  git \
  python3 \
  make \
  g++ \
  cmake \
  && rm -rf /var/lib/apt/lists/*

# Switch to node user before installing
USER node
WORKDIR /home/node

# Install OpenClaw locally in this folder
RUN npm install openclaw

# Create necessary directories
RUN mkdir -p $OPENCLAW_HOME/workspace

# Copy workspace files from the build context
COPY --chown=node:node workspace $OPENCLAW_HOME/workspace

# Create a streamlined openclaw.json for Cloud environment
# Note: API key will be provided via environment variable at runtime
RUN echo '{\
  "meta": {\
  "lastTouchedVersion": "2026.2.15"\
  },\
  "agents": {\
  "defaults": {\
  "model": {\
  "primary": "meta-llama/llama-4-maverick-17b-128e-instruct"\
  },\
  "workspace": "/home/node/.openclaw/workspace"\
  }\
  },\
  "gateway": {\
  "port": 7860,\
  "mode": "cloud",\
  "bind": "any",\
  "auth": {\
  "mode": "token",\
  "token": "admin-token-123"\
  }\
  },\
  "platforms": {\
  "telegram": {\
  "enabled": true,\
  "token": "${process.env.TELEGRAM_BOT_TOKEN}"\
  }\
  }\
  }' > $OPENCLAW_HOME/openclaw.json

# Expose the Hugging Face port
EXPOSE 7860

# Set working directory to OpenClaw home
WORKDIR $OPENCLAW_HOME

# Start the gateway
# Secrets needed: GROQ_API_KEY, TELEGRAM_BOT_TOKEN
CMD ["npx", "openclaw", "gateway"]