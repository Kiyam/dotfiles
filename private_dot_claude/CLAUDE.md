# Shared memory

Facts that hold on every machine (Mac, prometheus, apollo) live in the private repo
`~/.claude/shared-memory` (Forgejo `kiyam/claude-memory`), same file format as auto-memory.
A SessionStart hook pulls it and prints its `index.md`, so the index is already in context;
read individual files on demand.

Save a memory there instead of per-project memory when it applies across machines or
projects (homelab, hosts, fleet-wide rules). Run `git -C ~/.claude/shared-memory pull --ff-only`
first, add the file and its index line, then commit and push. If the push is rejected,
`pull --rebase` and push again. If the repo is missing, clone it from
`ssh://git@forgejo.olympus.kiyam.co:222/kiyam/claude-memory.git`.
