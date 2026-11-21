#!/bin/sh
# Install Claude Code plugins enabled in settings.json; reruns when this list changes.
PATH="$HOME/.local/bin:/opt/homebrew/bin:$PATH"
command -v claude >/dev/null || exit 0
set -e
for p in claude-md-management pyright-lsp session-report swift-lsp; do
  claude plugin install "$p@claude-plugins-official" >/dev/null
done
# Third-party marketplaces are declared in settings.json (extraKnownMarketplaces)
for p in caveman@caveman ponytail@ponytail; do
  claude plugin install "$p" >/dev/null
done
