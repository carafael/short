#!/bin/bash
#
# Deploy Nexus Assistant to Fly.io (FREE TIER)
#
# Usage: ./deploy-flyio.sh
#

set -e

echo "🚀 Deploying Nexus Assistant to Fly.io (Free Tier)"
echo "=================================================="
echo ""

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "📦 Installing Fly.io CLI..."
    curl -L https://fly.io/install.sh | sh

    # Add to PATH for current session
    export FLYCTL_INSTALL="/home/$USER/.fly"
    export PATH="$FLYCTL_INSTALL/bin:$PATH"

    echo ""
    echo "✅ Fly CLI installed!"
    echo ""
    echo "⚠️  Please run this command to add flyctl to your PATH:"
    echo "    export PATH=\"\$HOME/.fly/bin:\$PATH\""
    echo ""
    echo "Then re-run this script."
    exit 0
fi

echo "✅ Fly CLI found"
echo ""

# Check if logged in
if ! flyctl auth whoami &> /dev/null; then
    echo "🔐 Please login to Fly.io..."
    flyctl auth login
    echo ""
fi

echo "✅ Logged in to Fly.io"
echo ""

# Check if app exists
APP_NAME="nexus-assistant-$(whoami)"
if flyctl apps list | grep -q "$APP_NAME"; then
    echo "📦 App '$APP_NAME' already exists"
    DEPLOY_ONLY=true
else
    echo "📦 Creating new app: $APP_NAME"
    DEPLOY_ONLY=false
fi
echo ""

# Update fly.toml with unique app name
sed -i "s/app = \"nexus-assistant\"/app = \"$APP_NAME\"/" fly.toml
echo "✅ Updated fly.toml with app name: $APP_NAME"
echo ""

# Create or update secrets
echo "🔑 Setting up secrets..."
echo ""
echo "Please enter your API keys (press Enter to skip):"
echo ""

read -p "Anthropic API Key (Claude): " ANTHROPIC_KEY
read -p "OpenAI API Key (GPT): " OPENAI_KEY
read -p "Google API Key (Gemini): " GOOGLE_KEY

if [ -n "$ANTHROPIC_KEY" ]; then
    flyctl secrets set ANTHROPIC_API_KEY="$ANTHROPIC_KEY" --app "$APP_NAME"
    echo "✅ Anthropic key set"
fi

if [ -n "$OPENAI_KEY" ]; then
    flyctl secrets set OPENAI_API_KEY="$OPENAI_KEY" --app "$APP_NAME"
    echo "✅ OpenAI key set"
fi

if [ -n "$GOOGLE_KEY" ]; then
    flyctl secrets set GEMINI_API_KEY="$GOOGLE_KEY" --app "$APP_NAME"
    echo "✅ Google key set"
fi

echo ""

# Create volume if needed
if ! flyctl volumes list --app "$APP_NAME" 2>/dev/null | grep -q "nexus_data"; then
    echo "💾 Creating persistent storage volume (1GB)..."
    flyctl volumes create nexus_data --size 1 --app "$APP_NAME" --region iad
    echo "✅ Volume created"
fi
echo ""

# Deploy
echo "🚀 Deploying to Fly.io..."
echo ""

if [ "$DEPLOY_ONLY" = true ]; then
    flyctl deploy --app "$APP_NAME"
else
    flyctl launch --now --copy-config --name "$APP_NAME"
fi

echo ""
echo "=================================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=================================================="
echo ""
echo "Your Nexus Assistant is now running on Fly.io!"
echo ""
echo "📍 App URL: https://$APP_NAME.fly.dev"
echo ""
echo "Useful commands:"
echo "  flyctl status --app $APP_NAME          # Check status"
echo "  flyctl logs --app $APP_NAME            # View logs"
echo "  flyctl ssh console --app $APP_NAME     # SSH into app"
echo "  flyctl secrets list --app $APP_NAME    # List secrets"
echo "  flyctl scale memory 512 --app $APP_NAME  # Upgrade memory (if needed)"
echo ""
echo "💰 Cost: FREE (on free tier)"
echo ""
echo "🎉 Happy coding!"
