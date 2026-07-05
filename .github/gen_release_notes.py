#!/usr/bin/env python3
"""Generate categorized release notes from conventional commit messages.

Usage: python gen_release_notes.py -v v0.1.0...v0.2.0
       python gen_release_notes.py -v "...v0.1.0"   (first release, all history)

Writes release.md in the working directory.
Sections: What's Changed (features), Bug Fixes, Maintenance.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys


def git_log(range_str: str, grep_pattern: str, repo_url: str) -> list[str]:
    """Return sorted, deduplicated commit lines for a given commit-type filter."""
    fmt = f"* [%h]({repo_url}/commit/%H) %s by @%an"
    try:
        result = subprocess.run(
            ["git", "log", "--pretty", fmt, "--grep", grep_pattern, "-i", range_str],
            capture_output=True, text=True, check=True,
        )
    except subprocess.CalledProcessError:
        return []
    lines = sorted(set(result.stdout.strip().splitlines()), key=str.casefold)
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate release notes from git log")
    parser.add_argument("-v", "--version", required=True,
                        help="Version range (prev...curr) or ...curr for first release")
    args = parser.parse_args()

    version_range = args.version

    # Parse prev and curr from the range string
    if "..." in version_range:
        parts = version_range.split("...", 1)
        prev = parts[0]
        curr = parts[1]
    else:
        prev = ""
        curr = version_range

    repo_url = f"https://github.com/{os.environ.get('GITHUB_REPOSITORY', 'Ladbaby/HUAWEI_Router_Assistant')}"

    # For first release (no prev), use the tag directly instead of A...B range
    if not prev:
        log_range = curr
    else:
        log_range = f"{prev}...{curr}"

    lines: list[str] = []
    lines.append("# What's New")
    lines.append("")

    # Features
    lines.append("## What's Changed")
    lines.append("")
    lines.extend(git_log(log_range, "^feat", repo_url))
    lines.append("")

    # Bug fixes
    lines.append("## Bug Fixes")
    lines.append("")
    lines.extend(git_log(log_range, "^fix", repo_url))
    lines.append("")

    # Maintenance (ci, chore, docs, refactor, test)
    lines.append("## Maintenance")
    lines.append("")
    lines.extend(git_log(log_range, "^ci\\|^chore\\|^docs\\|^refactor\\|^test", repo_url))
    lines.append("")

    # Footer with changelog link
    if prev:
        lines.append(f"**Full Changelog**: {repo_url}/compare/{prev}...{curr}")
    else:
        lines.append(f"**Full Changelog**: {repo_url}/releases/tag/{curr}")

    output = "\n".join(lines) + "\n"
    with open("release.md", "w", encoding="utf-8") as f:
        f.write(output)
    print(output, end="")


if __name__ == "__main__":
    main()
