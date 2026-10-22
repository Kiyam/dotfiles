#!/bin/bash
# Combined statusline: caveman + ponytail badges + usage from Claude Code's own rate_limits JSON.
INPUT=$(cat)

CAVEMAN=$(printf '%s' "$INPUT" | bash "$HOME/.claude/plugins/marketplaces/caveman/src/hooks/caveman-statusline.sh" 2>/dev/null)
PONYTAIL=$(bash "$HOME/.claude/plugins/marketplaces/ponytail/hooks/ponytail-statusline.sh" 2>/dev/null)
BADGES="$CAVEMAN${CAVEMAN:+${PONYTAIL:+ }}$PONYTAIL"

USAGE=$(printf '%s' "$INPUT" | jq -r '
  def col(p): if p >= 90 then "\u001b[31m" elif p >= 75 then "\u001b[33m" else "\u001b[32m" end;
  def eta(t): (t - now | floor) as $s
    | if $s < 60 then "\($s)s" elif $s < 3600 then "\($s/60|floor)m"
      elif $s < 86400 then "\($s/3600|floor)h\(($s%3600)/60|floor)m" else "\($s/86400|floor)d" end;
  [ (.rate_limits.five_hour // empty | col(.used_percentage) + "session \(.used_percentage|round)%\u001b[0m\u001b[2m · \(eta(.resets_at))\u001b[0m"),
    (.rate_limits.seven_day // empty | col(.used_percentage) + "weekly \(.used_percentage|round)%\u001b[0m"),
    (.cost.total_cost_usd // empty | "\u001b[2m$\(. * 100 | round / 100) session\u001b[0m")
  ] | join(" · ")' 2>/dev/null)

if [ -n "$BADGES" ] && [ -n "$USAGE" ]; then
  printf '%s  \033[2m·\033[0m  %s' "$BADGES" "$USAGE"
elif [ -n "$BADGES" ]; then
  printf '%s' "$BADGES"
else
  printf '%s' "$USAGE"
fi
