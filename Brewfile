# Homebrew packages the dotfiles in this repo depend on (macOS). Install: brew bundle
# Not a dump of everything installed, only what the configs call. Non-brew deps: README.md.

tap "nikitabobko/tap"
tap "felixkratz/formulae"

# shell: .zshrc errors or degrades on startup without these
brew "spaceship"      # prompt, sourced directly
brew "zoxide"         # replaces cd
brew "atuin"          # shell history
brew "vivid"          # LS_COLORS
brew "carapace"       # completions
brew "fzf"
brew "fd"             # fzf backend
brew "bat"            # fzf previews
brew "eza"            # ls alias
brew "duf"            # df alias
brew "nvm"

# tools
brew "chezmoi"
brew "neovim"
brew "herdr"
brew "tmux"           # optional, herdr is the main multiplexer
brew "uv"             # MCP servers, pyright, arxiv-rag skill
brew "pandoc"         # arxiv-rag skill
brew "gh"             # wizard skill, optional

# GUI
cask "ghostty"
cask "font-space-mono-nerd-font"  # ghostty font
cask "aerospace"
brew "borders"                    # launched by aerospace.toml
cask "obsidian"                   # research vault
cask "zotero"                     # papers, local API for zotero-mcp
cask "mactex-no-gui"              # vimtex (basictex is a smaller alternative)
cask "skim"                       # vimtex PDF viewer
