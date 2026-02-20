# 🌐 Deploy OpenClaw to Oracle Cloud (FREE Forever)

This guide will walk you through deploying OpenClaw AI Agent to Oracle Cloud's **Always Free Tier** - giving you **4 ARM CPUs + 24GB RAM** completely free, forever.

## 🎯 Why Oracle Cloud?

- ✅ **Always Free** - No credit card expiry, truly free forever
- ✅ **Powerful** - 4 ARM CPUs + 24GB RAM (better than most paid tiers)
- ✅ **Reliable** - Enterprise-grade infrastructure
- ✅ **No Limits** - No time limits, no usage caps on free tier

---

## 📋 Step 1: Create Oracle Cloud Account

1. **Go to Oracle Cloud Free Tier**:
   - Visit: [https://www.oracle.com/cloud/free/](https://www.oracle.com/cloud/free/)
   - Click **"Start for free"**

2. **Sign Up**:
   - Enter your email and country
   - Create a password
   - **Note**: You'll need a credit card for verification, but you won't be charged

3. **Verify Your Account**:
   - Check your email for verification link
   - Complete phone verification

4. **Wait for Approval**:
   - Usually takes 5-30 minutes
   - You'll get an email when your account is ready

---

## 🖥️ Step 2: Create a VM Instance

### 2.1 Navigate to Compute Instances
1. Log in to [cloud.oracle.com](https://cloud.oracle.com)
2. Click **☰ Menu** (top left)
3. Go to **Compute** → **Instances**
4. Click **"Create Instance"**

### 2.2 Configure Instance

**Name**: `openclaw-agent`

**Placement**:
- Leave default (it will auto-select an availability domain)

**Image and Shape**:
1. Click **"Change Image"**
   - Select: **Ubuntu 22.04**
   - Click **"Select Image"**

2. Click **"Change Shape"**
   - Select: **Ampere** (ARM-based)
   - Choose: **VM.Standard.A1.Flex**
   - Set OCPUs: **4** (maximum free tier)
   - Set Memory: **24 GB** (maximum free tier)
   - Click **"Select Shape"**

**Networking**:
- Create new VCN: ✅ (leave checked)
- Assign public IP: ✅ (leave checked)

**Add SSH Keys**:
- **Option A**: Generate new key pair
  - Click **"Generate a key pair for me"**
  - Click **"Save Private Key"** (save as `openclaw-key.pem`)
  - Click **"Save Public Key"** (optional)

- **Option B**: Use existing key
  - If you have an SSH key, paste the public key

**Boot Volume**:
- Size: **50 GB** (free tier allows up to 200 GB)

### 2.3 Create Instance
- Click **"Create"**
- Wait 2-3 minutes for provisioning
- **Copy the Public IP address** when it appears

---

## 🔐 Step 3: Configure Firewall (Security List)

### 3.1 Open Required Ports
1. On the instance details page, click your **VCN name** (under "Primary VNIC")
2. Click **"Security Lists"** on the left
3. Click your security list (usually named "Default Security List")
4. Click **"Add Ingress Rules"**

**Add these rules one by one:**

**Rule 1: HTTP (Port 80)**
- Source CIDR: `0.0.0.0/0`
- IP Protocol: `TCP`
- Destination Port Range: `80`
- Click **"Add Ingress Rules"**

**Rule 2: HTTPS (Port 443)**
- Source CIDR: `0.0.0.0/0`
- IP Protocol: `TCP`
- Destination Port Range: `443`
- Click **"Add Ingress Rules"**

---

## 💻 Step 4: Connect to Your Instance

### 4.1 Windows (Using PowerShell)
```powershell
# Navigate to where you saved the key
cd C:\Users\YOUR_USERNAME\Downloads

# Set correct permissions (if needed)
icacls openclaw-key.pem /inheritance:r
icacls openclaw-key.pem /grant:r "%username%:R"

# Connect via SSH
ssh -i openclaw-key.pem ubuntu@YOUR_PUBLIC_IP
```

### 4.2 Mac/Linux
```bash
# Navigate to where you saved the key
cd ~/Downloads

# Set correct permissions
chmod 400 openclaw-key.pem

# Connect via SSH
ssh -i openclaw-key.pem ubuntu@YOUR_PUBLIC_IP
```

**First time connecting?**
- Type `yes` when asked about authenticity
- You should now see: `ubuntu@openclaw-agent:~$`

---

## 🚀 Step 5: Deploy OpenClaw

### 5.1 Upload Deployment Files

**From your local machine** (new terminal/PowerShell window):

```bash
# Upload deployment script
scp -i openclaw-key.pem deploy_vps.sh ubuntu@YOUR_PUBLIC_IP:/home/ubuntu/

# Upload workspace folder
scp -i openclaw-key.pem -r workspace ubuntu@YOUR_PUBLIC_IP:/home/ubuntu/
```

### 5.2 Run Deployment Script

**Back in your SSH session**:

```bash
# Make script executable
chmod +x deploy_vps.sh

# Run deployment (this takes 5-10 minutes)
sudo bash deploy_vps.sh
```

**What the script does:**
- ✅ Updates Ubuntu
- ✅ Installs Node.js 24
- ✅ Installs OpenClaw
- ✅ Sets up systemd service
- ✅ Configures Nginx reverse proxy
- ✅ Sets up firewall

### 5.3 Add Your OpenRouter API Key

```bash
# Edit the service file
sudo nano /etc/systemd/system/openclaw.service
```

**Find this line:**
```
Environment="OPENROUTER_API_KEY=YOUR_API_KEY_HERE"
```

**Replace `YOUR_API_KEY_HERE` with your actual OpenRouter API key**

**Save and exit:**
- Press `Ctrl + X`
- Press `Y`
- Press `Enter`

### 5.4 Start OpenClaw Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable openclaw

# Start the service
sudo systemctl start openclaw

# Check status (should show "active (running)")
sudo systemctl status openclaw
```

**Expected output:**
```
● openclaw.service - OpenClaw AI Agent Gateway
   Loaded: loaded (/etc/systemd/system/openclaw.service; enabled)
   Active: active (running) since ...
```

Press `q` to exit the status view.

---

## 🌐 Step 6: Configure Ubuntu Firewall

Oracle Cloud has TWO firewalls - we configured the cloud firewall, now configure Ubuntu's:

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw --force enable

# Check status
sudo ufw status
```

---

## ✅ Step 7: Access Your Agent

Open your browser and go to:
```
http://YOUR_PUBLIC_IP/?token=admin-token-123
```

**You should see the OpenClaw chat interface!**

Type "hello" and the agent should respond using Llama 3.3 70B.

---

## 🔐 Step 8: Add SSL (HTTPS) - Optional

### Prerequisites:
- A domain name (e.g., from [Freenom](https://www.freenom.com) - free)
- Domain's A record pointing to your Oracle Cloud IP

### Install Certbot:
```bash
sudo apt-get install certbot python3-certbot-nginx -y
```

### Get SSL Certificate:
```bash
# Replace yourdomain.com with your actual domain
sudo certbot --nginx -d yourdomain.com
```

**Follow the prompts:**
- Enter your email
- Agree to terms
- Choose whether to redirect HTTP to HTTPS (recommended: Yes)

**Your agent will now be accessible at:**
```
https://yourdomain.com/?token=admin-token-123
```

---

## 📊 Monitoring & Management

### View Real-time Logs:
```bash
sudo journalctl -u openclaw -f
```

### Restart Service:
```bash
sudo systemctl restart openclaw
```

### Check Service Status:
```bash
sudo systemctl status openclaw
```

### View Last 100 Log Lines:
```bash
sudo journalctl -u openclaw -n 100
```

### Update OpenClaw:
```bash
sudo npm update -g openclaw
sudo systemctl restart openclaw
```

---

## 🔧 Troubleshooting

### Can't connect via SSH?
1. Check your security list has port 22 open
2. Verify you're using the correct private key
3. Make sure you're using `ubuntu` as username (not `root`)

### Can't access the web interface?
1. Check service is running: `sudo systemctl status openclaw`
2. Check nginx is running: `sudo systemctl status nginx`
3. Verify firewall rules: `sudo ufw status`
4. Check Oracle Cloud security list has ports 80/443 open

### Agent not responding?
1. Check API key is correct: `sudo nano /etc/systemd/system/openclaw.service`
2. View logs: `sudo journalctl -u openclaw -f`
3. Restart service: `sudo systemctl restart openclaw`

### Service keeps crashing?
```bash
# View detailed error logs
sudo journalctl -u openclaw -n 200

# Check if port 7860 is already in use
sudo netstat -tulpn | grep 7860

# Verify OpenClaw is installed
openclaw --version
```

---

## 💡 Pro Tips

### 1. Set Up Automatic Backups
```bash
# Create backup script
sudo nano /usr/local/bin/backup-openclaw.sh
```

Add:
```bash
#!/bin/bash
tar -czf /home/ubuntu/openclaw-backup-$(date +%Y%m%d).tar.gz /home/openclaw/.openclaw
```

Make executable:
```bash
sudo chmod +x /usr/local/bin/backup-openclaw.sh
```

### 2. Monitor Resource Usage
```bash
# Install htop
sudo apt-get install htop -y

# Run htop
htop
```

### 3. Set Up Email Alerts (Optional)
```bash
# Install mailutils
sudo apt-get install mailutils -y

# Configure systemd to email on failure
sudo systemctl edit openclaw.service
```

Add:
```
[Unit]
OnFailure=status-email@%n.service
```

---

## 📈 Performance Optimization

### Enable HTTP/2 in Nginx:
```bash
sudo nano /etc/nginx/sites-available/openclaw
```

Change `listen 80;` to:
```nginx
listen 80;
listen [::]:80;
http2 on;
```

Restart nginx:
```bash
sudo systemctl restart nginx
```

### Enable Gzip Compression:
```bash
sudo nano /etc/nginx/nginx.conf
```

Uncomment these lines:
```nginx
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;
```

---

## 🎉 Success Checklist

- ✅ Oracle Cloud account created
- ✅ VM instance running (4 CPUs, 24GB RAM)
- ✅ SSH connection working
- ✅ OpenClaw deployed and running
- ✅ OpenRouter API key configured
- ✅ Firewall configured (both cloud and Ubuntu)
- ✅ Agent accessible via browser
- ✅ Agent responding to messages
- ✅ (Optional) SSL certificate installed
- ✅ (Optional) Custom domain configured

---

## 🆘 Need Help?

**Common Issues:**
1. **"Connection refused"** → Check firewalls (both Oracle and Ubuntu)
2. **"Agent not responding"** → Verify API key is set correctly
3. **"Service failed to start"** → Check logs: `sudo journalctl -u openclaw -n 50`

**Still stuck?**
- Check the logs: `sudo journalctl -u openclaw -f`
- Verify all steps were completed
- Make sure you're using Ubuntu 22.04 (not other versions)

---

**🎊 Congratulations! Your OpenClaw AI Agent is now running on Oracle Cloud's free tier with 4 CPUs and 24GB RAM!**

**Access your agent at:** `http://YOUR_PUBLIC_IP/?token=admin-token-123`
