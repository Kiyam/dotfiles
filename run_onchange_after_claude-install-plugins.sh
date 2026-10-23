#!/bin/sh
# Install Claude Code plugins enabled in settings.json; reruns when this list changes.
PATH="$HOME/.local/bin:/opt/homebrew/bin:$PATH"
command -v claude >/dev/null || exit 0
for p in claude-md-management pyright-lsp session-report; do
  claude plugin install "$p@claude-plugins-official" >/dev/null
done
