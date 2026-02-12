"""
Task management for executive functioning
"""

from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Priority(Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Status(Enum):
    """Task status"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Represents a single task"""
    id: int
    description: str
    priority: Priority = Priority.MEDIUM
    status: Status = Status.TODO
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    notes: str = ""

    def complete(self):
        """Mark task as completed"""
        self.status = Status.COMPLETED
        self.completed_at = datetime.now().isoformat()

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'description': self.description,
            'priority': self.priority.value,
            'status': self.status.value,
            'created_at': self.created_at,
            'completed_at': self.completed_at,
            'tags': self.tags,
            'notes': self.notes
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            description=data['description'],
            priority=Priority(data.get('priority', 'medium')),
            status=Status(data.get('status', 'todo')),
            created_at=data.get('created_at', datetime.now().isoformat()),
            completed_at=data.get('completed_at'),
            tags=data.get('tags', []),
            notes=data.get('notes', '')
        )


class TaskManager:
    """Manages tasks for executive functioning"""

    def __init__(self, storage):
        self.storage = storage
        self.tasks: List[Task] = []
        self.next_id = 1

    async def load_tasks(self):
        """Load tasks from storage"""
        task_data = await self.storage.load_tasks()
        self.tasks = [Task.from_dict(t) for t in task_data]
        self.next_id = max([t.id for t in self.tasks], default=0) + 1

    async def save_tasks(self):
        """Save tasks to storage"""
        task_data = [t.to_dict() for t in self.tasks]
        await self.storage.save_tasks(task_data)

    def add_task(self, description: str, priority: Priority = Priority.MEDIUM, tags: List[str] = None) -> Task:
        """Add a new task"""
        task = Task(
            id=self.next_id,
            description=description,
            priority=priority,
            tags=tags or []
        )
        self.tasks.append(task)
        self.next_id += 1
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed"""
        task = self.get_task(task_id)
        if task:
            task.complete()
            return True
        return False

    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            return True
        return False

    def list_tasks(self, status: Optional[Status] = None, priority: Optional[Priority] = None) -> List[Task]:
        """List tasks with optional filtering"""
        filtered = self.tasks

        if status:
            filtered = [t for t in filtered if t.status == status]

        if priority:
            filtered = [t for t in filtered if t.priority == priority]

        return sorted(filtered, key=lambda t: (t.priority.value, t.created_at), reverse=True)

    def get_active_tasks(self) -> List[Task]:
        """Get all active (not completed/cancelled) tasks"""
        return [t for t in self.tasks if t.status in [Status.TODO, Status.IN_PROGRESS]]

    def set_priority(self, task_id: int, priority: Priority) -> bool:
        """Set task priority"""
        task = self.get_task(task_id)
        if task:
            task.priority = priority
            return True
        return False

    def add_note(self, task_id: int, note: str) -> bool:
        """Add a note to a task"""
        task = self.get_task(task_id)
        if task:
            if task.notes:
                task.notes += f"\n{note}"
            else:
                task.notes = note
            return True
        return False

    def search_tasks(self, query: str) -> List[Task]:
        """Search tasks by description or tags"""
        query_lower = query.lower()
        return [
            t for t in self.tasks
            if query_lower in t.description.lower() or
            any(query_lower in tag.lower() for tag in t.tags)
        ]
