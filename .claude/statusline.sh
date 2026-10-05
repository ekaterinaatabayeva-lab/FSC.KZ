#!/usr/bin/env bash
# Статус-лайн Claude Code: модель, контекст и расход лимитов подписки.
# Получает JSON сессии на stdin. Нужен jq.

input=$(cat)

if ! command -v jq >/dev/null 2>&1; then
  echo "statusline: установите jq"
  exit 0
fi

model=$(jq -r '.model.display_name // "Claude"' <<<"$input")
ctx=$(jq -r '.context_window.used_percentage // empty' <<<"$input")

# Цвет по уровню заполнения: зелёный < 50, жёлтый < 80, красный >= 80
color() {
  local p=${1%.*}
  if   (( p >= 80 )); then printf '\033[31m'
  elif (( p >= 50 )); then printf '\033[33m'
  else                     printf '\033[32m'
  fi
}

# Полоска из 10 делений: ▰▰▰▱▱▱▱▱▱▱
bar() {
  local p=${1%.*} filled i out=""
  (( p > 100 )) && p=100
  filled=$(( (p + 5) / 10 ))
  for (( i = 0; i < 10; i++ )); do
    if (( i < filled )); then out+="▰"; else out+="▱"; fi
  done
  printf '%s' "$out"
}

# Время до сброса лимита: «2ч 15м» или «3д 4ч»
until_reset() {
  local left=$(( $1 - $(date +%s) ))
  (( left < 0 )) && left=0
  local d=$(( left / 86400 )) h=$(( left % 86400 / 3600 )) m=$(( left % 3600 / 60 ))
  if   (( d > 0 )); then printf '%dд %dч' "$d" "$h"
  elif (( h > 0 )); then printf '%dч %dм' "$h" "$m"
  else                   printf '%dм' "$m"
  fi
}

reset=$'\033[0m'
dim=$'\033[2m'

limit() {
  local label=$1 key=$2 pct resets
  pct=$(jq -r ".rate_limits.$key.used_percentage // empty" <<<"$input")
  [[ -z $pct ]] && return
  resets=$(jq -r ".rate_limits.$key.resets_at // empty" <<<"$input")
  printf ' │ %s %s%s %d%%%s' "$label" "$(color "$pct")" "$(bar "$pct")" "${pct%.*}" "$reset"
  [[ -n $resets ]] && printf ' %s↻ %s%s' "$dim" "$(until_reset "$resets")" "$reset"
}

line="$model"
[[ -n $ctx ]] && line+=" │ контекст $(color "$ctx")${ctx%.*}%${reset}"

limits="$(limit "5ч" five_hour)$(limit "неделя" seven_day)$(limit "бюджет" spend_limit)"
if [[ -n $limits ]]; then
  line+="$limits"
else
  line+=" │ ${dim}лимит: нет данных${reset}"
fi

printf '%s\n' "$line"
