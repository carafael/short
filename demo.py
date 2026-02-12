#!/usr/bin/env python3
"""
Interactive demo of Nexus Assistant core features
Run this to see what Nexus can do!
"""

import asyncio
import tempfile
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from nexus.core.providers import ProviderManager
from nexus.core.storage import Storage
from nexus.core.session import SessionManager
from nexus.executive.tasks import TaskManager, Priority, Status
from nexus.executive.context import ContextManager

console = Console()


def show_header():
    """Display demo header"""
    console.print(Panel.fit(
        "[bold cyan]🧠 NEXUS ASSISTANT - Interactive Demo[/bold cyan]\n"
        "[dim]Showcasing core features without API calls[/dim]",
        border_style="cyan"
    ))
    console.print()


async def demo_provider_manager():
    """Demo: Provider Management"""
    console.print("[bold yellow]1. Provider Management[/bold yellow]")
    console.print("   Managing multiple AI providers (Claude, Gemini, Ollama, etc.)\n")

    config = {
        'default_provider': 'claude',
        'providers': {
            'claude': {'enabled': True, 'cli_path': 'claude'},
            'ollama': {'enabled': True, 'cli_path': 'ollama'},
            'gemini': {'enabled': False, 'cli_path': 'gemini-cli'}
        }
    }

    pm = ProviderManager(config)

    table = Table(title="Available Providers", box=box.ROUNDED)
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Active", style="yellow")

    for provider in ['claude', 'ollama', 'gemini']:
        is_available = provider in pm.get_available_providers()
        is_active = provider == pm.get_active_provider()
        table.add_row(
            provider,
            "✅ Available" if is_available else "❌ Unavailable",
            "⭐ Active" if is_active else ""
        )

    console.print(table)
    console.print(f"   [green]✓[/green] Active provider: [bold]{pm.get_active_provider()}[/bold]\n")


