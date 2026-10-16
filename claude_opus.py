# Claude Opus 5 via `claude -p` (Claude Code headless mode) — same shape as nemotron_nano.py
# Runs on your Claude subscription login, so no API credit is needed
# Run:  .venv/bin/python claude_opus.py
import json
import subprocess

SYSTEM_PROMPT = """SYSTEM_PROMPT"""
USER_MESSAGE = """USER_MESSAGE"""

result = subprocess.run(
    [
        "claude", "-p",
        "--model", "claude-opus-5",
        "--system-prompt", SYSTEM_PROMPT,
        "--output-format", "json",
        # Plain model call: no tools, MCP servers, hooks, plugins or saved session.
        # Without these, every call carries ~134k tokens of Claude Code context instead of ~450.
        "--tools", "",
        "--strict-mcp-config",
        "--setting-sources", "",
        "--no-session-persistence",
    ],
    input=USER_MESSAGE,  # prompt via stdin, so long or multi-line messages are safe
    capture_output=True,
    text=True,
    check=True,
)

response = json.loads(result.stdout)
print(json.dumps(response, indent=2))
