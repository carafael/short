# Nexus Assistant - Quick Start Guide

Get up and running with Nexus in under 5 minutes! 🚀

---

## 1. Installation (1 minute)

```bash
# Clone the repository
git clone https://github.com/carafael/short.git
cd short

# Run the installer
./install.sh

# Activate virtual environment
source venv/bin/activate
```

---

## 2. Configuration (2 minutes)

Edit the `.env` file and add your API keys:

```bash
nano .env
```

Minimum configuration (choose one):

```bash
# Option 1: Use Claude (Anthropic)
ANTHROPIC_API_KEY=sk-ant-your-key-here
NEXUS_DEFAULT_PROVIDER=claude

# Option 2: Use Gemini (Google)
GEMINI_API_KEY=your-gemini-key-here
NEXUS_DEFAULT_PROVIDER=gemini

# Option 3: Use Ollama (Local, Free!)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=codellama
NEXUS_DEFAULT_PROVIDER=ollama
```

---

## 3. Test Installation (1 minute)

Run the test suite to verify everything works:

```bash
python test_nexus.py
```

You should see:
```
============================================================
🚀 NEXUS ASSISTANT - CORE MODULE TESTS
============================================================

🧪 Testing ProviderManager...
   ✅ Available providers: ['claude']
   ✅ Active provider: claude

... (more tests)

✅ ALL TESTS PASSED!
```

---

## 4. First Run (1 minute)

### Interactive Mode

```bash
nexus
```

You'll see the Nexus prompt:

```
╔══════════════════════════════════════════════════════════╗
║           🧠 NEXUS ASSISTANT - Forever Terminal          ║
║                                                          ║
║  Provider: claude | Domain: general                      ║
║  Type /help for commands                                 ║
╚══════════════════════════════════════════════════════════╝

nexus>
```

### Try These Commands

```bash
# Get help
/help

# Ask a question
> What's the weather like for coding today?

# Create a task
/task add "Write documentation for new feature"

# List tasks
/task list

# Switch domain to get specialized knowledge
/domain microcontroller
> How do I configure I2C on ESP32?

# Save your session
/save my-first-session

# Exit
/exit
```

---

## 5. Daemon Mode (Forever Terminal)

Run Nexus as a background service:

```bash
# Start daemon
nexus-daemon start

# Check status
nexus-daemon status

# View logs
tail -f ~/.nexus/nexus.log

# Stop daemon
nexus-daemon stop
```

---

## Demo Scenarios

### Scenario 1: Task Management

```bash
nexus
nexus> /task add "Research AI deployment options" high
nexus> /task add "Write deployment scripts" medium
nexus> /task add "Test on AWS" high
nexus> /task list

# Output:
# ┌────┬───────────────────────────────────┬──────────┬──────────┐
# │ ID │ Description                       │ Priority │ Status   │
# ├────┼───────────────────────────────────┼──────────┼──────────┤
# │ 1  │ Research AI deployment options    │ high     │ todo     │
# │ 2  │ Write deployment scripts          │ medium   │ todo     │
# │ 3  │ Test on AWS                       │ high     │ todo     │
# └────┴───────────────────────────────────┴──────────┴──────────┘

nexus> /task complete 1
nexus> /task list
```

### Scenario 2: Multi-Domain Conversations

```bash
nexus
# Start with general conversation
nexus> Tell me about AI assistants

# Switch to technical domain
nexus> /domain microcontroller
nexus> How do I read analog values on ESP32?

# Switch to philosophy
nexus> /domain philosophy
nexus> What are the ethics of AI development?

# Each domain has context-aware responses!
```

### Scenario 3: Session Management

```bash
nexus
# Work on project A
nexus> /session new project-a
nexus> Help me design a REST API for user authentication

# Save and switch
nexus> /save
nexus> /session new project-b
nexus> Let's plan a database schema for e-commerce

# Resume previous session
nexus> /session load project-a
# Context is preserved!
```

---

## Testing Without API Keys

If you don't have API keys yet, you can still test with **Ollama** (local, free):

```bash
# 1. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Pull a model
ollama pull codellama

# 3. Configure Nexus
echo "NEXUS_DEFAULT_PROVIDER=ollama" >> .env
echo "OLLAMA_HOST=http://localhost:11434" >> .env
echo "OLLAMA_MODEL=codellama" >> .env

# 4. Start Nexus
nexus
```

---

## Verification Checklist

✅ Installation completed without errors
✅ Tests pass (`python test_nexus.py`)
✅ `.env` file configured with API keys
✅ `nexus` command launches successfully
✅ Can create and complete tasks
✅ Can switch between domains
✅ Can save and load sessions
✅ Daemon mode starts and stops

---

## What's Next?

1. **Deploy to Cloud** - See [DEPLOYMENT.md](deploy/DEPLOYMENT.md)
2. **Customize Domains** - Add your own in `nexus/domains/`
3. **Configure Providers** - Mix Claude, GPT-4, and local models
4. **Extend Features** - Add custom commands in `nexus/ui/commands.py`

---

## Common Issues

### "Command not found: nexus"

```bash
# Make sure virtual environment is activated
source venv/bin/activate
```

### "No provider available"

```bash
# Check your .env file
cat .env | grep API_KEY

# Verify provider is configured
echo $ANTHROPIC_API_KEY
```

### "Tests failing"

```bash
# Check Python version (needs 3.11+)
python --version

# Reinstall dependencies
pip install -e .
```

---

## Getting Help

- 📖 Full Documentation: [README.md](README.md)
- 🚀 Deployment Guide: [DEPLOYMENT.md](deploy/DEPLOYMENT.md)
- 🐛 Report Issues: [GitHub Issues](https://github.com/carafael/short/issues)
- 💬 Ask Questions: [GitHub Discussions](https://github.com/carafael/short/discussions)

---

## Quick Command Reference

| Command | Description |
|---------|-------------|
| `/help` | Show all commands |
| `/task add <desc>` | Create new task |
| `/task list` | List all tasks |
| `/task complete <id>` | Mark task done |
| `/domain <name>` | Switch domain |
| `/session new <name>` | Create session |
| `/session list` | List sessions |
| `/save [name]` | Save current session |
| `/provider <name>` | Switch AI provider |
| `/exit` | Exit Nexus |

---

**🎉 You're ready to use Nexus! Happy coding!**
