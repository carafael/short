# Nexus Assistant - Deployment Guide

Complete guide for deploying Nexus Assistant on various cloud platforms.

---

## Table of Contents

1. [AWS Deployment](#aws-deployment)
2. [DigitalOcean](#digitalocean)
3. [Railway.app](#railway-app)
4. [Fly.io](#fly-io)
5. [Google Cloud Platform](#google-cloud-platform)
6. [Azure](#azure)
7. [Self-Hosted (VPS)](#self-hosted-vps)
8. [Docker Deployment](#docker-deployment)

---

## AWS Deployment

### Option 1: EC2 (Recommended)

**Best for:** Long-running terminal, full control

#### Quick Launch

```bash
# 1. Launch EC2 instance
#    - Instance Type: t3.micro (free tier) or t3.small
#    - AMI: Ubuntu 22.04 LTS
#    - Storage: 20GB gp3
#    - Security Group: SSH (22)

# 2. Use provided user data script
# Copy contents of deploy/aws-ec2-userdata.sh to User Data field

# 3. SSH into instance
ssh ubuntu@<instance-ip>

# 4. Edit API keys
sudo nano /home/nexus/nexus-assistant/.env

# 5. Restart service
sudo systemctl restart nexus
```

**Cost:** ~$7-15/month (t3.micro free tier eligible)

### Option 2: Lightsail

**Best for:** Simplest setup, predictable pricing

```bash
# 1. Create Lightsail instance ($3.50/month plan)
# 2. SSH in and run:
git clone https://github.com/carafael/short.git
cd short
./install.sh

# 3. Install as systemd service
sudo cp deploy/nexus.service /etc/systemd/system/
sudo sed -i "s/%USER%/$USER/g" /etc/systemd/system/nexus.service
sudo sed -i "s|%INSTALL_DIR%|$(pwd)|g" /etc/systemd/system/nexus.service
sudo systemctl daemon-reload
sudo systemctl enable nexus
sudo systemctl start nexus
```

**Cost:** $3.50-10/month

### Option 3: ECS Fargate

**Best for:** Scalable, managed containers

```bash
# 1. Build and push Docker image
docker build -t nexus-assistant -f deploy/Dockerfile .
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag nexus-assistant:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/nexus:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/nexus:latest

# 2. Create ECS task definition and service
# Use AWS Console or CloudFormation
```

**Cost:** ~$12-25/month (0.25 vCPU, 0.5GB memory)

---

## DigitalOcean

**Best for:** Simple VPS with great UX

```bash
# 1. Create Droplet
#    - Image: Ubuntu 22.04
#    - Plan: Basic $6/month
#    - Datacenter: Closest to you

# 2. SSH and install
ssh root@<droplet-ip>
git clone https://github.com/carafael/short.git /opt/nexus
cd /opt/nexus
./install.sh

# 3. Setup systemd
cp deploy/nexus.service /etc/systemd/system/
sed -i "s/%USER%/root/g" /etc/systemd/system/nexus.service
sed -i "s|%INSTALL_DIR%|/opt/nexus|g" /etc/systemd/system/nexus.service
systemctl daemon-reload
systemctl enable nexus
systemctl start nexus

# 4. Check status
systemctl status nexus
journalctl -u nexus -f
```

**Cost:** $6-12/month

---

## Railway.app

**Best for:** Dead simple deployment, great for developers

### Method 1: From GitHub

1. Push code to GitHub
2. Go to [railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub"
4. Select your repository
5. Add environment variables from `.env`
6. Deploy!

### Method 2: CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
cd /path/to/short
railway init

# Add environment variables
railway variables set ANTHROPIC_API_KEY=your_key_here

# Deploy
railway up
```

**Cost:** $5/month starter plan, scales with usage

---

## Fly.io

**Best for:** Global edge deployment, great free tier

```bash
# 1. Install flyctl
curl -L https://fly.io/install.sh | sh

# 2. Login
flyctl auth login

# 3. Launch app
cd /path/to/short
flyctl launch --name nexus-assistant

# 4. Set secrets
flyctl secrets set ANTHROPIC_API_KEY=your_key_here
flyctl secrets set OPENAI_API_KEY=your_key_here

# 5. Deploy
flyctl deploy

# 6. Connect via SSH
flyctl ssh console
```

**fly.toml** configuration:

```toml
app = "nexus-assistant"
primary_region = "iad"

[build]
  dockerfile = "deploy/Dockerfile"

[env]
  NEXUS_DATA_DIR = "/data/.nexus"

[[mounts]]
  source = "nexus_data"
  destination = "/data"
  initial_size = "1gb"

[[services]]
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    port = 80
```

**Cost:** Free tier available (3 shared CPUs, 256MB RAM)

---

## Google Cloud Platform

### Cloud Run (Serverless)

```bash
# 1. Build and deploy
gcloud run deploy nexus-assistant \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi

# 2. Set environment variables
gcloud run services update nexus-assistant \
  --set-env-vars ANTHROPIC_API_KEY=your_key
```

**Cost:** Pay per request, ~$5-10/month for light usage

### Compute Engine (VM)

```bash
# Similar to AWS EC2, use the aws-ec2-userdata.sh script
# adapted for Debian/Ubuntu on GCP
```

**Cost:** ~$5-15/month (f1-micro free tier eligible)

---

## Azure

### Container Instances

```bash
# 1. Create resource group
az group create --name nexus-rg --location eastus

# 2. Build and push to ACR
az acr create --resource-group nexus-rg --name nexusacr --sku Basic
az acr build --registry nexusacr --image nexus:latest -f deploy/Dockerfile .

# 3. Deploy container
az container create \
  --resource-group nexus-rg \
  --name nexus-assistant \
  --image nexusacr.azurecr.io/nexus:latest \
  --cpu 1 --memory 0.5 \
  --environment-variables \
    ANTHROPIC_API_KEY=your_key
```

**Cost:** ~$10-20/month

---

## Self-Hosted (VPS)

**Works on:** Linode, Vultr, Hetzner, OVH, or any Linux server

```bash
# 1. Install on any Ubuntu/Debian server
ssh user@your-server
git clone https://github.com/carafael/short.git /opt/nexus
cd /opt/nexus
./install.sh

# 2. Setup systemd service
sudo cp deploy/nexus.service /etc/systemd/system/
sudo sed -i "s/%USER%/$USER/g" /etc/systemd/system/nexus.service
sudo sed -i "s|%INSTALL_DIR%|/opt/nexus|g" /etc/systemd/system/nexus.service
sudo systemctl daemon-reload
sudo systemctl enable nexus
sudo systemctl start nexus

# 3. Access via tmux
tmux attach -t nexus
```

**Cost:** $3-10/month (provider dependent)

---

## Docker Deployment

### Using Docker Compose

```bash
# 1. Clone repository
git clone https://github.com/carafael/short.git
cd short

# 2. Copy and edit .env
cp .env.example .env
nano .env

# 3. Start with Docker Compose
docker-compose -f deploy/docker-compose.yml up -d

# 4. View logs
docker logs -f nexus-assistant

# 5. Access container
docker exec -it nexus-assistant bash
```

### Standalone Docker

```bash
# Build
docker build -t nexus-assistant -f deploy/Dockerfile .

# Run
docker run -d \
  --name nexus \
  --restart unless-stopped \
  -v nexus-data:/root/.nexus \
  --env-file .env \
  nexus-assistant

# Access
docker exec -it nexus bash
```

---

## Post-Deployment Checklist

After deploying to any platform:

- [ ] Edit `.env` and add your API keys
- [ ] Restart the service/container
- [ ] Test basic functionality
- [ ] Configure backups for `~/.nexus` directory
- [ ] Set up monitoring/alerts (optional)
- [ ] Configure automatic updates (optional)

---

## Troubleshooting

### Service won't start

```bash
# Check logs
journalctl -u nexus -n 50 --no-pager

# Check permissions
ls -la /path/to/nexus

# Verify Python version
python3 --version  # Should be 3.11+
```

### API keys not working

```bash
# Verify .env is loaded
systemctl show nexus | grep Environment

# Test manually
source venv/bin/activate
python -c "import os; print(os.getenv('ANTHROPIC_API_KEY'))"
```

### High memory usage

```bash
# Check resource usage
systemctl status nexus
docker stats nexus-assistant

# Adjust limits in systemd or docker-compose.yml
```

---

## Security Best Practices

1. **Never commit API keys** - Use `.env` files
2. **Use SSH keys** - Disable password authentication
3. **Enable firewall** - Only allow necessary ports
4. **Regular updates** - Keep system packages updated
5. **Backups** - Automate `~/.nexus` backups
6. **Monitoring** - Set up alerts for service downtime

---

## Next Steps

- **Configure AI providers**: Edit `.env` with your API keys
- **Customize domains**: Add your own domain knowledge
- **Extend functionality**: Add custom commands
- **Set up backups**: Automate data persistence
- **Monitor usage**: Track API costs and usage

---

## Support

- 🐛 Issues: [GitHub Issues](https://github.com/carafael/short/issues)
- 📖 Documentation: [README.md](../README.md)
- 💬 Discussions: [GitHub Discussions](https://github.com/carafael/short/discussions)
