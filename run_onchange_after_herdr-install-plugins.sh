#!/bin/sh
# Install audited herdr plugins pinned to reviewed commits; reruns when a ref changes.
PATH="$HOME/.local/bin:/opt/homebrew/bin:$PATH"
command -v herdr >/dev/null || exit 0
herdr plugin install -y --ref ac5eef7cec6a65fbf8f0c9bbd61b4383489beba5 jhochenbaum/herdr-hunk-diff
herdr plugin install -y --ref 742db891e7d1f9a550b16c01dc8a6763f2b1493a paulbkim-dev/vim-herdr-navigation
