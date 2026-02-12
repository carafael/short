#!/bin/bash
#
# AWS EC2 User Data Script for Nexus Assistant
# This script runs automatically when an EC2 instance launches
#
# Launch with: AWS Console > EC2 > Launch Instance > Advanced Details > User Data
#

set -e

echo "🚀 Starting Nexus Assistant installation..."

# Update system
apt-get update
apt-get upgrade -y

# Install dependencies
apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    tmux \
    curl \
    build-essential

# Create nexus user
useradd -m -s /bin/bash nexus || true
cd /home/nexus

# Clone repository
su - nexus -c "git clone https://github.com/carafael/short.git /home/nexus/nexus-assistant"
cd /home/nexus/nexus-assistant

# Run installation
su - nexus -c "cd /home/nexus/nexus-assistant && ./install.sh"

# Configure environment
cat > /home/nexus/nexus-assistant/.env << 'EOF'
# Nexus Assistant Configuration

# AI Provider API Keys (replace with your keys)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=codellama

# CLI Paths
GEMINI_CLI_PATH=gemini-cli
CODEX_CLI_PATH=codex-cli
CLAUDE_CLI_PATH=claude
OLLAMA_CLI_PATH=ollama

# Nexus Settings
NEXUS_DATA_DIR=/home/nexus/.nexus
NEXUS_LOG_LEVEL=INFO
NEXUS_DEFAULT_PROVIDER=claude

# Executive Function Features
ENABLE_TASK_REMINDERS=true
AUTO_SAVE_INTERVAL=300
CONTEXT_RETENTION_DAYS=30
EOF

chown nexus:nexus /home/nexus/nexus-assistant/.env

# Install systemd service
cat > /etc/systemd/system/nexus.service << 'EOF'
[Unit]
Description=Nexus Assistant Forever Terminal
After=network.target

[Service]
Type=simple
User=nexus
WorkingDirectory=/home/nexus/nexus-assistant
ExecStart=/home/nexus/nexus-assistant/venv/bin/nexus-daemon start --max-restarts -1
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
systemctl daemon-reload
systemctl enable nexus.service
systemctl start nexus.service

echo "✅ Nexus Assistant installed and running!"
echo "📝 Edit /home/nexus/nexus-assistant/.env to add your API keys"
echo "🔍 Check status: systemctl status nexus"
echo "📋 View logs: journalctl -u nexus -f"
