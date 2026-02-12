# Nexus Assistant 🧠

A forever terminal that integrates multiple AI CLIs (Gemini, Codex, Claude, Ollama) into a unified executive functioning environment for microcontrollers, physics, philosophy, and general task management.

## Features

- 🤖 **Multi-AI Integration** - Seamlessly switch between Gemini, Codex, Claude Code, and Ollama
- 🧠 **Executive Functioning** - Task management, reminders, context tracking
- 🔬 **Domain Modes** - Specialized contexts for:
  - Embedded systems & microcontrollers
  - Physics lab work
  - Philosophy discussions
  - General assistance
- 💾 **Persistent Sessions** - Never lose your conversation history or context
- 🔄 **Forever Running** - Background daemon with auto-restart
- 📋 **Context Switching** - Maintain separate contexts for different projects/domains
- 🎨 **Rich Terminal UI** - Beautiful, interactive command-line interface

## Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd short

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Quick Start

```bash
# Start Nexus in interactive mode
nexus

# Start as background daemon
nexus-daemon start

# Stop daemon
nexus-daemon stop

# Check daemon status
nexus-daemon status
```

## Usage

### Basic Commands

```
/help              - Show all commands
/switch <ai>       - Switch AI provider (gemini|codex|claude|ollama)
/mode <domain>     - Switch domain mode (microcontroller|physics|philosophy|general)
/task add <desc>   - Add a task
/task list         - List all tasks
/context save      - Save current context
/context load      - Load saved context
/history           - Show conversation history
/quit              - Exit Nexus
```

### Domain Modes

#### Microcontroller Mode
```
/mode microcontroller
> Optimized for embedded systems, Arduino, ESP32, STM32, etc.
> Provides code snippets, debugging help, and hardware-specific advice
```

#### Physics Mode
```
/mode physics
> Lab calculations, experimental design, data analysis
> LaTeX equation rendering, unit conversions
```

#### Philosophy Mode
```
/mode philosophy
> Socratic dialogue, argument analysis, ethical reasoning
> Citation formatting, bibliography management
```

### Executive Functioning

```bash
# Task Management
/task add "Review microcontroller power consumption code"
/task add "Calculate resonance frequency for lab setup"
/task complete 1
/task priority 2 high

# Context Switching
/context create "ESP32_Project"
/context switch "ESP32_Project"
/context list

# Reminders
/remind in 1h "Check sensor calibration"
/remind at 14:00 "Team meeting"
```

### Multi-AI Comparison

```bash
# Ask multiple AIs the same question
/compare "What's the best way to implement I2C on ESP32?"

# Output shows responses from all configured AIs side-by-side
```

## Configuration

Edit `~/.nexus/config.yaml` to customize:

```yaml
default_provider: claude
auto_save: true
save_interval: 300  # seconds

providers:
  gemini:
    enabled: true
    model: gemini-pro
  claude:
    enabled: true
    model: claude-sonnet-4-5
  ollama:
    enabled: true
    model: codellama
  codex:
    enabled: false

domains:
  microcontroller:
    default_provider: codex
    context_files:
      - ~/projects/embedded/common.h
  physics:
    default_provider: gemini
    enable_latex: true
  philosophy:
    default_provider: claude
    enable_citations: true
```

## Architecture

```
nexus/
├── cli.py              # Main CLI interface
├── daemon.py           # Background daemon
├── core/
│   ├── providers.py    # AI provider abstraction
│   ├── session.py      # Session management
│   └── storage.py      # Persistent storage
├── executive/
│   ├── tasks.py        # Task management
│   ├── reminders.py    # Reminder system
│   └── context.py      # Context tracking
├── domains/
│   ├── microcontroller.py
│   ├── physics.py
│   └── philosophy.py
└── ui/
    ├── terminal.py     # Rich terminal UI
    └── commands.py     # Command processing
```

## Requirements

- Python 3.9+
- One or more AI CLI tools:
  - `gemini-cli` (Google Gemini)
  - `codex-cli` (OpenAI Codex)
  - `claude` (Claude Code CLI)
  - `ollama` (Ollama)

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details
