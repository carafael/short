"""
Persistent storage for conversations, contexts, and settings
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import aiofiles


class Storage:
    """Handles persistent storage of Nexus data"""

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir or os.path.expanduser("~/.nexus"))
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.sessions_dir = self.data_dir / "sessions"
        self.contexts_dir = self.data_dir / "contexts"
        self.tasks_dir = self.data_dir / "tasks"

        for directory in [self.sessions_dir, self.contexts_dir, self.tasks_dir]:
            directory.mkdir(exist_ok=True)

    async def save_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Save a session to disk"""
        try:
            session_file = self.sessions_dir / f"{session_id}.json"
            data['last_saved'] = datetime.now().isoformat()

            async with aiofiles.open(session_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False

    async def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load a session from disk"""
        try:
            session_file = self.sessions_dir / f"{session_id}.json"
            if not session_file.exists():
                return None

            async with aiofiles.open(session_file, 'r') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            print(f"Error loading session: {e}")
            return None

    async def list_sessions(self) -> List[str]:
        """List all saved sessions"""
        try:
            sessions = []
            for session_file in self.sessions_dir.glob("*.json"):
                sessions.append(session_file.stem)
            return sorted(sessions, reverse=True)
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []

    async def save_context(self, context_name: str, data: Dict[str, Any]) -> bool:
        """Save a named context"""
        try:
            context_file = self.contexts_dir / f"{context_name}.json"
            data['created'] = data.get('created', datetime.now().isoformat())
            data['updated'] = datetime.now().isoformat()

            async with aiofiles.open(context_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))
            return True
        except Exception as e:
            print(f"Error saving context: {e}")
            return False

    async def load_context(self, context_name: str) -> Optional[Dict[str, Any]]:
        """Load a named context"""
        try:
            context_file = self.contexts_dir / f"{context_name}.json"
            if not context_file.exists():
                return None

            async with aiofiles.open(context_file, 'r') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            print(f"Error loading context: {e}")
            return None

    async def list_contexts(self) -> List[str]:
        """List all saved contexts"""
        try:
            contexts = []
            for context_file in self.contexts_dir.glob("*.json"):
                contexts.append(context_file.stem)
            return sorted(contexts)
        except Exception as e:
            print(f"Error listing contexts: {e}")
            return []

    async def save_tasks(self, tasks: List[Dict[str, Any]]) -> bool:
        """Save task list"""
        try:
            tasks_file = self.tasks_dir / "tasks.json"
            data = {
                'tasks': tasks,
                'updated': datetime.now().isoformat()
            }

            async with aiofiles.open(tasks_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))
            return True
        except Exception as e:
            print(f"Error saving tasks: {e}")
            return False

    async def load_tasks(self) -> List[Dict[str, Any]]:
        """Load task list"""
        try:
            tasks_file = self.tasks_dir / "tasks.json"
            if not tasks_file.exists():
                return []

            async with aiofiles.open(tasks_file, 'r') as f:
                content = await f.read()
                data = json.loads(content)
                return data.get('tasks', [])
        except Exception as e:
            print(f"Error loading tasks: {e}")
            return []

    def get_config_path(self) -> Path:
        """Get path to config file"""
        return self.data_dir / "config.yaml"

    def get_log_path(self) -> Path:
        """Get path to log file"""
        return self.data_dir / "nexus.log"