async def demo_task_manager():
    """Demo: Task Management"""
    console.print("[bold yellow]2. Task Management[/bold yellow]")
    console.print("   Executive function for tracking work and staying organized\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        storage = Storage(tmpdir)
        tm = TaskManager(storage)

        # Create tasks
        tasks_to_add = [
            ("Deploy Nexus to AWS", Priority.HIGH, ["deployment", "aws"]),
            ("Write documentation", Priority.MEDIUM, ["docs"]),
            ("Test API integrations", Priority.URGENT, ["testing", "api"]),
            ("Refactor code", Priority.LOW, ["refactor"]),
            ("Fix authentication bug", Priority.HIGH, ["bug", "auth"])
        ]

        for desc, priority, tags in tasks_to_add:
            tm.add_task(desc, priority, tags)

        # Complete some tasks
        tm.complete_task(2)  # Complete documentation
        tm.complete_task(4)  # Complete refactor

        # Display tasks
        table = Table(title="Task List", box=box.ROUNDED)
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Description", style="white")
        table.add_column("Priority", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Tags", style="dim")

        for task in tm.tasks:
            status_icon = "✅" if task.status == Status.COMPLETED else "⏳"
            status_text = f"{status_icon} {task.status.value}"

            table.add_row(
                str(task.id),
                task.description,
                task.priority.value.upper(),
                status_text,
                ", ".join(task.tags)
            )

        console.print(table)

        active = tm.get_active_tasks()
        console.print(f"   [green]✓[/green] Active tasks: {len(active)}")
        console.print(f"   [green]✓[/green] Completed tasks: {len([t for t in tm.tasks if t.status == Status.COMPLETED])}\n")


async def demo_session_manager():
    """Demo: Session Management"""
    console.print("[bold yellow]3. Session Management[/bold yellow]")
    console.print("   Maintaining context across conversations\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        storage = Storage(tmpdir)

        config = {
            'default_provider': 'claude',
            'providers': {'claude': {'enabled': True, 'cli_path': 'claude'}}
        }
        pm = ProviderManager(config)

        sm = SessionManager(storage, pm)

        # Create sessions
        sessions_to_create = [
            ("Project Alpha - API Design", "development"),
            ("Database Schema Planning", "development"),
            ("Philosophy Discussion", "philosophy"),
            ("ESP32 Programming", "microcontroller")
        ]

        table = Table(title="Active Sessions", box=box.ROUNDED)
        table.add_column("Session ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Domain", style="yellow")
        table.add_column("Created", style="dim")

        for name, domain in sessions_to_create:
            session = await sm.create_session(name, domain)
            table.add_row(
                session.id[:20] + "...",
                session.name,
                session.domain,
                session.created_at[:10]
            )

        console.print(table)

        session_list = await sm.list_sessions()
        console.print(f"   [green]✓[/green] Total sessions: {len(session_list)}")
        console.print(f"   [green]✓[/green] Sessions persist across restarts\n")


async def demo_context_manager():
    """Demo: Context Management"""
    console.print("[bold yellow]4. Context Management[/bold yellow]")
    console.print("   Domain-specific knowledge and file associations\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        storage = Storage(tmpdir)
        cm = ContextManager(storage)

        # Create contexts
        contexts_to_create = [
            ("esp32-project", "microcontroller", "ESP32 IoT sensor array", ["main.ino", "config.h"]),
            ("ai-ethics", "philosophy", "Discussion on AI moral implications", ["notes.md"]),
            ("web-api", "development", "REST API for user management", ["api.py", "models.py", "tests.py"]),
        ]

        table = Table(title="Contexts", box=box.ROUNDED)
        table.add_column("Name", style="cyan")
        table.add_column("Domain", style="yellow")
        table.add_column("Description", style="white")
        table.add_column("Files", style="dim")

        for name, domain, description, files in contexts_to_create:
            ctx = await cm.create_context(name, domain, description)
            for file in files:
                await cm.add_file_to_context(file, name)

            table.add_row(
                name,
                domain,
                description,
                ", ".join(files)
            )

        console.print(table)

        contexts = cm.list_contexts()
        console.print(f"   [green]✓[/green] Total contexts: {len(contexts)}")
        console.print(f"   [green]✓[/green] Contexts track files and notes\n")


async def demo_storage():
    """Demo: Persistent Storage"""
    console.print("[bold yellow]5. Persistent Storage[/bold yellow]")
    console.print("   Everything saves automatically to ~/.nexus\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        storage = Storage(tmpdir)

        # Show storage structure
        storage_info = [
            ("Sessions", str(storage.sessions_dir), "Conversation history"),
            ("Contexts", str(storage.contexts_dir), "Domain knowledge"),
            ("Tasks", str(storage.tasks_dir), "To-do lists"),
            ("Config", str(storage.get_config_path()), "Settings"),
            ("Logs", str(storage.get_log_path()), "Activity logs")
        ]

        table = Table(title="Storage Structure", box=box.ROUNDED)
        table.add_column("Type", style="cyan")
        table.add_column("Location", style="dim")
        table.add_column("Purpose", style="white")

        for type_name, location, purpose in storage_info:
            # Simplify path for display
            display_path = location.replace(str(tmpdir), "~/.nexus")
            table.add_row(type_name, display_path, purpose)

        console.print(table)
        console.print(f"   [green]✓[/green] All data persists across sessions")
        console.print(f"   [green]✓[/green] JSON format for easy backup and inspection\n")


async def demo_features():
    """Demo: Key Features"""
    console.print("[bold yellow]6. Key Features Summary[/bold yellow]\n")

    features = [
        ("🔄 Provider Switching", "Seamlessly switch between Claude, GPT, Gemini, Ollama"),
        ("📝 Task Management", "Built-in todo list with priorities and tags"),
        ("💾 Session Persistence", "Resume conversations from where you left off"),
        ("🎯 Domain Knowledge", "Specialized contexts for different topics"),
        ("🔧 CLI & Daemon", "Run interactively or as background service"),
        ("🐳 Docker Ready", "Deploy anywhere with containerization"),
        ("☁️  Cloud Deploy", "AWS, GCP, Azure, Railway, Fly.io support"),
        ("🧠 Executive Functions", "Task reminders, context retention, auto-save")
    ]

    table = Table(box=box.ROUNDED, show_header=False)
    table.add_column("Feature", style="cyan")
    table.add_column("Description", style="white")

    for feature, description in features:
        table.add_row(feature, description)

    console.print(table)
    console.print()


async def main():
    """Run the demo"""
    show_header()

    console.print("[bold]Running interactive demonstrations...[/bold]\n")

    demos = [
        demo_provider_manager,
        demo_task_manager,
        demo_session_manager,
        demo_context_manager,
        demo_storage,
        demo_features
    ]

    for demo in demos:
        await demo()
        await asyncio.sleep(0.5)  # Brief pause between demos

    console.print(Panel.fit(
        "[bold green]✨ Demo Complete![/bold green]\n\n"
        "Next steps:\n"
        "  1. Configure your API keys in .env\n"
        "  2. Run: [cyan]nexus[/cyan] to start\n"
        "  3. Try: [cyan]/help[/cyan] for commands\n\n"
        "See QUICKSTART.md for detailed guide!",
        border_style="green"
    ))


if __name__ == "__main__":
    asyncio.run(main())
