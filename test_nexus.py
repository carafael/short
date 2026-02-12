#!/usr/bin/env python3
"""
Test script for Nexus Assistant core functionality
"""

import asyncio
import tempfile
from pathlib import Path

from nexus.core.providers import ProviderManager
from nexus.core.storage import Storage
from nexus.core.session import SessionManager
from nexus.executive.tasks import TaskManager, Priority, Status
from nexus.executive.context import ContextManager


async def test_storage():
    """Test Storage class"""
    print("🧪 Testing Storage...")
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = Storage(tmpdir)

        # Test session save/load
        test_session = {
            'id': 'test-123',
            'messages': [{'role': 'user', 'content': 'Hello!'}]
        }
        await storage.save_session('test-123', test_session)
        loaded = await storage.load_session('test-123')

        assert loaded is not None
        assert loaded['id'] == 'test-123'
        print("   ✅ Storage: Save/load working")

        # Test context save/load
        test_context = {'key': 'value', 'data': [1, 2, 3]}
        await storage.save_context('test-ctx', test_context)
        loaded_ctx = await storage.load_context('test-ctx')

        assert loaded_ctx is not None
        assert loaded_ctx['key'] == 'value'
        print("   ✅ Storage: Context save/load working")

        # Test task save/load
        test_tasks = [
            {'id': 1, 'description': 'Task 1', 'priority': 'high', 'status': 'todo'},
            {'id': 2, 'description': 'Task 2', 'priority': 'medium', 'status': 'completed'}
        ]
        await storage.save_tasks(test_tasks)
        loaded_tasks = await storage.load_tasks()

        assert len(loaded_tasks) == 2
        assert loaded_tasks[0]['description'] == 'Task 1'
        print("   ✅ Storage: Task save/load working\n")


def test_provider_manager():
    """Test ProviderManager"""
    print("🧪 Testing ProviderManager...")

    config = {
        'default_provider': 'claude',
        'providers': {
            'claude': {'enabled': True, 'cli_path': 'claude'},
            'ollama': {'enabled': False, 'cli_path': 'ollama'}
        }
    }

    pm = ProviderManager(config)

    available = pm.get_available_providers()
    assert 'claude' in available
    print(f"   ✅ Available providers: {available}")

    active = pm.get_active_provider()
    assert active == 'claude'
    print(f"   ✅ Active provider: {active}\n")


async def test_session_manager():
    """Test SessionManager"""
    print("🧪 Testing SessionManager...")

    with tempfile.TemporaryDirectory() as tmpdir:
        storage = Storage(tmpdir)

        config = {
            'default_provider': 'claude',
            'providers': {'claude': {'enabled': True, 'cli_path': 'claude'}}
        }
        pm = ProviderManager(config)

        sm = SessionManager(storage, pm)

        # Create session
        session = await sm.create_session("Test Session", domain="testing")
        assert session is not None
        assert session.name == "Test Session"
        print(f"   ✅ Session created: {session.id}")

        # List sessions
        sessions = await sm.list_sessions()
        assert len(sessions) > 0
        print(f"   ✅ Sessions listed: {len(sessions)} session(s)")

        # Load session
        loaded = await sm.load_session(session.id)
        assert loaded is not None
        assert loaded.id == session.id
        print(f"   ✅ Session loaded successfully\n")


async def test_task_manager():
    """Test TaskManager"""
    print("🧪 Testing TaskManager...")

    with tempfile.TemporaryDirectory() as tmpdir:
        storage = Storage(tmpdir)
        tm = TaskManager(storage)

        # Add tasks
        task1 = tm.add_task("Write documentation", Priority.HIGH, tags=["docs"])
        task2 = tm.add_task("Fix bug", Priority.URGENT, tags=["bug", "critical"])
        task3 = tm.add_task("Refactor code", Priority.LOW)

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3
        print(f"   ✅ Created 3 tasks")

        # Test get task
        task = tm.get_task(1)
        assert task is not None
        assert task.description == "Write documentation"
        print(f"   ✅ Get task working")

        # Complete task
        success = tm.complete_task(2)
        assert success
        task2_completed = tm.get_task(2)
        assert task2_completed.status == Status.COMPLETED
        print(f"   ✅ Task completion working")

        # List active tasks
        active = tm.get_active_tasks()
        assert len(active) == 2  # task1 and task3
        print(f"   ✅ Active tasks: {len(active)}")

        # Search tasks
        results = tm.search_tasks("bug")
        assert len(results) == 1
        assert results[0].id == 2
        print(f"   ✅ Task search working")

        # Save and load
        await tm.save_tasks()

        # Create new manager and load
        tm2 = TaskManager(storage)
        await tm2.load_tasks()
        assert len(tm2.tasks) == 3
        print(f"   ✅ Task persistence working\n")


async def test_context_manager():
    """Test ContextManager"""
    print("🧪 Testing ContextManager...")

    with tempfile.TemporaryDirectory() as tmpdir:
        storage = Storage(tmpdir)
        cm = ContextManager(storage)

        # Create contexts
        ctx1 = await cm.create_context(
            "microcontroller",
            domain="hardware",
            description="ESP32 programming notes"
        )

        ctx2 = await cm.create_context(
            "philosophy",
            domain="humanities",
            description="Ethics discussion"
        )

        # Add files and notes
        await cm.add_file_to_context("esp32_code.ino", "microcontroller")
        await cm.add_note_to_context("Remember to configure WiFi", "microcontroller")

        # Get contexts
        contexts = cm.list_contexts()
        assert len(contexts) == 2
        print(f"   ✅ Context tracking working: {len(contexts)} contexts")

        # Switch context
        success = cm.switch_context("microcontroller")
        assert success
        active = cm.get_active_context()
        assert active is not None
        assert active.name == "microcontroller"
        print(f"   ✅ Context switching working")

        # Load context
        loaded = await cm.load_context("philosophy")
        assert loaded is not None
        assert loaded.description == "Ethics discussion"
        print(f"   ✅ Context persistence working\n")


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 NEXUS ASSISTANT - CORE MODULE TESTS")
    print("="*60 + "\n")

    try:
        # Run tests
        test_provider_manager()
        await test_storage()
        await test_session_manager()
        await test_task_manager()
        await test_context_manager()

        print("="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60 + "\n")

        print("📊 Test Summary:")
        print("   • Provider Manager: ✅")
        print("   • Storage System: ✅")
        print("   • Session Manager: ✅")
        print("   • Task Manager: ✅")
        print("   • Context Manager: ✅")
        print("\n🎉 Nexus is ready for deployment!\n")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
