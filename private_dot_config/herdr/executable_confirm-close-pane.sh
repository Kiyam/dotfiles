#!/bin/sh
PATH="$HOME/.local/bin:/opt/homebrew/bin:$PATH"
# Ask before closing the focused herdr pane (bound to prefix+x in config.toml).
pane=$(herdr pane list | jq -r '.result.panes[] | select(.focused) | .pane_id' | head -n1)
[ -n "$pane" ] || { echo "No focused pane found."; sleep 2; exit 1; }
eval "$(herdr pane get "$pane" | jq -r '.result.pane | @sh "title=\(.terminal_title_stripped // "") agent=\(.agent // "") cwd=\(.foreground_cwd // .cwd // "") ws_id=\(.workspace_id) tab_id=\(.tab_id)"')"
ws=$(herdr workspace get "$ws_id" | jq -r '.result.workspace.label // empty')
tab=$(herdr tab get "$tab_id" | jq -r '.result.tab.label // empty')
cwd=$(printf '%s' "$cwd" | sed "s|^$HOME|~|")
[ -n "$title" ] || title="(untitled)"
w=$(( $(tput cols) - 6 ))
trunc() { printf '%s' "$1" | cut -c1-"$w"; }

b=$(printf '\033[1m'); d=$(printf '\033[2m'); r=$(printf '\033[31m'); c=$(printf '\033[36m'); x=$(printf '\033[0m')
printf '\033[?25l\n'
printf '  %s%s⚠  Close this pane?%s\n\n' "$b" "$r" "$x"
printf '  %s%s%s\n' "$b" "$(trunc "$title")" "$x"
[ -n "$agent" ] && printf '  %s●%s %s\n' "$c" "$x" "$agent"
printf '  %s%s%s\n' "$d" "$(trunc "$cwd")" "$x"
printf '  %s%s%s\n\n' "$d" "$(trunc "${ws:-$ws_id} › ${tab:-$tab_id}")" "$x"
printf '  %s%sy%s close     %sany other key%s cancel' "$b" "$r" "$x" "$d" "$x"

stty raw -echo; ans=$(dd bs=1 count=1 2>/dev/null); stty -raw echo
printf '\033[?25h'
case "$ans" in y|Y) herdr pane close "$pane" >/dev/null ;; esac
