"""
Orchestrator - Master Watcher Orchestrator for AI Employee Vault

⚠️ This script manages background processes - run with python orchestrator.py

This is the master orchestration script that:
- Starts all watchers as background processes
- Implements watchdog pattern (auto-restart on crash)
- Logs all watcher status to Logs/orchestrator.log
- Supports graceful shutdown with SIGINT/SIGTERM handling
- Has --dry-run flag for testing without starting watchers
- Includes health check endpoint returning JSON status
- Uses environment variables for configuration

Usage:
    python orchestrator.py              # Start all watchers
    python orchestrator.py --dry-run    # Test without starting
    python orchestrator.py --health     # Check health status
    python orchestrator.py --stop       # Stop all watchers

Environment Variables:
    WATCHER_INTERVAL        - Default watcher interval in seconds (default: 60)
    LOG_LEVEL              - Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)
    LOG_FILE               - Log file path (default: Logs/orchestrator.log)
    RESTART_DELAY          - Delay before restarting crashed watcher (default: 5)
    HEALTH_CHECK_PORT      - Port for health check HTTP endpoint (default: 8765)

See CREDENTIALS_GUIDE.md for secure setup instructions
"""

import os
import sys
import signal
import subprocess
import time
import json
import logging
import threading
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver

# ⚠️ NEVER commit this file to version control
# See CREDENTIALS_GUIDE.md for secure setup instructions


# =============================================================================
# CONFIGURATION
# =============================================================================

# Paths
VAULT_PATH = Path(__file__).parent
LOGS_DIR = VAULT_PATH / "Logs"
WATCHERS_DIR = VAULT_PATH / "watchers"

# Ensure logs directory exists
LOGS_DIR.mkdir(exist_ok=True)

# Environment variables with defaults
WATCHER_INTERVAL = int(os.getenv("WATCHER_INTERVAL", "60"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", str(LOGS_DIR / "orchestrator.log"))
RESTART_DELAY = int(os.getenv("RESTART_DELAY", "5"))
HEALTH_CHECK_PORT = int(os.getenv("HEALTH_CHECK_PORT", "8765"))

# Watcher configuration
WATCHERS = {
    "gmail_watcher": {
        "script": "gmail_watcher.py",
        "interval": int(os.getenv("GMAIL_WATCHER_INTERVAL", "120")),
        "description": "Gmail Inbox Monitor",
        "enabled": os.getenv("GMAIL_WATCHER_ENABLED", "true").lower() == "true",
    },
    "whatsapp_watcher": {
        "script": "whatsapp_watcher.py",
        "interval": int(os.getenv("WHATSAPP_WATCHER_INTERVAL", "30")),
        "description": "WhatsApp Business Monitor",
        "enabled": os.getenv("WHATSAPP_WATCHER_ENABLED", "true").lower() == "true",
    },
    "office_watcher": {
        "script": "office_watcher.py",
        "interval": int(os.getenv("OFFICE_WATCHER_INTERVAL", "1")),
        "description": "Office Files Monitor",
        "enabled": os.getenv("OFFICE_WATCHER_ENABLED", "true").lower() == "true",
    },
    "social_watcher": {
        "script": "social_watcher.py",
        "interval": int(os.getenv("SOCIAL_WATCHER_INTERVAL", "60")),
        "description": "Social Media Monitor",
        "enabled": os.getenv("SOCIAL_WATCHER_ENABLED", "true").lower() == "true",
    },
    "odoo_lead_watcher": {
        "script": "odoo_lead_watcher.py",
        "interval": int(os.getenv("ODOO_WATCHER_INTERVAL", "300")),
        "description": "Odoo CRM Lead Monitor",
        "enabled": os.getenv("ODOO_WATCHER_ENABLED", "true").lower() == "true",
    },
}


# =============================================================================
# LOGGING SETUP
# =============================================================================

def setup_logging() -> logging.Logger:
    """Setup logging configuration."""
    logger = logging.getLogger("orchestrator")
    logger.setLevel(getattr(logging, LOG_LEVEL.upper()))

    # File handler
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LOG_LEVEL.upper()))

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logging()


# =============================================================================
# WATCHER PROCESS CLASS
# =============================================================================

