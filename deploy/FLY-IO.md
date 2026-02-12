# Deploy Nexus to Fly.io - FREE! 🆓

Deploy Nexus Assistant to Fly.io's generous free tier in under 5 minutes.

---

## ✨ Free Tier Includes

- **3 shared VMs** with 256MB RAM each
- **3GB persistent storage** for your data
- **160GB bandwidth** per month
- **Global edge deployment** - runs close to you
- **Automatic SSL/HTTPS** certificates
- **Zero cost** - completely free!

---

## 🚀 Two Ways to Deploy

### Option 1: Automated Script (Easiest)

```bash
# One command deployment
./deploy-flyio.sh
```

The script will:
1. ✅ Install Fly CLI (if needed)
2. ✅ Login to Fly.io
3. ✅ Create your app
4. ✅ Set up API keys
5. ✅ Create persistent storage
6. ✅ Deploy Nexus
7. ✅ Give you the URL

**Total time: ~3 minutes**

---

### Option 2: Manual Deployment

#### Step 1: Install Fly CLI

```bash
curl -L https://fly.io/install.sh | sh
export PATH="$HOME/.fly/bin:$PATH"
```

#### Step 2: Login

```bash
flyctl auth login
```

This opens your browser for authentication.

#### Step 3: Launch App

```bash
flyctl launch --now
```

Follow the prompts:
- **App name?** Press Enter for auto-generated name
- **Region?** Choose closest to you (or press Enter for `iad`)
- **PostgreSQL?** No
- **Redis?** No

#### Step 4: Create Storage Volume

```bash
flyctl volumes create nexus_data --size 1 --region iad
```

#### Step 5: Set API Keys (Optional)

```bash
# Add your API keys as secrets
flyctl secrets set ANTHROPIC_API_KEY=sk-ant-your-key-here
flyctl secrets set OPENAI_API_KEY=sk-your-key-here
flyctl secrets set GEMINI_API_KEY=your-key-here
```

#### Step 6: Deploy

```bash
flyctl deploy
```

---

## 📱 Using Your Deployed App

### Check Status

```bash
flyctl status
```

Output:
```
Name    = nexus-assistant
Status  = deployed
...
```

### View Logs

```bash
flyctl logs
```

Or follow logs in real-time:
```bash
flyctl logs -f
```

### SSH Into Your App

```bash
flyctl ssh console
```

Once inside:
```bash
# Check if Nexus is running
ps aux | grep nexus

# View local logs
tail -f /data/.nexus/nexus.log

# Activate environment and test
source /app/venv/bin/activate
nexus --version
```

### Access the Terminal

Since Nexus runs as a daemon, connect via SSH:

```bash
flyctl ssh console
source /app/venv/bin/activate
nexus
```

---

## 🔧 Configuration

### Update Environment Variables

```bash
# Set variables
flyctl secrets set NEXUS_LOG_LEVEL=DEBUG
flyctl secrets set NEXUS_DEFAULT_PROVIDER=claude

# List all secrets
flyctl secrets list
```

### Change Region

```bash
# See available regions
flyctl regions list

# Add a region
flyctl regions add sea

# Remove a region
flyctl regions remove iad
```

### Scale Resources (If Needed)

**Free tier:** 256MB RAM (usually enough)

**Upgrade if needed:**
```bash
# Upgrade to 512MB (may incur small cost)
flyctl scale memory 512

# Check pricing first
flyctl pricing
```

---

## 📊 Monitoring

### View Resource Usage

```bash
# App metrics
flyctl dashboard metrics

# VM status
flyctl status --all
```

### Health Checks

Fly.io automatically monitors your app health based on `fly.toml`:

```toml
[checks.nexus_alive]
  grace_period = "10s"
  interval = "30s"
  timeout = "5s"
```

---

## 💾 Data Persistence

Your Nexus data is stored in a **persistent volume** at `/data/.nexus`:

- ✅ **Survives restarts** - Data persists across deploys
- ✅ **Backed up automatically** - Fly.io snapshots
- ✅ **1GB storage** - Enough for thousands of sessions

### Backup Your Data

```bash
# SSH in and create backup
flyctl ssh console

# Inside the container:
cd /data
tar -czf nexus-backup.tar.gz .nexus

# Exit and copy to local
exit

# From your local machine:
flyctl ssh sftp get /data/nexus-backup.tar.gz
```

### Restore Data

```bash
# Copy backup to app
flyctl ssh sftp put nexus-backup.tar.gz /data/

# SSH in and extract
flyctl ssh console
cd /data
tar -xzf nexus-backup.tar.gz
```

---

## 🐛 Troubleshooting

### App Won't Start

```bash
# Check logs for errors
flyctl logs

# Common issues:
# - Missing secrets (API keys)
# - Volume not mounted
# - Dockerfile build errors

# Verify volume
flyctl volumes list

# Recreate volume if needed
flyctl volumes create nexus_data --size 1
```

### Out of Memory

```bash
# Check current allocation
flyctl status

# If free tier is too small, upgrade:
flyctl scale memory 512  # $2-3/month
```

### Can't Connect

```bash
# Verify app is running
flyctl status

# Test health check
curl https://your-app.fly.dev

# Restart if needed
flyctl restart
```

### Slow Performance

Free tier uses **shared CPUs**. For better performance:

```bash
# Upgrade to dedicated CPU (incurs cost)
flyctl scale vm dedicated-cpu-1x
```

---

## 💰 Staying in Free Tier

**To stay FREE forever:**

1. ✅ Use shared VMs (default)
2. ✅ Keep memory at 256MB
3. ✅ Use ≤ 3GB storage
4. ✅ Stay under 160GB/month bandwidth
5. ✅ Run 1-3 small apps

**What costs extra:**
- ❌ Dedicated CPUs
- ❌ More than 256MB RAM
- ❌ Storage over 3GB
- ❌ Bandwidth over 160GB/month
- ❌ IPv4 addresses ($2/month)

---

## 🔄 Updates & Redeploys

### Update Nexus Code

```bash
# Pull latest code
git pull origin main

# Redeploy
flyctl deploy
```

### Auto-Deploy on Git Push

Set up GitHub Actions:

```yaml
# .github/workflows/fly-deploy.yml
name: Deploy to Fly.io

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

Get token: `flyctl auth token`

---

## 🎯 Next Steps

1. ✅ Deploy with `./deploy-flyio.sh`
2. ✅ Add your API keys
3. ✅ SSH in and test: `flyctl ssh console`
4. ✅ Monitor logs: `flyctl logs -f`
5. ✅ Use Nexus: Connect and start chatting!

---

## 📚 Resources

- 🌐 [Fly.io Docs](https://fly.io/docs/)
- 💬 [Fly.io Community](https://community.fly.io/)
- 📖 [Fly.io Pricing](https://fly.io/pricing)
- 🐛 [Report Issues](https://github.com/carafael/short/issues)

---

## 🎉 You're Done!

Your Nexus Assistant is now running on Fly.io's free tier!

**App URL:** `https://your-app.fly.dev`

**Connect:** `flyctl ssh console`

**Free forever!** 🆓

---

Need help? Check the main [DEPLOYMENT.md](DEPLOYMENT.md) or open an issue!
