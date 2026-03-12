#!/usr/bin/env bash
# Hook: intercept rm -r / rm -rf commands and require explicit user confirmation.
# Receives tool input JSON on stdin; exits 0 to allow, exits 2 to block.

set -euo pipefail

input=$(cat)
command=$(echo "$input" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('command',''))" 2>/dev/null || true)

# Match rm with recursive flags anywhere in the command
if echo "$command" | grep -qE '(^|[;&|`(]|\bsudo\b)\s*rm\s+[^;]*-[a-zA-Z]*r'; then
  # Write prompt directly to the terminal, bypassing stdout (which Claude reads)
  exec 3>/dev/tty
  echo "" >&3
  echo "⚠️  Claude wants to run a recursive rm command:" >&3
  echo "   $command" >&3
  echo "" >&3
  printf "Allow this? [y/N] " >&3
  exec 3>&-

  # Read the answer from the terminal
  read -r answer </dev/tty

  if [[ "$answer" =~ ^[Yy]$ ]]; then
    exit 0
  else
    echo "User denied recursive rm. Command was: $command"
    exit 2
  fi
fi

exit 0
