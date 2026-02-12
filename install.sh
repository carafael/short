#!/bin/bash
# Installation script for Nexus Assistant

set -e

echo "🧠 Installing Nexus Assistant..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.9+ required (found: $python_version)"
    exit 1
fi

echo "✅ Python version OK ($python_version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install package
echo "📥 Installing Nexus Assistant..."
pip install -e .

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys!"
fi

# Create data directory
mkdir -p ~/.nexus

echo ""
echo "✅ Installation complete!"
echo ""
echo "📚 Next steps:"
echo "   1. Edit .env and add your API keys"
echo "   2. Install AI CLI tools you want to use:"
echo "      - gemini-cli: https://github.com/google/generative-ai-python"
echo "      - codex-cli: npm install -g @anthropic-ai/codex-cli (if available)"
echo "      - claude: https://docs.anthropic.com/claude/docs/cli"
echo "      - ollama: https://ollama.ai/download"
echo ""
echo "🚀 To start Nexus:"
echo "   source venv/bin/activate"
echo "   nexus"
echo ""
echo "🔄 To run as daemon:"
echo "   nexus-daemon start"
echo ""
