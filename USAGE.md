# Nexus Assistant - Usage Guide

## Quick Start

### Installation

```bash
# Run installation script
./install.sh

# Or manual installation
python -m venv venv
source venv/bin/activate
pip install -e .
```

### Configuration

1. Edit `.env` file and add your API keys:

```bash
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
OLLAMA_HOST=http://localhost:11434
```

2. Install the AI CLI tools you want to use:

```bash
# Ollama (recommended for local/offline use)
curl https://ollama.ai/install.sh | sh
ollama pull codellama

# Claude CLI
pip install anthropic-claude-cli

# Gemini CLI
pip install google-generativeai
```

### Starting Nexus

**Interactive Mode:**
```bash
source venv/bin/activate
nexus
```

**Daemon Mode (Forever Running):**
```bash
# Start daemon
nexus-daemon start

# Check status
nexus-daemon status

# Stop daemon
nexus-daemon stop

# Restart daemon
nexus-daemon restart
```

## Core Features

### 1. AI Provider Switching

Switch between different AI models on the fly:

```
> /switch claude
Switched to claude

> /switch ollama
Switched to ollama

> /switch
Current provider: ollama
Available: gemini, codex, claude, ollama
```

### 2. Domain Modes

Activate specialized modes for different types of work:

#### Microcontroller Mode
```
> /mode microcontroller
Switched to microcontroller mode

> How do I set up I2C on ESP32?
[Gets specialized embedded systems help]

> Show me an I2C scanner sketch
[Receives working Arduino code]
```

#### Physics Mode
```
> /mode physics
Switched to physics mode

> Calculate the resonant frequency for L=10mH, C=100nF
[Gets calculation with proper units and formulas]

> What's the uncertainty if L has ±1% error?
[Receives error propagation analysis]
```

#### Philosophy Mode
```
> /mode philosophy
Switched to philosophy mode

> What's the trolley problem?
[Gets philosophical analysis with multiple perspectives]

> Analyze this argument: ...
[Receives logical analysis and fallacy detection]
```

### 3. Task Management

Executive functioning support with task tracking:

```
> /task add Review ESP32 power consumption code
Task #1 added

> /task add Calculate lab resonance values
Task #2 added

> /task list
ID  Description                          Priority  Status
1   Review ESP32 power consumption code  medium    todo
2   Calculate lab resonance values       medium    todo

> /task priority 1 high
Task #1 priority set to high

> /task complete 1
Task #1 completed!
```

### 4. Reminders

Set time-based reminders:

```
> /remind in 1h Check sensor calibration
Reminder #1 set for 2024-12-10 15:30:00

> /remind at 14:00 Team meeting
Reminder #2 set for 2024-12-10 14:00:00

> /remind in 30m Review pull request
Reminder #3 set for 2024-12-10 14:45:00
```

Time formats supported:
- Relative: `1h`, `30m`, `2h30m`, `1d`
- Absolute: `14:00`, `2024-12-25 10:00`

### 5. Context Management

Maintain separate contexts for different projects:

```
> /context create ESP32_Project
Context 'ESP32_Project' created

> /context create Physics_Lab_Exp1
Context 'Physics_Lab_Exp1' created

> /context switch ESP32_Project
Switched to context 'ESP32_Project'

> /context list
Contexts:
  * ESP32_Project
    Physics_Lab_Exp1
```

### 6. Multi-AI Comparison

Compare responses from different AI models:

```
> /compare What's the best way to debounce a button in Arduino?

┌─ gemini ─────────────────────────────────┐
│ Use a delay-based approach...            │
│ [response truncated]                      │
└──────────────────────────────────────────┘

┌─ claude ─────────────────────────────────┐
│ I recommend using interrupts with...     │
│ [response truncated]                      │
└──────────────────────────────────────────┘

┌─ ollama ─────────────────────────────────┐
│ Here's a hardware and software solution..│
│ [response truncated]                      │
└──────────────────────────────────────────┘
```

### 7. Session Management

Save and resume conversation sessions:

