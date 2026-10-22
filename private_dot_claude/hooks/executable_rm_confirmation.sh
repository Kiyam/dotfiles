#!/usr/bin/env bash
# Hook: intercept rm -r / rm -rf commands and require explicit user confirmation.
# Receives the PreToolUse JSON on stdin; the command is at .tool_input.command.
# Replies with permissionDecision "ask", so Claude Code shows its own prompt
# (also in auto mode) instead of this script reading /dev/tty under the TUI.

set -euo pipefail

input=$(cat)
command=$(echo "$input" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null || true)

# Match rm with recursive flags anywhere in the command
if echo "$command" | grep -qE '(^|[;&|`(]|\bsudo\b)\s*rm\s+[^;]*(-[a-zA-Z]*[rR]|--recursive)'; then
  python3 -c 'import json,sys; print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask", "permissionDecisionReason": "Recursive rm: confirm before running:\n" + sys.argv[1]}}))' "$command"
fi

exit 0
