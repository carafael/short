"""
Forever daemon for Nexus Assistant with auto-restart capability
"""

import os
import sys
import time
import signal
import subprocess
from typing import Optional
import psutil
import click
from pathlib import Path
from datetime import datetime


class NexusDaemon:
    """Daemon manager for Nexus Assistant"""

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir or os.path.expanduser("~/.nexus"))
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.pid_file = self.data_dir / "nexus.pid"
        self.log_file = self.data_dir / "daemon.log"
        self.running = False
        self.process = None

    def _log(self, message: str):
        """Log a message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        with open(self.log_file, 'a') as f:
            f.write(log_message)

        print(log_message.strip())

    def _write_pid(self, pid: int):
        """Write PID to file"""
        with open(self.pid_file, 'w') as f:
            f.write(str(pid))

    def _read_pid(self) -> Optional[int]:
        """Read PID from file"""
        if not self.pid_file.exists():
            return None

        try:
            with open(self.pid_file, 'r') as f:
                return int(f.read().strip())
        except (ValueError, IOError):
            return None

    def _remove_pid(self):
        """Remove PID file"""
        if self.pid_file.exists():
            self.pid_file.unlink()

    def _is_running(self, pid: Optional[int] = None) -> bool:
        """Check if daemon is running"""
        if pid is None:
            pid = self._read_pid()

        if pid is None:
            return False

        try:
            process = psutil.Process(pid)
            # Check if it's actually a nexus process
            cmdline = ' '.join(process.cmdline())
            return 'nexus' in cmdline.lower()
        except psutil.NoSuchProcess:
            return False

    def start(self, max_restarts: int = -1, restart_delay: int = 5):
        """Start the daemon with auto-restart"""
        # Check if already running
        existing_pid = self._read_pid()
        if existing_pid and self._is_running(existing_pid):
            self._log(f"Nexus daemon already running (PID: {existing_pid})")
            return

        self._log("Starting Nexus daemon in forever mode...")

        # Fork to background
        try:
            pid = os.fork()
            if pid > 0:
                # Parent process
                self._write_pid(pid)
                self._log(f"Nexus daemon started (PID: {pid})")
                self._log(f"Logs: {self.log_file}")
                return
        except OSError as e:
            self._log(f"Fork failed: {e}")
            sys.exit(1)

        # Child process continues here
        os.setsid()
        os.chdir('/')
        os.umask(0)

        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()

        with open(os.devnull, 'r') as dev_null:
            os.dup2(dev_null.fileno(), sys.stdin.fileno())

        with open(self.log_file, 'a') as log:
            os.dup2(log.fileno(), sys.stdout.fileno())
            os.dup2(log.fileno(), sys.stderr.fileno())

        # Run the forever loop
        self._forever_loop(max_restarts, restart_delay)

    def _forever_loop(self, max_restarts: int, restart_delay: int):
        """Main forever loop with auto-restart"""
        restart_count = 0

        def signal_handler(signum, frame):
            self._log("Received shutdown signal")
            self.running = False
            if self.process:
                self.process.terminate()
            self._remove_pid()
            sys.exit(0)

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        self.running = True

        while self.running:
            try:
                self._log(f"Starting Nexus (attempt {restart_count + 1})...")

                # Start the nexus CLI
                self.process = subprocess.Popen(
                    [sys.executable, '-m', 'nexus.cli'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )

                # Monitor the process
                for line in iter(self.process.stdout.readline, ''):
                    if line:
                        self._log(line.strip())

                return_code = self.process.wait()

                if return_code == 0:
                    self._log("Nexus exited normally")
                    break
                else:
                    self._log(f"Nexus crashed with return code {return_code}")

                    restart_count += 1
                    if max_restarts >= 0 and restart_count >= max_restarts:
                        self._log(f"Max restarts ({max_restarts}) reached. Stopping daemon.")
                        break

                    self._log(f"Restarting in {restart_delay} seconds...")
                    time.sleep(restart_delay)

            except Exception as e:
                self._log(f"Error in forever loop: {e}")
                import traceback
                self._log(traceback.format_exc())

                restart_count += 1
                if max_restarts >= 0 and restart_count >= max_restarts:
                    break

                time.sleep(restart_delay)

        self._remove_pid()
        self._log("Daemon stopped")

    def stop(self):
        """Stop the daemon"""
        pid = self._read_pid()

        if pid is None or not self._is_running(pid):
            self._log("Nexus daemon is not running")
            return

        try:
            self._log(f"Stopping Nexus daemon (PID: {pid})...")
            os.kill(pid, signal.SIGTERM)

            # Wait for process to terminate
            for _ in range(10):
                if not self._is_running(pid):
                    break
                time.sleep(0.5)
            else:
                # Force kill if it didn't stop
                self._log("Force killing daemon...")
                os.kill(pid, signal.SIGKILL)

            self._remove_pid()
            self._log("Daemon stopped")

        except ProcessLookupError:
            self._log("Process not found")
            self._remove_pid()
        except PermissionError:
            self._log("Permission denied. Are you the owner?")

    def status(self):
        """Check daemon status"""
        pid = self._read_pid()

        if pid is None:
            print("Nexus daemon is not running (no PID file)")
            return

        if self._is_running(pid):
            try:
                process = psutil.Process(pid)
                print(f"Nexus daemon is running (PID: {pid})")
                print(f"CPU: {process.cpu_percent()}%")
                print(f"Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB")
                print(f"Started: {datetime.fromtimestamp(process.create_time())}")
                print(f"Logs: {self.log_file}")
            except Exception as e:
                print(f"Error getting process info: {e}")
        else:
            print(f"Nexus daemon is not running (stale PID file: {pid})")
            self._remove_pid()

    def restart(self):
        """Restart the daemon"""
        self.stop()
        time.sleep(1)
        self.start()


@click.command()
@click.argument('action', type=click.Choice(['start', 'stop', 'restart', 'status']))
@click.option('--max-restarts', default=-1, help='Maximum number of restarts (-1 for unlimited)')
@click.option('--restart-delay', default=5, help='Delay between restarts in seconds')
@click.option('--data-dir', help='Data directory')
def main(action, max_restarts, restart_delay, data_dir):
    """
    Nexus Daemon - Forever mode for Nexus Assistant

    Commands:
        start   - Start the daemon
        stop    - Stop the daemon
        restart - Restart the daemon
        status  - Check daemon status
    """
    daemon = NexusDaemon(data_dir)

    if action == 'start':
        daemon.start(max_restarts, restart_delay)
    elif action == 'stop':
        daemon.stop()
    elif action == 'restart':
        daemon.restart()
    elif action == 'status':
        daemon.status()


if __name__ == '__main__':
    main()
