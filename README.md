# dotfiles

chezmoi-managed config: zsh, ghostty, aerospace, neovim, herdr, tmux, and Claude Code
(settings, hooks, skills, statusline, research-wiki tooling).

## Install on a new Mac

1. Xcode command line tools: `xcode-select --install`
2. Homebrew: see https://brew.sh
3. Apply the dotfiles, then install packages:
   ```sh
   brew install chezmoi
   chezmoi init --apply <github-user>   # clones <github-user>/dotfiles
   brew bundle --file="$(chezmoi source-path)/Brewfile"
   ```
4. Install the non-Homebrew dependencies below.
5. Open a new shell.

## Non-Homebrew dependencies

| What | Install | Used by |
|---|---|---|
| Claude Code | `curl -fsSL https://claude.ai/install.sh \| bash` | everything under `~/.claude` |
| oh-my-zsh | https://ohmyz.sh | `.zshrc` |
| zsh plugins | `git clone https://github.com/zsh-users/zsh-autosuggestions ~/.oh-my-zsh/custom/plugins/zsh-autosuggestions`<br>`git clone https://github.com/zsh-users/zsh-syntax-highlighting ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting`<br>`git clone https://github.com/jeffreytse/zsh-vi-mode ~/.oh-my-zsh/custom/plugins/zsh-vi-mode` | `plugins=(...)` in `.zshrc` |
| rustup | https://rustup.rs | `.zshrc` sources `~/.cargo/env` unconditionally, errors without it |
| node | `nvm install --lts` | nvm, Claude plugins |
| hunk | installer from the hunk project, lands in `~/.hunk/bin` | herdr diff plugin, `/hunk` |
| tpm | `git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm` | tmux plugins (only if using tmux) |
| mcp-ads-arxiv | `uv tool install git+https://github.com/estevesjh/mcp-ads-arxiv --with 'bibtexparser<2'` | `~/.local/bin/research-ads-mcp` |
| zotero-mcp | `uv tool install zotero-mcp-server` | `~/.local/bin/research-zotero-mcp` |
| pyright, pymupdf | `uv tool install pyright` and `uv tool install pymupdf` | pyright-lsp plugin, arxiv-rag skill |

Claude Code and herdr plugins install themselves on `chezmoi apply` (the `run_onchange_*`
scripts), once `claude` and `herdr` are on PATH. Rerun `chezmoi apply` after step 4 if they
were missing the first time.

## Machine-specific parts

Hostname gates in `.chezmoiignore`, `dot_zshrc.tmpl`, `dot_bashrc.tmpl` and
`private_settings.json.tmpl` decide what applies where. Research secrets
(`~/.config/research/secrets.env`) are age-encrypted and only decrypt on the owner's machines.
