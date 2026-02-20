# 🌐 Deploying OpenClaw to a VPS

This guide will help you deploy your OpenClaw AI Agent to any VPS (Virtual Private Server).

## 🎯 Recommended VPS Providers

### 1. **Oracle Cloud (FREE Forever)** ⭐ BEST
- **Cost**: FREE (always free tier)
- **Resources**: 4 ARM CPUs + 24GB RAM
- **Setup**: [https://www.oracle.com/cloud/free/](https://www.oracle.com/cloud/free/)
- **Best for**: Long-term hosting

### 2. **Google Cloud Platform**
- **Cost**: $300 free credit (90 days)
- **Resources**: Flexible
- **Setup**: [https://cloud.google.com/free](https://cloud.google.com/free)
- **Best for**: Testing and development

### 3. **DigitalOcean**
- **Cost**: $200 credit (60 days with GitHub Student Pack)
- **Resources**: Starting at $4/month
- **Setup**: [https://www.digitalocean.com/](https://www.digitalocean.com/)
- **Best for**: Simple deployment

### 4. **Linode (Akamai)**
- **Cost**: $100 credit (60 days)
- **Resources**: Starting at $5/month
- **Setup**: [https://www.linode.com/](https://www.linode.com/)
- **Best for**: Reliability

## 🚀 Quick Deployment (Any Ubuntu VPS)

### Step 1: Get a VPS
1. Sign up for any VPS provider above
2. Create an Ubuntu 22.04 LTS instance
3. Note your server's IP address
4. Make sure you can SSH into it

### Step 2: Upload Files
```bash
# On your local machine, upload the deployment script and workspace
scp deploy_vps.sh root@YOUR_VPS_IP:/root/
scp -r workspace root@YOUR_VPS_IP:/root/
```

### Step 3: Run Deployment Script
```bash
# SSH into your VPS
ssh root@YOUR_VPS_IP

# Make the script executable
chmod +x deploy_vps.sh

# Run the deployment
sudo bash deploy_vps.sh
```

### Step 4: Add Your API Key
```bash
# Edit the service file
sudo nano /etc/systemd/system/openclaw.service

# Find this line:
# Environment="OPENROUTER_API_KEY=YOUR_API_KEY_HERE"

# Replace YOUR_API_KEY_HERE with your actual OpenRouter API key
# Save: Ctrl+X, then Y, then Enter
```

### Step 5: Start the Service
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable openclaw

# Start the service
sudo systemctl start openclaw

# Check status
sudo systemctl status openclaw
```

### Step 6: Access Your Agent
Open your browser and go to:
```
http://YOUR_VPS_IP/?token=admin-token-123
```

## 🔐 Adding SSL (HTTPS) - Optional but Recommended

### Prerequisites:
- A domain name pointing to your VPS IP
- Port 80 and 443 open in firewall

### Install Certbot:
```bash
sudo apt-get install certbot python3-certbot-nginx -y
```

### Get SSL Certificate:
```bash
# Replace example.com with your domain
sudo certbot --nginx -d example.com
```

### Auto-renewal:
Certbot automatically sets up renewal. Test it:
```bash
sudo certbot renew --dry-run
```

## 📊 Monitoring & Management

### View Logs:
```bash
# Real-time logs
sudo journalctl -u openclaw -f

# Last 100 lines
sudo journalctl -u openclaw -n 100
```

### Restart Service:
```bash
sudo systemctl restart openclaw
```

### Stop Service:
```bash
sudo systemctl stop openclaw
```

### Update OpenClaw:
```bash
# Update to latest version
sudo npm update -g openclaw

# Restart service
sudo systemctl restart openclaw
```

## 🔧 Troubleshooting

### Service won't start:
```bash
# Check logs
sudo journalctl -u openclaw -n 50

# Check if port is in use
sudo netstat -tulpn | grep 7860

# Verify OpenClaw is installed
openclaw --version
```

### Can't access from browser:
```bash
# Check firewall
sudo ufw status

# Check nginx
sudo systemctl status nginx
sudo nginx -t

# Check if OpenClaw is listening
sudo netstat -tulpn | grep 7860
```

### Agent not responding:
1. Verify API key is set correctly in `/etc/systemd/system/openclaw.service`
2. Restart the service: `sudo systemctl restart openclaw`
3. Check logs: `sudo journalctl -u openclaw -f`

## 💰 Cost Comparison

| Provider | Free Tier | After Free Tier | Best For |
|----------|-----------|-----------------|----------|
| Oracle Cloud | Always free (4 ARM CPUs, 24GB RAM) | FREE | Long-term hosting |
| Google Cloud | $300 credit (90 days) | ~$10-30/month | Testing |
| DigitalOcean | $200 credit (60 days) | $4-12/month | Simplicity |
| Linode | $100 credit (60 days) | $5-12/month | Reliability |

## 🎯 Recommended Setup

**For production use:**
- **Provider**: Oracle Cloud (free forever)
- **Instance**: ARM-based (4 CPUs, 24GB RAM)
- **OS**: Ubuntu 22.04 LTS
- **SSL**: Yes (using Let's Encrypt)
- **Domain**: Yes (for professional look)

**For testing:**
- **Provider**: Google Cloud (generous free credits)
- **Instance**: e2-micro (2 vCPUs, 1GB RAM)
- **OS**: Ubuntu 22.04 LTS
- **SSL**: Optional
- **Domain**: Optional

## 📚 Additional Resources

- [OpenClaw Documentation](https://docs.openclaw.ai)
- [Oracle Cloud Free Tier Guide](https://www.oracle.com/cloud/free/)
- [DigitalOcean Tutorials](https://www.digitalocean.com/community/tutorials)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

## 🆘 Need Help?

If you encounter issues:
1. Check the logs: `sudo journalctl -u openclaw -f`
2. Verify your API key is correct
3. Make sure ports 80, 443, and 7860 are open
4. Check that OpenClaw is installed: `openclaw --version`

---

**Made with ❤️ for easy OpenClaw deployment**