```
> /save
Session saved successfully

> /sessions
Available sessions:
  - 20241210_140523_default
  - 20241209_093012_embedded_work
  - 20241208_151234_physics_calc

> /session load 20241209_093012_embedded_work
Loaded session: embedded_work

> /history
[Shows conversation history]
```

## Domain-Specific Features

### Microcontroller Mode

#### Quick Templates
```
> Show me the arduino_blink template
> Give me the esp32_wifi template
> Show me the i2c_scanner template
```

#### Platform-Specific Help
```
> What's the voltage for ESP32?
3.3V - be careful with 5V devices!

> Common I2C addresses?
0x27: LCD Display
0x3C: OLED (SSD1306)
0x68: MPU6050 (IMU)
...
```

### Physics Mode

#### Constants Reference
```
> What's the value of Planck's constant?
h = 6.62607015×10⁻³⁴ J·s

> Show me all constants
[Displays table of physical constants]
```

#### Unit Conversions
```
> Convert 5 eV to Joules
5 eV = 8.01×10⁻¹⁹ J
```

#### Formula Reference
```
> Show me kinematics formulas
- v = v₀ + at
- x = x₀ + v₀t + ½at²
- v² = v₀² + 2a(x - x₀)
```

### Philosophy Mode

#### Fallacy Detection
```
> Check my argument for fallacies
[Provides analysis of logical structure]
```

#### Ethical Framework Analysis
```
> Analyze this from a utilitarian perspective
> What would Kant say about this?
> Compare virtue ethics and deontology here
```

#### Thought Experiments
```
> Explain the trolley problem
> What's the ship of Theseus?
> Tell me about the experience machine
```

## Advanced Usage

### Custom Configuration

Edit `~/.nexus/config.yaml`:

```yaml
default_provider: claude
auto_save: true
save_interval: 300

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

domains:
  microcontroller:
    default_provider: codex
  physics:
    default_provider: gemini
    enable_latex: true
  philosophy:
    default_provider: claude
```

### Integration with Other Tools

#### Use with tmux/screen
```bash
# In tmux
tmux new -s nexus
nexus

# Detach: Ctrl+B, then D
# Reattach: tmux attach -t nexus
```

#### Systemd Service (Linux)

Create `/etc/systemd/system/nexus.service`:

```ini
[Unit]
Description=Nexus Assistant Daemon
After=network.target

[Service]
Type=forking
User=youruser
WorkingDirectory=/path/to/nexus
ExecStart=/path/to/venv/bin/nexus-daemon start
ExecStop=/path/to/venv/bin/nexus-daemon stop
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable nexus
sudo systemctl start nexus
sudo systemctl status nexus
```

## Troubleshooting

### AI Provider Not Working

Check if the CLI is installed and in PATH:
```bash
which gemini-cli
which claude
which ollama
```

### Permission Denied

Check file permissions:
```bash
chmod +x install.sh
chmod -R u+w ~/.nexus
```

### Daemon Won't Start

Check logs:
```bash
tail -f ~/.nexus/daemon.log
```

### Clear Corrupted Data

```bash
rm -rf ~/.nexus/*.json
# Restart Nexus - it will create fresh data
```

## Tips and Tricks

1. **Use Tab Completion**: Commands support tab completion

2. **Multi-line Input**: Use `\` at end of line for continuation

3. **Quick Mode Switch**: Create aliases in your shell:
   ```bash
   alias nexus-mcu='nexus --mode microcontroller'
   alias nexus-phys='nexus --mode physics'
   ```

4. **Backup Important Sessions**:
   ```bash
   cp -r ~/.nexus/sessions ~/nexus-backup
   ```

5. **Share Contexts Between Machines**:
   ```bash
   # Export
   tar -czf nexus-contexts.tar.gz ~/.nexus/contexts

   # Import on another machine
   tar -xzf nexus-contexts.tar.gz -C ~/
   ```

## Getting Help

- GitHub Issues: https://github.com/yourusername/nexus-assistant/issues
- Type `/help` in Nexus for command reference
- Check logs: `~/.nexus/nexus.log` and `~/.nexus/daemon.log`
