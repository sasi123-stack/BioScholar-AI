#!/bin/bash
# OpenClaw VPS Deployment Script
# Works on Ubuntu 20.04+ / Debian 11+

set -e

echo "🦞 OpenClaw VPS Deployment Script"
echo "=================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use: sudo bash deploy_vps.sh)"
    exit 1
fi

# Update system
echo "1️⃣  Updating system packages..."
apt-get update
apt-get upgrade -y

# Install Node.js 24
echo "2️⃣  Installing Node.js 24..."
curl -fsSL https://deb.nodesource.com/setup_24.x | bash -
apt-get install -y nodejs

# Verify Node installation
node --version
npm --version

# Install OpenClaw globally
echo "3️⃣  Installing OpenClaw..."
npm install -g openclaw

# Create openclaw user (non-root for security)
echo "4️⃣  Creating openclaw user..."
if ! id "openclaw" &>/dev/null; then
    useradd -m -s /bin/bash openclaw
fi

# Setup OpenClaw home directory
echo "5️⃣  Setting up OpenClaw workspace..."
OPENCLAW_HOME="/home/openclaw/.openclaw"
mkdir -p $OPENCLAW_HOME/workspace
mkdir -p $OPENCLAW_HOME/agents/main/agent

# Copy workspace files (if they exist)
if [ -d "./workspace" ]; then
    cp -r ./workspace/* $OPENCLAW_HOME/workspace/
    echo "   ✅ Workspace files copied"
else
    echo "   ⚠️  No workspace directory found, using defaults"
fi

# Create auth-profiles.json for OpenRouter
echo "6️⃣  Configuring OpenRouter authentication..."
cat > $OPENCLAW_HOME/agents/main/agent/auth-profiles.json <<EOF
{
  "openrouter:default": {
    "provider": "openrouter",
    "mode": "api_key"
  }
}
EOF

# Create openclaw.json configuration
echo "7️⃣  Creating OpenClaw configuration..."
cat > $OPENCLAW_HOME/openclaw.json <<EOF
{
  "meta": {
    "lastTouchedVersion": "2026.2.15"
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "openrouter/meta-llama/llama-3.3-70b-instruct"
      },
      "workspace": "$OPENCLAW_HOME/workspace"
    }
  },
  "gateway": {
    "port": 7860,
    "mode": "local",
    "bind": "lan",
    "auth": {
      "mode": "token",
      "token": "admin-token-123"
    }
  }
}
EOF

# Set proper permissions
chown -R openclaw:openclaw /home/openclaw/.openclaw

# Create systemd service
echo "8️⃣  Creating systemd service..."
cat > /etc/systemd/system/openclaw.service <<EOF
[Unit]
Description=OpenClaw AI Agent Gateway
After=network.target

[Service]
Type=simple
User=openclaw
WorkingDirectory=/home/openclaw
Environment="OPENCLAW_HOME=/home/openclaw/.openclaw"
Environment="OPENROUTER_API_KEY=YOUR_API_KEY_HERE"
ExecStart=/usr/bin/openclaw gateway --port 7860 --bind lan --token admin-token-123
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Install and configure nginx (reverse proxy)
echo "9️⃣  Installing and configuring Nginx..."
apt-get install -y nginx

cat > /etc/nginx/sites-available/openclaw <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/openclaw /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

# Configure firewall
echo "🔥 Configuring firewall..."
apt-get install -y ufw
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo ""
echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit the service file to add your OpenRouter API key:"
echo "   sudo nano /etc/systemd/system/openclaw.service"
echo "   Replace 'YOUR_API_KEY_HERE' with your actual key"
echo ""
echo "2. Start the service:"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable openclaw"
echo "   sudo systemctl start openclaw"
echo ""
echo "3. Check status:"
echo "   sudo systemctl status openclaw"
echo ""
echo "4. View logs:"
echo "   sudo journalctl -u openclaw -f"
echo ""
echo "5. Access your agent at: http://YOUR_VPS_IP/?token=admin-token-123"
echo ""
echo "🔐 To add SSL (HTTPS), install certbot:"
echo "   sudo apt-get install certbot python3-certbot-nginx"
echo "   sudo certbot --nginx"
echo ""
