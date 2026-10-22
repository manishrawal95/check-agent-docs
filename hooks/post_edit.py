#!/usr/bin/env python3
"""PostToolUse hook: when an agent instruction file was just edited, run the local checks on it.

Prints findings to stderr and exits 2 so Claude sees them; exits 0 silently otherwise. Never blocks on errors.
"""
import json
import os
import re
import subprocess
import sys

NAMES = re.compile(r"(^|/)(CLAUDE\.md|AGENTS\.md|GEMINI\.md|\.cursorrules|\.windsurfrules|\.clinerules|"
                   r"copilot-instructions\.md|[^/]+\.instructions\.md)$|(^|/)\.(cursor/rules|windsurf/rules|clinerules)/")


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    tool_input = event.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("path") or ""
    if not path or not NAMES.search(path.replace(os.sep, "/")):
        return 0
    root = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cwd = event.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    try:
        r = subprocess.run([sys.executable, os.path.join(root, "check_agent_docs.py"), cwd, "--no-llm", "--only", path,
                            "--format", "json"], capture_output=True, text=True, timeout=25)
        res = json.loads(r.stdout)
    except (subprocess.SubprocessError, ValueError, OSError):
        return 0  # a broken check must never get in the way of editing
    issues = res.get("issues") or []
    if not issues:
        return 0
    lines = [f"check-agent-docs: {len(issues)} claim(s) in {res['checked_files'][0]} don't match the repo:"]
    for i in issues[:10]:
        fix = f" (suggested: {i['suggested_fix']})" if i.get("suggested_fix") else ""
        lines.append(f"  line {i['line']}: {i['claim']} - {i['problem']}{fix}")
    lines.append("Fix these if they are mistakes, or add <!-- check-agent-docs-disable-next-line --> above an intended example.")
    print("\n".join(lines), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
