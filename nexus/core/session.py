"""
Session management for maintaining conversation state
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field, asdict
from nexus.core.providers import Message, ProviderType, ProviderManager
from nexus.core.storage import Storage


@dataclass
class Session:
    """Represents a conversation session"""
    id: str
    name: str
    messages: List[Message] = field(default_factory=list)
    domain: str = "general"
    provider: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    context_data: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, message: Message):
        """Add a message to the session"""
        self.messages.append(message)
        self.updated_at = datetime.now().isoformat()

    def get_recent_messages(self, count: int = 10) -> List[Message]:
        """Get recent messages"""
        return self.messages[-count:] if len(self.messages) > count else self.messages

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for storage"""
        return {
            'id': self.id,
            'name': self.name,
            'messages': [
                {
                    'role': msg.role,
                    'content': msg.content,
                    'provider': msg.provider.value if msg.provider else None,
                    'timestamp': msg.timestamp
                }
                for msg in self.messages
            ],
            'domain': self.domain,
            'provider': self.provider,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'context_data': self.context_data
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """Create session from dictionary"""
        messages = [
            Message(
                role=msg['role'],
                content=msg['content'],
                provider=ProviderType(msg['provider']) if msg.get('provider') else None,
                timestamp=msg.get('timestamp')
            )
            for msg in data.get('messages', [])
        ]

        return cls(
            id=data['id'],
            name=data['name'],
            messages=messages,
            domain=data.get('domain', 'general'),
            provider=data.get('provider'),
            created_at=data.get('created_at', datetime.now().isoformat()),
            updated_at=data.get('updated_at', datetime.now().isoformat()),
            context_data=data.get('context_data', {})
        )


class SessionManager:
    """Manages multiple sessions"""

    def __init__(self, storage: Storage, provider_manager: ProviderManager):
        self.storage = storage
        self.provider_manager = provider_manager
        self.current_session: Optional[Session] = None
        self.sessions: Dict[str, Session] = {}

    async def create_session(self, name: str, domain: str = "general") -> Session:
        """Create a new session"""
        session_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name.replace(' ', '_')}"
        session = Session(
            id=session_id,
            name=name,
            domain=domain,
            provider=self.provider_manager.get_active_provider()
        )
        self.sessions[session_id] = session
        self.current_session = session
        await self.save_session(session)
        return session

    async def load_session(self, session_id: str) -> Optional[Session]:
        """Load a session from storage"""
        if session_id in self.sessions:
            self.current_session = self.sessions[session_id]
            return self.current_session

        data = await self.storage.load_session(session_id)
        if data:
            session = Session.from_dict(data)
            self.sessions[session_id] = session
            self.current_session = session
            return session
        return None

    async def save_session(self, session: Optional[Session] = None) -> bool:
        """Save a session to storage"""
        session = session or self.current_session
        if not session:
            return False
        return await self.storage.save_session(session.id, session.to_dict())

    async def list_sessions(self) -> List[str]:
        """List all available sessions"""
        return await self.storage.list_sessions()

    async def send_message(self, content: str) -> str:
        """Send a message in the current session"""
        if not self.current_session:
            await self.create_session("default")

        # Add user message
        user_message = Message(
            role="user",
            content=content,
            timestamp=datetime.now().timestamp()
        )
        self.current_session.add_message(user_message)

        # Get response from AI
        context = self.current_session.get_recent_messages(10)
        response = await self.provider_manager.send_message(content, context[:-1])

        # Add assistant message
        assistant_message = Message(
            role="assistant",
            content=response,
            provider=ProviderType(self.provider_manager.get_active_provider()),
            timestamp=datetime.now().timestamp()
        )
        self.current_session.add_message(assistant_message)

        # Auto-save
        await self.save_session()

        return response

    def get_current_session(self) -> Optional[Session]:
        """Get the current active session"""
        return self.current_session

    async def switch_session(self, session_id: str) -> bool:
        """Switch to a different session"""
        session = await self.load_session(session_id)
        return session is not None
