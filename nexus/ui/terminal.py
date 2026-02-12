"""
Rich terminal UI for Nexus Assistant
"""

import asyncio
from typing import Optional
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from pathlib import Path


class NexusTerminal:
    """Interactive terminal interface for Nexus"""

    def __init__(self, app, data_dir: Path):
        self.app = app
        self.console = Console()
        self.data_dir = data_dir

        # Setup command completer
        commands = [
            "/help", "/switch", "/mode", "/task", "/remind", "/context",
            "/history", "/sessions", "/session", "/compare", "/status",
            "/clear", "/save", "/quit", "/exit"
        ]
        self.completer = WordCompleter(commands, ignore_case=True)

        # Setup history
        history_file = data_dir / "command_history.txt"
        self.session = PromptSession(
            history=FileHistory(str(history_file)),
            auto_suggest=AutoSuggestFromHistory(),
            completer=self.completer,
        )

    def show_welcome(self):
        """Display welcome message"""
        welcome_text = """
# 🧠 Nexus Assistant

Your forever terminal for AI-powered executive functioning.

**Current Configuration:**
- Provider: {provider}
- Mode: {mode}
- Available AIs: {providers}

Type `/help` for commands or start chatting!
"""
        provider = self.app.provider_manager.get_active_provider()
        providers = ", ".join(self.app.provider_manager.get_available_providers())

        welcome = welcome_text.format(
            provider=provider,
            mode=self.app.current_mode,
            providers=providers
        )

        self.console.print(Panel(Markdown(welcome), border_style="cyan", title="Welcome"))

    def show_prompt(self) -> str:
        """Generate the prompt string"""
        provider = self.app.provider_manager.get_active_provider()
        mode = self.app.current_mode
        session = self.app.session_manager.get_current_session()

        prompt_parts = []
        if session:
            prompt_parts.append(f"[cyan]{session.name}[/cyan]")
        prompt_parts.append(f"[yellow]{mode}[/yellow]")
        prompt_parts.append(f"[green]{provider}[/green]")

        return " | ".join(prompt_parts) + " > "

    async def get_input(self) -> Optional[str]:
        """Get input from user"""
        try:
            # Run prompt_toolkit in thread since it's synchronous
            loop = asyncio.get_event_loop()
            prompt_str = self.show_prompt()
            user_input = await loop.run_in_executor(
                None,
                lambda: self.session.prompt(prompt_str)
            )
            return user_input
        except (EOFError, KeyboardInterrupt):
            return "/quit"

    def display_response(self, response: str, as_markdown: bool = True):
        """Display AI response"""
        if not response or response == "QUIT":
            return

        if as_markdown and not response.startswith("["):
            # Try to render as markdown
            try:
                md = Markdown(response)
                self.console.print(Panel(md, border_style="green", title="Response"))
            except:
                self.console.print(response)
        else:
            self.console.print(response)

    def display_error(self, error: str):
        """Display error message"""
        self.console.print(f"[red]Error:[/red] {error}")

    def display_reminder(self, reminder):
        """Display a reminder notification"""
        msg = f"⏰ Reminder: {reminder.message}"
        self.console.print(Panel(msg, border_style="yellow", title="Reminder"))
        # Terminal bell
        print("\a")

    async def run(self):
        """Main terminal loop"""
        self.show_welcome()

        # Register reminder callback
        self.app.reminder_manager.register_callback(self.display_reminder)

        while True:
            try:
                user_input = await self.get_input()

                if user_input is None:
                    continue

                # Process the input
                response = await self.app.command_processor.process(user_input)

                if response == "QUIT":
                    self.console.print("[yellow]Goodbye! 👋[/yellow]")
                    break

                if response:
                    self.display_response(response)

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use /quit to exit[/yellow]")
                continue
            except Exception as e:
                self.display_error(str(e))
                import traceback
                traceback.print_exc()