class WatcherProcess:
    """Manages a single watcher process with auto-restart capability."""

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.script_path = WATCHERS_DIR / config["script"]
        self.process: Optional[subprocess.Popen] = None
        self.start_time: Optional[datetime] = None
        self.restart_count = 0
        self.last_crash_time: Optional[datetime] = None
        self.status = "stopped"
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> bool:
        """Start the watcher process."""
        if not self.script_path.exists():
            logger.error(f"Watcher script not found: {self.script_path}")
            self.status = "error_script_not_found"
            return False

        if self.process and self.process.poll() is None:
            logger.warning(f"Watcher {self.name} is already running")
            return True

        try:
            logger.info(f"Starting watcher: {self.name} ({self.config['description']})")

            # Start process with proper error handling
            self.process = subprocess.Popen(
                [sys.executable, str(self.script_path)],
                cwd=str(WATCHERS_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            self.start_time = datetime.now()
            self.status = "running"
            self.restart_count = 0

            logger.info(f"Watcher {self.name} started with PID {self.process.pid}")
            return True

        except Exception as e:
            logger.error(f"Failed to start watcher {self.name}: {e}")
            self.status = f"error_starting: {str(e)}"
            return False

    def stop(self) -> None:
        """Stop the watcher process gracefully."""
        self._stop_event.set()

        if self.process:
            try:
                logger.info(f"Stopping watcher: {self.name} (PID: {self.process.pid})")

                # Try graceful termination first
                self.process.terminate()

                # Wait up to 10 seconds for graceful shutdown
                try:
                    self.process.wait(timeout=10)
                    logger.info(f"Watcher {self.name} stopped gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if not responding
                    logger.warning(f"Watcher {self.name} not responding, forcing kill")
                    self.process.kill()
                    self.process.wait()

                self.status = "stopped"
                self.process = None

            except Exception as e:
                logger.error(f"Error stopping watcher {self.name}: {e}")
                self.status = f"error_stopping: {str(e)}"

    def check_health(self) -> Dict[str, Any]:
        """Check watcher health status."""
        health = {
            "name": self.name,
            "description": self.config["description"],
            "status": self.status,
            "pid": self.process.pid if self.process else None,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "restart_count": self.restart_count,
            "last_crash": self.last_crash_time.isoformat() if self.last_crash_time else None,
        }

        if self.process:
            # Check if process is still running
            if self.process.poll() is not None:
                # Process has exited
                returncode = self.process.poll()
                if returncode == 0:
                    health["status"] = "exited_normally"
                else:
                    health["status"] = f"crashed_exit_code_{returncode}"
                    self.last_crash_time = datetime.now()

                # Capture any error output
                try:
                    stderr = self.process.stderr.read()
                    if stderr:
                        health["error_output"] = stderr[:500]  # First 500 chars
                except:
                    pass

                self.process = None
                self.status = health["status"]

        return health

    def run_with_watchdog(self) -> None:
        """Run watcher with watchdog pattern (auto-restart on crash)."""
        while not self._stop_event.is_set():
            if not self.process or self.process.poll() is not None:
                # Process has crashed or not started
                if self.start_time:  # Only restart if it was running before
                    self.restart_count += 1
                    self.last_crash_time = datetime.now()

                    logger.warning(
                        f"Watcher {self.name} crashed! "
                        f"Restarting in {RESTART_DELAY} seconds... "
                        f"(Restart count: {self.restart_count})"
                    )

                    # Wait before restarting
                    for _ in range(RESTART_DELAY):
                        if self._stop_event.is_set():
                            break
                        time.sleep(1)

                    if not self._stop_event.is_set():
                        self.start()
                else:
                    # Initial start
                    if not self.start():
                        break
            else:
                # Process is running, wait a bit before checking again
                time.sleep(5)

    def start_thread(self) -> None:
        """Start watcher in a background thread."""
        self._thread = threading.Thread(
            target=self.run_with_watchdog,
            name=f"watcher-{self.name}",
            daemon=True
        )
        self._thread.start()

    def join(self, timeout: float = None) -> None:
        """Wait for watcher thread to complete."""
        if self._thread:
            self._thread.join(timeout=timeout)


# =============================================================================
# ORCHESTRATOR CLASS
# =============================================================================

class Orchestrator:
    """Master orchestrator for all watchers."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.watchers: Dict[str, WatcherProcess] = {}
        self._stop_event = threading.Event()
        self.health_server: Optional[HTTPServer] = None
        self._health_thread: Optional[threading.Thread] = None

        # Initialize watchers
        for name, config in WATCHERS.items():
            if config["enabled"]:
                self.watchers[name] = WatcherProcess(name, config)

    def start_health_server(self) -> None:
        """Start HTTP health check server."""
        orchestrator_instance = self

        class HealthHandler(BaseHTTPRequestHandler):
            """HTTP handler for health check requests."""

            def log_message(self, format, *args):
                """Suppress default logging."""
                pass

            def do_GET(self):
                """Handle GET requests."""
                if self.path == "/health":
                    health_data = orchestrator_instance.get_health_status()
                    response = json.dumps(health_data, indent=2)

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(response.encode())

                elif self.path == "/status":
                    status_data = orchestrator_instance.get_status_summary()
                    response = json.dumps(status_data, indent=2)

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(response.encode())

                else:
                    self.send_response(404)
                    self.end_headers()

        # Use TCPServer with allow_reuse_address
        class ReusableTCPServer(socketserver.TCPServer):
            allow_reuse_address = True

        try:
            self.health_server = ReusableTCPServer(
                ("", HEALTH_CHECK_PORT),
                HealthHandler
            )

            self._health_thread = threading.Thread(
                target=self.health_server.serve_forever,
                name="health-server",
                daemon=True
            )
            self._health_thread.start()

            logger.info(f"Health check server started on port {HEALTH_CHECK_PORT}")
            logger.info(f"  GET http://localhost:{HEALTH_CHECK_PORT}/health")

        except OSError as e:
            logger.warning(f"Could not start health server on port {HEALTH_CHECK_PORT}: {e}")

    def stop_health_server(self) -> None:
        """Stop HTTP health check server."""
        if self.health_server:
            self.health_server.shutdown()
            logger.info("Health check server stopped")

    def start_all_watchers(self) -> None:
        """Start all enabled watchers."""
        if self.dry_run:
            logger.info("[DRY RUN] Would start the following watchers:")
            for name, watcher in self.watchers.items():
                logger.info(f"  - {name}: {watcher.config['description']} "
                          f"(interval: {watcher.config['interval']}s)")
            return

        logger.info(f"Starting {len(self.watchers)} watcher(s)...")

        for name, watcher in self.watchers.items():
            watcher.start_thread()
            # Small delay between watcher starts
            time.sleep(1)

    def stop_all_watchers(self, timeout: float = 10) -> None:
        """Stop all watchers gracefully."""
        logger.info("Stopping all watchers...")

        self._stop_event.set()

        # Stop each watcher
        for name, watcher in self.watchers.items():
            watcher.stop()

        # Wait for all watchers to stop
        for name, watcher in self.watchers.items():
            watcher.join(timeout=timeout / len(self.watchers))

        logger.info("All watchers stopped")

    def get_health_status(self) -> Dict[str, Any]:
        """Get detailed health status for all watchers."""
        status = {
            "timestamp": datetime.now().isoformat(),
            "orchestrator": {
                "version": "1.0.0",
                "dry_run": self.dry_run,
                "uptime_seconds": None,
            },
            "watchers": {},
            "summary": {
                "total": len(self.watchers),
                "running": 0,
                "stopped": 0,
                "error": 0,
            }
        }

        for name, watcher in self.watchers.items():
            health = watcher.check_health()
            status["watchers"][name] = health

            # Update summary
            watcher_status = health["status"]
            if watcher_status == "running":
                status["summary"]["running"] += 1
            elif watcher_status in ["stopped", "exited_normally"]:
                status["summary"]["stopped"] += 1
            else:
                status["summary"]["error"] += 1

        return status

    def get_status_summary(self) -> Dict[str, Any]:
        """Get simplified status summary."""
        health = self.get_health_status()

        summary = {
            "timestamp": health["timestamp"],
            "status": "healthy" if health["summary"]["error"] == 0 else "degraded",
            "watchers": {}
        }

        for name, watcher_health in health["watchers"].items():
            summary["watchers"][name] = watcher_health["status"]

        return summary

    def run(self) -> None:
        """Run the orchestrator main loop."""
        logger.info("=" * 70)
        logger.info("🤖 AI EMPLOYEE WATCHER ORCHESTRATOR")
        logger.info("=" * 70)
        logger.info(f"Vault Path: {VAULT_PATH}")
        logger.info(f"Log Level: {LOG_LEVEL}")
        logger.info(f"Watcher Interval: {WATCHER_INTERVAL}s")
        logger.info(f"Restart Delay: {RESTART_DELAY}s")
        logger.info(f"Dry Run: {self.dry_run}")
        logger.info("=" * 70)

        if self.dry_run:
            self.start_all_watchers()
            logger.info("\n[DRY RUN] Complete! No watchers were actually started.")
            return

        # Start health server
        self.start_health_server()

        # Start all watchers
        self.start_all_watchers()

        logger.info("\n" + "=" * 70)
        logger.info("✅ All watchers started successfully!")
        logger.info("Press Ctrl+C to stop all watchers")
        logger.info("=" * 70)

        # Main loop - keep running until interrupted
        try:
            while not self._stop_event.is_set():
                # Log status every 60 seconds
                time.sleep(60)

                if not self._stop_event.is_set():
                    status = self.get_status_summary()
                    logger.info(f"Status: {status['status']} - "
                              f"Running: {status['summary']['running']}, "
                              f"Errors: {status['summary']['error']}")

        except KeyboardInterrupt:
            logger.info("\n\nReceived interrupt signal")
        finally:
            # Cleanup
            self.stop_all_watchers()
            self.stop_health_server()
            logger.info("Orchestrator shutdown complete")


# =============================================================================
# SIGNAL HANDLERS
# =============================================================================

def setup_signal_handlers(orchestrator_instance: Orchestrator) -> None:
    """Setup graceful shutdown signal handlers."""

    def signal_handler(signum, frame):
        """Handle SIGINT and SIGTERM signals."""
        logger.info(f"\nReceived signal {signum}, initiating graceful shutdown...")
        orchestrator_instance._stop_event.set()

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


# =============================================================================
# CLI FUNCTIONS
# =============================================================================

def check_health_command() -> None:
    """Check health of running orchestrator."""
    try:
        import urllib.request

        url = f"http://localhost:{HEALTH_CHECK_PORT}/health"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            print(json.dumps(data, indent=2))

    except Exception as e:
        print(json.dumps({
            "error": f"Could not connect to orchestrator: {e}",
            "hint": "Is orchestrator running? Start with: python orchestrator.py"
        }, indent=2))
        sys.exit(1)


def stop_command() -> None:
    """Stop running orchestrator."""
    try:
        import urllib.request

        # Send stop request (would need endpoint implementation)
        # For now, just inform user
        print("To stop the orchestrator:")
        print("  1. Find the process: tasklist | findstr python")
        print("  2. Kill the process: taskkill /PID <pid> /F")
        print("\nOr press Ctrl+C if running in foreground")

    except Exception as e:
        print(f"Error: {e}")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI Employee Watcher Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python orchestrator.py              # Start all watchers
  python orchestrator.py --dry-run    # Test configuration
  python orchestrator.py --health     # Check health status
  python orchestrator.py --stop       # Stop all watchers

Environment Variables:
  WATCHER_INTERVAL     - Default watcher interval (default: 60)
  LOG_LEVEL           - Logging level (default: INFO)
  LOG_FILE            - Log file path (default: Logs/orchestrator.log)
  RESTART_DELAY       - Restart delay after crash (default: 5)
  HEALTH_CHECK_PORT   - Health check port (default: 8765)
        """
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test configuration without starting watchers"
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="Check health status of running orchestrator"
    )
    parser.add_argument(
        "--stop",
        action="store_true",
        help="Stop all running watchers"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose (DEBUG) logging"
    )

    args = parser.parse_args()

    # Override log level if verbose
    if args.verbose:
        os.environ["LOG_LEVEL"] = "DEBUG"

    # Handle commands
    if args.health:
        check_health_command()
        return

    if args.stop:
        stop_command()
        return

    # Create and run orchestrator
    orchestrator = Orchestrator(dry_run=args.dry_run)
    setup_signal_handlers(orchestrator)
    orchestrator.run()


if __name__ == "__main__":
    main()
