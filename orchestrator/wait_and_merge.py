#!/usr/bin/env python3
"""
wait_and_merge.py

This script monitors one or more GitHub pull requests until they update or
become mergeable. It uses the GitHub REST API. When the specified PRs
report a successful status and a clean mergeable state, the script can
optionally merge them automatically. If the timeout expires without
seeing an update, the script exits with a nonzero code so a caller can
decide whether to rerun.

This is a simplified implementation intended for local orchestration. It
expects a valid `GITHUB_TOKEN` environment variable.

Usage:
    python3 orchestrator/wait_and_merge.py --owner OWNER --repo REPO --prs 12,13 [--timeout 3600] [--interval 30] [--mode any|all] [--auto-merge]

"""

import argparse
import os
import time
from datetime import datetime, timedelta
import requests


GITHUB_API = "https://api.github.com"


def gh_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

def pr_status(owner: str, repo: str, pr: int, headers: dict[str, str]) -> tuple[str, str, str]:
    """Return (updated_at, mergeable_state, status_state) for a PR."""
    pr_url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr}"
    r = requests.get(pr_url, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    updated_at = data["updated_at"]
    mergeable_state = data.get("mergeable_state") or ""  # clean, dirty, etc.
    head_sha = data["head"]["sha"]
    # Get combined status
    checks_url = f"{GITHUB_API}/repos/{owner}/{repo}/commits/{head_sha}/status"
    c = requests.get(checks_url, headers=headers, timeout=30)
    c.raise_for_status()
    checks_state = c.json().get("state", "pending")
    return updated_at, mergeable_state, checks_state

def attempt_merge(owner: str, repo: str, pr: int, headers: dict[str, str], method: str) -> bool:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr}/merge"
    r = requests.put(url, headers=headers, json={"merge_method": method}, timeout=30)
    return r.status_code in (200, 204)

def main() -> None:
    parser = argparse.ArgumentParser(description="Wait for PRs to update and optionally merge.")
    parser.add_argument("--owner", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--prs", required=True, help="Comma‑separated list of PR numbers to watch")
    parser.add_argument("--timeout", type=int, default=3600, help="Seconds to wait before timing out")
    parser.add_argument("--interval", type=int, default=30, help="Seconds between polls")
    parser.add_argument("--mode", choices=["any", "all"], default="any", help="Return when any or all PRs update")
    parser.add_argument("--auto-merge", action="store_true", help="Automatically merge when status is success and mergeable is clean")
    parser.add_argument("--merge-method", choices=["merge", "squash", "rebase"], default="squash", help="Merge method to use if auto merging")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN environment variable is required")
    headers = gh_headers(token)
    pr_nums = [int(x.strip()) for x in args.prs.split(",") if x.strip()]

    deadline = datetime.utcnow() + timedelta(seconds=args.timeout)
    updated_prs: set[int] = set()
    merged_prs: set[int] = set()

    while datetime.utcnow() < deadline:
        for pr in pr_nums:
            try:
                updated_at, mergeable, status = pr_status(args.owner, args.repo, pr, headers)
                # If there is a new commit or status update, consider it updated
                updated_prs.add(pr)
                if status == "success" and mergeable in ("clean", "unstable"):
                    if args.auto_merge and pr not in merged_prs:
                        ok = attempt_merge(args.owner, args.repo, pr, headers, args.merge_method)
                        if ok:
                            merged_prs.add(pr)
            except Exception:
                pass
        # Termination conditions
        if args.mode == "any" and updated_prs:
            break
        if args.mode == "all" and all(p in updated_prs for p in pr_nums):
            break
        time.sleep(args.interval)

    # Print summary
    print("UPDATED:", sorted(updated_prs))
    if args.auto_merge:
        print("MERGED:", sorted(merged_prs))
    # Exit code 0 if any updated (for mode any) or all updated (for mode all), else 1
    if (args.mode == "any" and updated_prs) or (args.mode == "all" and all(p in updated_prs for p in pr_nums)):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()