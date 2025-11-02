#!/usr/bin/env python3
"""
dispatch.py

This script provides a convenience wrapper to launch multiple tasks in
parallel. It reads the orchestrator configuration and uses the
`bin/kick-task` script to create branches, commit a task file and open
a pull request via the GitHub CLI. After kicking off tasks, it can
optionally start the watcher to wait for updates or merges.

Usage:
    python3 orchestrator/dispatch.py kickoff --feature FEATURE_ID --tasks task001=src/api/** task002=src/ui/**
    python3 orchestrator/dispatch.py watch --owner OWNER --repo REPO --prs 12,13

Tasks are specified as key=value pairs where the key is the slug and the
value is the allowed path glob. The description/title defaults to the slug.
"""

import argparse
import subprocess
import sys
from pathlib import Path
import concurrent.futures


ROOT = Path(__file__).resolve().parents[1]

def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout

def kick_task(feature: str, slug: str, allowed: str, title: str | None = None) -> str:
    """Call bin/kick-task to create a task branch and PR. Returns the output."""
    script = ROOT / "bin" / "kick-task"
    if not script.exists():
        raise FileNotFoundError("kick-task script not found. Did you bootstrap the project?")
    args = ["bash", str(script), feature, slug, allowed, title or slug]
    return run(args)

def kickoff(args: argparse.Namespace) -> None:
    tasks = []
    for pair in args.tasks:
        if '=' not in pair:
            print(f"Invalid task spec: {pair}. Use slug=path.")
            continue
        slug, path = pair.split('=', 1)
        tasks.append((slug, path, slug))
    # Launch tasks concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, len(tasks))) as ex:
        futures = {ex.submit(kick_task, args.feature, slug, path, title): slug for slug, path, title in tasks}
        for future in concurrent.futures.as_completed(futures):
            slug = futures[future]
            try:
                output = future.result()
                print(f"Kicked task {slug}:\n{output}")
            except Exception as e:
                print(f"Error kicking task {slug}: {e}")

def watch(args: argparse.Namespace) -> None:
    # Defer to wait_and_merge script
    cmd = [
        sys.executable,
        str(ROOT / "orchestrator" / "wait_and_merge.py"),
        "--owner", args.owner,
        "--repo", args.repo,
        "--prs", args.prs,
        "--timeout", str(args.timeout),
        "--interval", str(args.interval),
        "--mode", args.mode
    ]
    if args.auto_merge:
        cmd.append("--auto-merge")
    run(cmd)

def main() -> None:
    parser = argparse.ArgumentParser(description="Dispatch orchestrator commands")
    sub = parser.add_subparsers(dest="cmd")
    # kickoff
    kickoff_parser = sub.add_parser("kickoff", help="Kick off multiple tasks")
    kickoff_parser.add_argument("--feature", required=True, help="Feature identifier")
    kickoff_parser.add_argument("tasks", nargs='+', help="Tasks as slug=allowed_path pairs")
    kickoff_parser.set_defaults(func=kickoff)
    # watch
    watch_parser = sub.add_parser("watch", help="Watch PRs for updates/merges")
    watch_parser.add_argument("--owner", required=True)
    watch_parser.add_argument("--repo", required=True)
    watch_parser.add_argument("--prs", required=True)
    watch_parser.add_argument("--timeout", type=int, default=1800)
    watch_parser.add_argument("--interval", type=int, default=20)
    watch_parser.add_argument("--mode", choices=["any", "all"], default="any")
    watch_parser.add_argument("--auto-merge", action="store_true")
    watch_parser.set_defaults(func=watch)
    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return
    args.func(args)

if __name__ == "__main__":
    main()