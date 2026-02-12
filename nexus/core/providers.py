"""
AI Provider abstraction layer for integrating multiple AI CLIs
"""

import asyncio
import subprocess
import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class ProviderType(Enum):
    """Supported AI providers"""
    GEMINI = "gemini"
    CODEX = "codex"
    CLAUDE = "claude"
    OLLAMA = "ollama"


@dataclass
class Message:
    """Represents a message in the conversation"""
    role: str  # 'user' or 'assistant'
    content: str
    provider: Optional[ProviderType] = None
    timestamp: Optional[float] = None


class AIProvider(ABC):
    """Abstract base class for AI providers"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__

    @abstractmethod
    async def send_message(self, message: str, context: Optional[List[Message]] = None) -> str:
        """Send a message and get response"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available/configured"""
        pass

    def _run_cli(self, command: List[str], input_text: str = "") -> str:
        """Helper to run CLI commands"""
        try:
            result = subprocess.run(
                command,
                input=input_text,
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.stdout if result.returncode == 0 else result.stderr
        except subprocess.TimeoutExpired:
            return "Error: Command timed out"
        except FileNotFoundError:
            return f"Error: Command '{command[0]}' not found. Please install it first."
        except Exception as e:
            return f"Error: {str(e)}"


class GeminiProvider(AIProvider):
    """Google Gemini CLI integration"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.cli_path = config.get('cli_path', 'gemini-cli')
        self.model = config.get('model', 'gemini-pro')

    async def send_message(self, message: str, context: Optional[List[Message]] = None) -> str:
        """Send message via gemini-cli"""
        # Build context if provided
        full_prompt = message
        if context:
            context_text = "\n".join([f"{msg.role}: {msg.content}" for msg in context[-5:]])
            full_prompt = f"{context_text}\nuser: {message}"

        command = [self.cli_path, "--model", self.model]
        return await asyncio.to_thread(self._run_cli, command, full_prompt)

    def is_available(self) -> bool:
        """Check if gemini-cli is available"""
        try:
            result = subprocess.run(
                [self.cli_path, "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False


class CodexProvider(AIProvider):
    """OpenAI Codex CLI integration"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.cli_path = config.get('cli_path', 'codex-cli')

    async def send_message(self, message: str, context: Optional[List[Message]] = None) -> str:
        """Send message via codex-cli"""
        command = [self.cli_path]
        return await asyncio.to_thread(self._run_cli, command, message)

    def is_available(self) -> bool:
        """Check if codex-cli is available"""
        try:
            result = subprocess.run(
                [self.cli_path, "--help"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False


class ClaudeProvider(AIProvider):
    """Claude Code CLI integration"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.cli_path = config.get('cli_path', 'claude')
        self.model = config.get('model', 'claude-sonnet-4-5')

    async def send_message(self, message: str, context: Optional[List[Message]] = None) -> str:
        """Send message via claude CLI"""
        # Claude CLI might have different invocation pattern
        # Adjust based on actual claude CLI interface
        command = [self.cli_path, "chat", "--model", self.model]
        return await asyncio.to_thread(self._run_cli, command, message)

    def is_available(self) -> bool:
        """Check if claude CLI is available"""
        try:
            result = subprocess.run(
                [self.cli_path, "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False


class OllamaProvider(AIProvider):
    """Ollama local model integration"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.cli_path = config.get('cli_path', 'ollama')
        self.model = config.get('model', 'codellama')
        self.host = config.get('host', 'http://localhost:11434')

    async def send_message(self, message: str, context: Optional[List[Message]] = None) -> str:
        """Send message via ollama"""
        os.environ['OLLAMA_HOST'] = self.host
        command = [self.cli_path, "run", self.model]
        return await asyncio.to_thread(self._run_cli, command, message)

    def is_available(self) -> bool:
        """Check if ollama is available"""
        try:
            result = subprocess.run(
                [self.cli_path, "list"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False


class ProviderManager:
    """Manages multiple AI providers"""

    def __init__(self, config: Dict[str, Any]):
        self.providers: Dict[ProviderType, AIProvider] = {}
        self.active_provider: Optional[ProviderType] = None
        self._initialize_providers(config)

    def _initialize_providers(self, config: Dict[str, Any]):
        """Initialize all configured providers"""
        provider_classes = {
            ProviderType.GEMINI: GeminiProvider,
            ProviderType.CODEX: CodexProvider,
            ProviderType.CLAUDE: ClaudeProvider,
            ProviderType.OLLAMA: OllamaProvider,
        }

        for provider_type, provider_class in provider_classes.items():
            provider_config = config.get('providers', {}).get(provider_type.value, {})
            if provider_config.get('enabled', True):
                provider = provider_class(provider_config)
                if provider.is_available():
                    self.providers[provider_type] = provider

        # Set default active provider
        default = config.get('default_provider', 'claude')
        self.active_provider = ProviderType(default) if default in [p.value for p in self.providers.keys()] else None

        if not self.active_provider and self.providers:
            self.active_provider = list(self.providers.keys())[0]

    def switch_provider(self, provider_type: ProviderType) -> bool:
        """Switch to a different provider"""
        if provider_type in self.providers:
            self.active_provider = provider_type
            return True
        return False

    async def send_message(self, message: str, context: Optional[List[Message]] = None) -> str:
        """Send message using active provider"""
        if not self.active_provider or self.active_provider not in self.providers:
            return "Error: No active AI provider configured"

        provider = self.providers[self.active_provider]
        return await provider.send_message(message, context)

    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return [p.value for p in self.providers.keys()]

    def get_active_provider(self) -> Optional[str]:
        """Get currently active provider name"""
        return self.active_provider.value if self.active_provider else None
