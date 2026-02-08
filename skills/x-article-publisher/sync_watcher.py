#!/usr/bin/env python3
"""
File watcher for x-article sync mode.

Polls a markdown file's mtime and writes change events to a JSON state file.
Runs as a background process. Claude Code checks the state file between turns
to detect changes and re-push content to the X Articles editor.

Zero external dependencies — uses only stdlib.

Usage:
    python3 sync_watcher.py /path/to/article.md [--state /tmp/x-article-sync.json] [--interval 1]
    python3 sync_watcher.py --stop [--state /tmp/x-article-sync.json]
"""

import argparse
import json
import os
import signal
import sys
import time
from typing import Optional

DEFAULT_STATE_FILE = "/tmp/x-article-sync.json"
DEFAULT_INTERVAL = 1  # seconds


def write_state(state_file: str, data: dict) -> None:
    """Atomically write state to JSON file."""
    tmp = state_file + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, state_file)


def read_state(state_file: str) -> Optional[dict]:
    """Read state from JSON file, returns None if missing or corrupt."""
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def cleanup(state_file: str) -> None:
    """Remove state file on shutdown."""
    try:
        os.unlink(state_file)
    except FileNotFoundError:
        pass


def watch(filepath: str, state_file: str, interval: float) -> None:
    """Poll file mtime and write changes to state file."""
    filepath = os.path.abspath(os.path.expanduser(filepath))

    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    pid = os.getpid()
    last_mtime = os.stat(filepath).st_mtime
    change_count = 0
    running = True

    def handle_signal(signum, frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    # Write initial state
    state = {
        "filepath": filepath,
        "pid": pid,
        "last_mtime": last_mtime,
        "last_change": None,
        "change_count": 0,
        "status": "watching",
    }
    write_state(state_file, state)
    print(f"Watching: {filepath} (pid={pid}, state={state_file})")

    try:
        while running:
            time.sleep(interval)
            try:
                current_mtime = os.stat(filepath).st_mtime
            except FileNotFoundError:
                # File deleted — keep watching in case it comes back
                continue

            if current_mtime != last_mtime:
                last_mtime = current_mtime
                change_count += 1
                state.update({
                    "last_mtime": current_mtime,
                    "last_change": time.time(),
                    "change_count": change_count,
                })
                write_state(state_file, state)
                print(f"Change #{change_count} detected at {time.strftime('%H:%M:%S')}")
    finally:
        cleanup(state_file)
        print("Watcher stopped.")


def stop(state_file: str) -> None:
    """Stop a running watcher by reading PID from state file."""
    state = read_state(state_file)
    if state is None:
        print("No active watcher found.", file=sys.stderr)
        sys.exit(1)

    pid = state.get("pid")
    if pid is None:
        print("State file has no PID.", file=sys.stderr)
        sys.exit(1)

    try:
        os.kill(pid, signal.SIGTERM)
        print(f"Sent SIGTERM to watcher (pid={pid}).")
    except ProcessLookupError:
        print(f"Watcher (pid={pid}) is not running. Cleaning up state file.")
        cleanup(state_file)
    except PermissionError:
        print(f"Permission denied sending signal to pid={pid}.", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="File watcher for x-article sync mode")
    parser.add_argument("filepath", nargs="?", help="Markdown file to watch")
    parser.add_argument("--state", default=DEFAULT_STATE_FILE, help="State file path")
    parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL, help="Poll interval in seconds")
    parser.add_argument("--stop", action="store_true", help="Stop a running watcher")

    args = parser.parse_args()

    if args.stop:
        stop(args.state)
    elif args.filepath:
        watch(args.filepath, args.state, args.interval)
    else:
        parser.error("Either provide a filepath to watch or use --stop")


if __name__ == "__main__":
    main()
