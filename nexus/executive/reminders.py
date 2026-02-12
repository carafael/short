"""
Reminder system for time-based notifications
"""

import asyncio
from typing import List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import re


@dataclass
class Reminder:
    """Represents a reminder"""
    id: int
    message: str
    trigger_time: datetime
    created_at: datetime
    triggered: bool = False

    def is_due(self) -> bool:
        """Check if reminder is due"""
        return not self.triggered and datetime.now() >= self.trigger_time

    def time_until(self) -> timedelta:
        """Get time remaining until trigger"""
        return self.trigger_time - datetime.now()


class ReminderManager:
    """Manages time-based reminders"""

    def __init__(self):
        self.reminders: List[Reminder] = []
        self.next_id = 1
        self.callbacks: List[Callable] = []
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def add_reminder(self, message: str, trigger_time: datetime) -> Reminder:
        """Add a new reminder"""
        reminder = Reminder(
            id=self.next_id,
            message=message,
            trigger_time=trigger_time,
            created_at=datetime.now()
        )
        self.reminders.append(reminder)
        self.next_id += 1
        return reminder

    def add_reminder_relative(self, message: str, time_str: str) -> Optional[Reminder]:
        """Add a reminder with relative time (e.g., '1h', '30m', '2h30m')"""
        delta = self._parse_time_string(time_str)
        if delta:
            trigger_time = datetime.now() + delta
            return self.add_reminder(message, trigger_time)
        return None

    def add_reminder_absolute(self, message: str, time_str: str) -> Optional[Reminder]:
        """Add a reminder with absolute time (e.g., '14:00', '2024-12-25 10:00')"""
        trigger_time = self._parse_absolute_time(time_str)
        if trigger_time:
            return self.add_reminder(message, trigger_time)
        return None

    def _parse_time_string(self, time_str: str) -> Optional[timedelta]:
        """Parse relative time strings like '1h', '30m', '1h30m'"""
        time_str = time_str.lower().strip()

        # Match patterns like 1h, 30m, 1h30m, 2d
        pattern = r'(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?'
        match = re.match(pattern, time_str)

        if not match:
            return None

        days, hours, minutes, seconds = match.groups()
        days = int(days) if days else 0
        hours = int(hours) if hours else 0
        minutes = int(minutes) if minutes else 0
        seconds = int(seconds) if seconds else 0

        if days == 0 and hours == 0 and minutes == 0 and seconds == 0:
            return None

        return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    def _parse_absolute_time(self, time_str: str) -> Optional[datetime]:
        """Parse absolute time strings"""
        formats = [
            '%H:%M',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d %H:%M:%S',
            '%m/%d/%Y %H:%M',
        ]

        for fmt in formats:
            try:
                parsed = datetime.strptime(time_str, fmt)
                # If only time is provided, use today's date
                if fmt == '%H:%M':
                    now = datetime.now()
                    parsed = parsed.replace(year=now.year, month=now.month, day=now.day)
                    # If the time has passed today, schedule for tomorrow
                    if parsed < now:
                        parsed += timedelta(days=1)
                return parsed
            except ValueError:
                continue

        return None

    def list_reminders(self, include_triggered: bool = False) -> List[Reminder]:
        """List all reminders"""
        if include_triggered:
            return sorted(self.reminders, key=lambda r: r.trigger_time)
        return sorted(
            [r for r in self.reminders if not r.triggered],
            key=lambda r: r.trigger_time
        )

    def cancel_reminder(self, reminder_id: int) -> bool:
        """Cancel a reminder"""
        for reminder in self.reminders:
            if reminder.id == reminder_id:
                self.reminders.remove(reminder)
                return True
        return False

    def register_callback(self, callback: Callable):
        """Register a callback to be called when reminders trigger"""
        self.callbacks.append(callback)

    async def start(self):
        """Start the reminder checking loop"""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._check_reminders())

    async def stop(self):
        """Stop the reminder checking loop"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _check_reminders(self):
        """Background task to check for due reminders"""
        while self._running:
            try:
                for reminder in self.reminders:
                    if reminder.is_due():
                        reminder.triggered = True
                        # Call all registered callbacks
                        for callback in self.callbacks:
                            try:
                                if asyncio.iscoroutinefunction(callback):
                                    await callback(reminder)
                                else:
                                    callback(reminder)
                            except Exception as e:
                                print(f"Error in reminder callback: {e}")

                # Clean up old triggered reminders (older than 1 day)
                cutoff = datetime.now() - timedelta(days=1)
                self.reminders = [
                    r for r in self.reminders
                    if not r.triggered or r.trigger_time > cutoff
                ]

                await asyncio.sleep(10)  # Check every 10 seconds
            except Exception as e:
                print(f"Error in reminder check loop: {e}")
                await asyncio.sleep(10)
