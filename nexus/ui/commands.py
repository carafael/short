"""
Command processor for Nexus terminal
"""

from typing import Dict, Callable, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown


class CommandProcessor:
    """Processes commands and routes them to appropriate handlers"""

    def __init__(self, app):
        self.app = app
        self.console = Console()
        self.commands: Dict[str, Callable] = {}
        self._register_commands()

    def _register_commands(self):
        """Register all available commands"""
        self.commands = {
            "/help": self.cmd_help,
            "/switch": self.cmd_switch_provider,
            "/mode": self.cmd_switch_mode,
            "/task": self.cmd_task,
            "/remind": self.cmd_remind,
            "/context": self.cmd_context,
            "/history": self.cmd_history,
            "/sessions": self.cmd_sessions,
            "/session": self.cmd_session,
            "/compare": self.cmd_compare,
            "/status": self.cmd_status,
            "/clear": self.cmd_clear,
            "/save": self.cmd_save,
            "/quit": self.cmd_quit,
            "/exit": self.cmd_quit,
        }

    async def process(self, input_text: str) -> Optional[str]:
        """Process user input"""
        input_text = input_text.strip()

        if not input_text:
            return None

        # Check if it's a command
        if input_text.startswith("/"):
            parts = input_text.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            if command in self.commands:
                return await self.commands[command](args)
            else:
                return f"Unknown command: {command}. Type /help for available commands."
        else:
            # Regular message - send to AI
            return await self.app.session_manager.send_message(input_text)

    async def cmd_help(self, args: str) -> str:
        """Show help information"""
        table = Table(title="Nexus Assistant Commands", show_header=True, header_style="bold magenta")
        table.add_column("Command", style="cyan", width=25)
        table.add_column("Description", style="green")

        commands_help = [
            ("/help", "Show this help message"),
            ("/switch <ai>", "Switch AI provider (gemini|codex|claude|ollama)"),
            ("/mode <domain>", "Switch domain mode (microcontroller|physics|philosophy|general)"),
            ("/task add <desc>", "Add a new task"),
            ("/task list", "List all tasks"),
            ("/task complete <id>", "Mark task as completed"),
            ("/task priority <id> <level>", "Set task priority"),
            ("/remind in <time> <msg>", "Set reminder (e.g., 'in 1h Check sensors')"),
            ("/remind at <time> <msg>", "Set reminder at time (e.g., 'at 14:00 Meeting')"),
            ("/context create <name>", "Create a new context"),
            ("/context switch <name>", "Switch to a context"),
            ("/context list", "List all contexts"),
            ("/history", "Show conversation history"),
            ("/sessions", "List all sessions"),
            ("/session load <id>", "Load a session"),
            ("/compare <question>", "Ask multiple AIs and compare responses"),
            ("/status", "Show current status"),
            ("/save", "Save current session"),
            ("/clear", "Clear screen"),
            ("/quit", "Exit Nexus"),
        ]

        for cmd, desc in commands_help:
            table.add_row(cmd, desc)

        self.console.print(table)
        return ""

    async def cmd_switch_provider(self, args: str) -> str:
        """Switch AI provider"""
        if not args:
            available = self.app.provider_manager.get_available_providers()
            current = self.app.provider_manager.get_active_provider()
            return f"Current provider: {current}\nAvailable: {', '.join(available)}\nUsage: /switch <provider>"

        from nexus.core.providers import ProviderType
        try:
            provider_type = ProviderType(args.lower())
            if self.app.provider_manager.switch_provider(provider_type):
                return f"Switched to {args}"
            else:
                return f"Provider '{args}' not available"
        except ValueError:
            return f"Unknown provider: {args}"

    async def cmd_switch_mode(self, args: str) -> str:
        """Switch domain mode"""
        if not args:
            return f"Current mode: {self.app.current_mode}\nAvailable: {', '.join(self.app.domain_modes.keys())}\nUsage: /mode <domain>"

        if args in self.app.domain_modes:
            self.app.current_mode = args
            mode = self.app.domain_modes[args]
            return f"Switched to {args} mode\n{mode.description}"
        else:
            return f"Unknown mode: {args}\nAvailable: {', '.join(self.app.domain_modes.keys())}"

    async def cmd_task(self, args: str) -> str:
        """Handle task commands"""
        parts = args.split(maxsplit=1)
        if not parts:
            return "Usage: /task <add|list|complete|priority> [args]"

        action = parts[0].lower()

        if action == "add":
            if len(parts) < 2:
                return "Usage: /task add <description>"
            from nexus.executive.tasks import Priority
            task = self.app.task_manager.add_task(parts[1])
            await self.app.task_manager.save_tasks()
            return f"Task #{task.id} added: {task.description}"

        elif action == "list":
            tasks = self.app.task_manager.get_active_tasks()
            if not tasks:
                return "No active tasks"

            table = Table(title="Active Tasks")
            table.add_column("ID", style="cyan")
            table.add_column("Description", style="white")
            table.add_column("Priority", style="yellow")
            table.add_column("Status", style="green")

            for task in tasks:
                table.add_row(
                    str(task.id),
                    task.description,
                    task.priority.value,
                    task.status.value
                )

            self.console.print(table)
            return ""

        elif action == "complete":
            if len(parts) < 2:
                return "Usage: /task complete <id>"
            try:
                task_id = int(parts[1])
                if self.app.task_manager.complete_task(task_id):
                    await self.app.task_manager.save_tasks()
                    return f"Task #{task_id} completed!"
                else:
                    return f"Task #{task_id} not found"
            except ValueError:
                return "Invalid task ID"

        elif action == "priority":
            parts2 = parts[1].split(maxsplit=1) if len(parts) > 1 else []
            if len(parts2) < 2:
                return "Usage: /task priority <id> <low|medium|high|urgent>"
            try:
                from nexus.executive.tasks import Priority
                task_id = int(parts2[0])
                priority = Priority(parts2[1].lower())
                if self.app.task_manager.set_priority(task_id, priority):
                    await self.app.task_manager.save_tasks()
                    return f"Task #{task_id} priority set to {priority.value}"
                else:
                    return f"Task #{task_id} not found"
            except (ValueError, KeyError):
                return "Invalid task ID or priority level"

        return "Unknown task action"

    async def cmd_remind(self, args: str) -> str:
        """Handle reminder commands"""
        parts = args.split(maxsplit=2)
        if len(parts) < 3:
            return "Usage: /remind <in|at> <time> <message>"

        timing_type = parts[0].lower()
        time_str = parts[1]
        message = parts[2]

        if timing_type == "in":
            reminder = self.app.reminder_manager.add_reminder_relative(message, time_str)
        elif timing_type == "at":
            reminder = self.app.reminder_manager.add_reminder_absolute(message, time_str)
        else:
            return "Usage: /remind <in|at> <time> <message>"

        if reminder:
            return f"Reminder #{reminder.id} set for {reminder.trigger_time.strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            return "Failed to parse time. Use formats like '1h', '30m' or '14:00'"

    async def cmd_context(self, args: str) -> str:
        """Handle context commands"""
        parts = args.split(maxsplit=1)
        if not parts:
            return "Usage: /context <create|switch|list|save> [args]"

        action = parts[0].lower()

        if action == "create":
            if len(parts) < 2:
                return "Usage: /context create <name>"
            context = await self.app.context_manager.create_context(parts[1], self.app.current_mode)
            return f"Context '{parts[1]}' created"

        elif action == "switch":
            if len(parts) < 2:
                return "Usage: /context switch <name>"
            if self.app.context_manager.switch_context(parts[1]):
                return f"Switched to context '{parts[1]}'"
            else:
                return f"Context '{parts[1]}' not found"

        elif action == "list":
            contexts = self.app.context_manager.list_contexts()
            if not contexts:
                return "No contexts available"
            active = self.app.context_manager.active_context
            return "Contexts:\n" + "\n".join(
                f"  {'*' if c == active else ' '} {c}" for c in contexts
            )

        elif action == "save":
            await self.app.context_manager.save_context()
            return "Context saved"

        return "Unknown context action"

    async def cmd_history(self, args: str) -> str:
        """Show conversation history"""
        session = self.app.session_manager.get_current_session()
        if not session or not session.messages:
            return "No conversation history"

        count = 20
        if args:
            try:
                count = int(args)
            except ValueError:
                pass

        messages = session.get_recent_messages(count)

        for msg in messages:
            role_color = "cyan" if msg.role == "user" else "green"
            self.console.print(f"[{role_color}]{msg.role}:[/{role_color}] {msg.content}\n")

        return ""

    async def cmd_sessions(self, args: str) -> str:
        """List all sessions"""
        sessions = await self.app.session_manager.list_sessions()
        if not sessions:
            return "No saved sessions"
        return "Available sessions:\n" + "\n".join(f"  - {s}" for s in sessions)

    async def cmd_session(self, args: str) -> str:
        """Handle session commands"""
        parts = args.split(maxsplit=1)
        if not parts or parts[0] != "load":
            return "Usage: /session load <id>"

        if len(parts) < 2:
            return "Usage: /session load <id>"

        session = await self.app.session_manager.load_session(parts[1])
        if session:
            return f"Loaded session: {session.name}"
        else:
            return f"Session '{parts[1]}' not found"

    async def cmd_compare(self, args: str) -> str:
        """Compare responses from multiple AIs"""
        if not args:
            return "Usage: /compare <question>"

        # Store current provider
        original_provider = self.app.provider_manager.active_provider

        responses = {}
        for provider_name in self.app.provider_manager.get_available_providers():
            from nexus.core.providers import ProviderType
            provider_type = ProviderType(provider_name)
            self.app.provider_manager.switch_provider(provider_type)
            response = await self.app.provider_manager.send_message(args)
            responses[provider_name] = response

        # Restore original provider
        self.app.provider_manager.active_provider = original_provider

        # Display comparison
        for provider, response in responses.items():
            panel = Panel(
                response[:500] + ("..." if len(response) > 500 else ""),
                title=f"[bold]{provider}[/bold]",
                border_style="blue"
            )
            self.console.print(panel)

        return ""

    async def cmd_status(self, args: str) -> str:
        """Show current status"""
        session = self.app.session_manager.get_current_session()
        active_tasks = self.app.task_manager.get_active_tasks()
        pending_reminders = self.app.reminder_manager.list_reminders()

        status_info = f"""
[bold cyan]Nexus Assistant Status[/bold cyan]

[yellow]AI Provider:[/yellow] {self.app.provider_manager.get_active_provider()}
[yellow]Domain Mode:[/yellow] {self.app.current_mode}
[yellow]Current Session:[/yellow] {session.name if session else 'None'}
[yellow]Active Tasks:[/yellow] {len(active_tasks)}
[yellow]Pending Reminders:[/yellow] {len(pending_reminders)}
[yellow]Available Providers:[/yellow] {', '.join(self.app.provider_manager.get_available_providers())}
"""
        self.console.print(Panel(status_info, border_style="green"))
        return ""

    async def cmd_clear(self, args: str) -> str:
        """Clear the screen"""
        self.console.clear()
        return ""

    async def cmd_save(self, args: str) -> str:
        """Save current session"""
        await self.app.session_manager.save_session()
        await self.app.task_manager.save_tasks()
        await self.app.context_manager.save_context()
        return "Session saved successfully"

    async def cmd_quit(self, args: str) -> str:
        """Quit the application"""
        await self.cmd_save("")
        return "QUIT"
