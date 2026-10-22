#!/bin/sh
# Popup for kiyam.close-pane: herdr passes the pane under the popup in HERDR_PLUGIN_CONTEXT_JSON.
herdr=${HERDR_BIN_PATH:-herdr}
eval "$(printf '%s' "$HERDR_PLUGIN_CONTEXT_JSON" | jq -r '@sh "pane=\(.focused_pane_id // "") agent=\(.focused_pane_agent // "") cwd=\(.focused_pane_cwd // "") ws=\(.workspace_label // .workspace_id // "") tab=\(.tab_label // .tab_id // "")"')"
[ -n "$pane" ] || { echo "No focused pane found."; sleep 2; exit 1; }
title=$("$herdr" pane get "$pane" | jq -r '.result.pane.terminal_title_stripped // empty')
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
printf '  %s%s%s\n\n' "$d" "$(trunc "$ws › $tab")" "$x"
printf '  %s%sy%s close     %sany other key%s cancel' "$b" "$r" "$x" "$d" "$x"

stty raw -echo; ans=$(dd bs=1 count=1 2>/dev/null); stty -raw echo
printf '\033[?25h'
case "$ans" in y|Y) "$herdr" pane close "$pane" >/dev/null ;; esac
