"""
Main CLI entry point for Nexus Assistant
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional
import click
from dotenv import load_dotenv
import yaml

from nexus.core.providers import ProviderManager
from nexus.core.storage import Storage
from nexus.core.session import SessionManager
from nexus.executive.tasks import TaskManager
from nexus.executive.reminders import ReminderManager
from nexus.executive.context import ContextManager
from nexus.domains.microcontroller import MicrocontrollerMode
from nexus.domains.physics import PhysicsMode
from nexus.domains.philosophy import PhilosophyMode
from nexus.ui.terminal import NexusTerminal
from nexus.ui.commands import CommandProcessor


class NexusApp:
    """Main Nexus application"""

    def __init__(self, config_path: Optional[Path] = None):
        # Load environment variables
        load_dotenv()

        # Initialize storage
        data_dir = os.getenv('NEXUS_DATA_DIR', '~/.nexus')
        self.storage = Storage(data_dir)

        # Load config
        self.config = self._load_config(config_path)

        # Initialize core components
        self.provider_manager = ProviderManager(self.config)
        self.session_manager = SessionManager(self.storage, self.provider_manager)
        self.task_manager = TaskManager(self.storage)
        self.reminder_manager = ReminderManager()
        self.context_manager = ContextManager(self.storage)

        # Initialize domain modes
        self.domain_modes = {
            "microcontroller": MicrocontrollerMode(),
            "physics": PhysicsMode(),
            "philosophy": PhilosophyMode(),
            "general": type('GeneralMode', (), {
                'name': 'general',
                'description': 'General purpose assistance',
                'get_system_prompt': lambda: 'General purpose AI assistant'
            })()
        }
        self.current_mode = "general"

        # Initialize UI components
        self.command_processor = CommandProcessor(self)
        self.terminal = NexusTerminal(self, self.storage.data_dir)

    def _load_config(self, config_path: Optional[Path] = None) -> dict:
        """Load configuration from file or use defaults"""
        if config_path is None:
            config_path = self.storage.get_config_path()

        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        else:
            # Default configuration
            default_config = {
                'default_provider': os.getenv('NEXUS_DEFAULT_PROVIDER', 'claude'),
                'auto_save': True,
                'save_interval': 300,
                'providers': {
                    'gemini': {
                        'enabled': True,
                        'cli_path': os.getenv('GEMINI_CLI_PATH', 'gemini-cli'),
                        'model': 'gemini-pro'
                    },
                    'codex': {
                        'enabled': True,
                        'cli_path': os.getenv('CODEX_CLI_PATH', 'codex-cli')
                    },
                    'claude': {
                        'enabled': True,
                        'cli_path': os.getenv('CLAUDE_CLI_PATH', 'claude'),
                        'model': 'claude-sonnet-4-5'
                    },
                    'ollama': {
                        'enabled': True,
                        'cli_path': os.getenv('OLLAMA_CLI_PATH', 'ollama'),
                        'model': os.getenv('OLLAMA_MODEL', 'codellama'),
                        'host': os.getenv('OLLAMA_HOST', 'http://localhost:11434')
                    }
                }
            }

            # Save default config
            with open(config_path, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)

            return default_config

    async def initialize(self):
        """Initialize the application"""
        # Load saved data
        await self.task_manager.load_tasks()
        await self.context_manager.load_contexts()

        # Create default session if none exists
        if not self.session_manager.current_session:
            await self.session_manager.create_session("default")

        # Start reminder manager
        await self.reminder_manager.start()

    async def run(self):
        """Run the main application"""
        await self.initialize()
        await self.terminal.run()
        await self.shutdown()

    async def shutdown(self):
        """Cleanup on shutdown"""
        # Save all data
        await self.session_manager.save_session()
        await self.task_manager.save_tasks()
        await self.context_manager.save_context()

        # Stop reminder manager
        await self.reminder_manager.stop()


@click.command()
@click.option('--config', type=click.Path(exists=True), help='Path to config file')
@click.option('--version', is_flag=True, help='Show version')
def main(config, version):
    """Nexus Assistant - Forever terminal with multiple AI integrations"""
    if version:
        from nexus import __version__
        click.echo(f"Nexus Assistant v{__version__}")
        return

    config_path = Path(config) if config else None

    try:
        app = NexusApp(config_path)
        asyncio.run(app.run())
    except KeyboardInterrupt:
        click.echo("\nExiting...")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
