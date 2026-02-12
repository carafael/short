"""
Context management for maintaining project/domain-specific information
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class Context:
    """Represents a named context with associated data"""
    name: str
    domain: str = "general"
    description: str = ""
    files: List[str] = field(default_factory=list)
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'domain': self.domain,
            'description': self.description,
            'files': self.files,
            'notes': self.notes,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Context':
        """Create from dictionary"""
        return cls(
            name=data['name'],
            domain=data.get('domain', 'general'),
            description=data.get('description', ''),
            files=data.get('files', []),
            notes=data.get('notes', ''),
            metadata=data.get('metadata', {}),
            created_at=data.get('created_at', datetime.now().isoformat()),
            updated_at=data.get('updated_at', datetime.now().isoformat())
        )

    def add_file(self, file_path: str):
        """Add a file to the context"""
        if file_path not in self.files:
            self.files.append(file_path)
            self.updated_at = datetime.now().isoformat()

    def remove_file(self, file_path: str):
        """Remove a file from the context"""
        if file_path in self.files:
            self.files.remove(file_path)
            self.updated_at = datetime.now().isoformat()

    def add_note(self, note: str):
        """Add a note to the context"""
        if self.notes:
            self.notes += f"\n\n{note}"
        else:
            self.notes = note
        self.updated_at = datetime.now().isoformat()


class ContextManager:
    """Manages multiple named contexts"""

    def __init__(self, storage):
        self.storage = storage
        self.contexts: Dict[str, Context] = {}
        self.active_context: Optional[str] = None

    async def load_contexts(self):
        """Load all contexts from storage"""
        context_names = await self.storage.list_contexts()
        for name in context_names:
            data = await self.storage.load_context(name)
            if data:
                self.contexts[name] = Context.from_dict(data)

    async def create_context(self, name: str, domain: str = "general", description: str = "") -> Context:
        """Create a new context"""
        context = Context(name=name, domain=domain, description=description)
        self.contexts[name] = context
        await self.save_context(context)
        return context

    async def save_context(self, context: Optional[Context] = None):
        """Save a context to storage"""
        if context:
            await self.storage.save_context(context.name, context.to_dict())
        elif self.active_context and self.active_context in self.contexts:
            context = self.contexts[self.active_context]
            await self.storage.save_context(context.name, context.to_dict())

    async def load_context(self, name: str) -> Optional[Context]:
        """Load a specific context"""
        if name in self.contexts:
            return self.contexts[name]

        data = await self.storage.load_context(name)
        if data:
            context = Context.from_dict(data)
            self.contexts[name] = context
            return context
        return None

    def switch_context(self, name: str) -> bool:
        """Switch to a different context"""
        if name in self.contexts:
            self.active_context = name
            return True
        return False

    def get_active_context(self) -> Optional[Context]:
        """Get the currently active context"""
        if self.active_context and self.active_context in self.contexts:
            return self.contexts[self.active_context]
        return None

    def list_contexts(self) -> List[str]:
        """List all context names"""
        return list(self.contexts.keys())

    async def delete_context(self, name: str) -> bool:
        """Delete a context"""
        if name in self.contexts:
            del self.contexts[name]
            # TODO: Delete from storage as well
            return True
        return False

    def get_context_files(self, context_name: Optional[str] = None) -> List[str]:
        """Get files associated with a context"""
        name = context_name or self.active_context
        if name and name in self.contexts:
            return self.contexts[name].files
        return []

    async def add_file_to_context(self, file_path: str, context_name: Optional[str] = None):
        """Add a file to a context"""
        name = context_name or self.active_context
        if name and name in self.contexts:
            self.contexts[name].add_file(file_path)
            await self.save_context(self.contexts[name])

    async def add_note_to_context(self, note: str, context_name: Optional[str] = None):
        """Add a note to a context"""
        name = context_name or self.active_context
        if name and name in self.contexts:
            self.contexts[name].add_note(note)
            await self.save_context(self.contexts[name])
