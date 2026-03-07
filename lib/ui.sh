#!/bin/bash
# ============================================================
#   lib/ui.sh — Premium Dashboard UI Engine
# ============================================================

# ── Colors ───────────────────────────────────────────────────
RESET="\033[0m";  BOLD="\033[1m";  DIM="\033[2m"
RED="\033[91m";    GREEN="\033[92m"
YELLOW="\033[93m"; BLUE="\033[94m"
MAGENTA="\033[95m"; CYAN="\033[96m"
WHITE="\033[97m";  BLACK="\033[30m"

# ── Symbols ──────────────────────────────────────────────────
OK="✔";  FAIL="✖";  INFO="ℹ";  WARN="⚠"
ARROW="➜";  DOT="•";  STEP="◆"

# ── Terminal width ────────────────────────────────────────────
COLS=$(tput cols 2>/dev/null || echo 80)
[[ $COLS -gt 80 ]] && COLS=80

# ─────────────────────────────────────────────────────────────
#   Layout Helpers
# ─────────────────────────────────────────────────────────────

draw_line() {
  local char="${1:-─}" color="${2:-$DIM}"
  echo -e "${color}$(printf "%${COLS}s" | tr ' ' "$char")${RESET}"
}

center_text() {
  local text="$1"
  local clean; clean=$(echo -e "$text" | sed 's/\x1b\[[0-9;]*m//g')
  local pad=$(( (COLS - ${#clean}) / 2 ))
  [[ $pad -lt 0 ]] && pad=0
  printf "%${pad}s%b\n" "" "$text"
}

# ─────────────────────────────────────────────────────────────
#   Banner (The Classic Big Title)
# ─────────────────────────────────────────────────────────────

show_banner() {
  clear
  echo ""
  center_text "${CYAN}${BOLD} ██╗      █████╗ ██████╗  █████╗ ██╗   ██╗███████╗██╗     ${RESET}"
  center_text "${CYAN}${BOLD} ██║     ██╔══██╗██╔══██╗██╔══██╗██║   ██║██╔════╝██║     ${RESET}"
  center_text "${CYAN}${BOLD} ██║     ███████║██████╔╝███████║██║   ██║█████╗  ██║     ${RESET}"
  center_text "${CYAN}${BOLD} ██║     ██╔══██║██╔══██╗██╔══██║╚██╗ ██╔╝██╔══╝  ██║     ${RESET}"
  center_text "${CYAN}${BOLD} ███████╗██║  ██║██║  ██║██║  ██║ ╚████╔╝ ███████╗███████╗${RESET}"
  center_text "${CYAN}${BOLD} ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚══════╝${RESET}"
  echo ""
  center_text "${WHITE}${BOLD}          ██████╗ ███████╗██╗   ██╗    ███████╗███████╗████████╗██╗   ██╗██████╗ ${RESET}"
  center_text "${WHITE}${BOLD}          ██╔══██╗██╔════╝██║   ██║    ██╔════╝██╔════╝╚══██╔══╝██║   ██║██╔══██╗${RESET}"
  center_text "${WHITE}${BOLD}          ██║  ██║█████╗  ██║   ██║    ███████╗█████╗     ██║   ██║   ██║██████╔╝${RESET}"
  center_text "${WHITE}${BOLD}          ██║  ██║██╔══╝  ╚██╗ ██╔╝    ╚════██║██╔══╝     ██║   ██║   ██║██╔═══╝ ${RESET}"
  center_text "${WHITE}${BOLD}          ██████╔╝███████╗ ╚████╔╝     ███████║███████╗   ██║   ╚██████╔╝██║     ${RESET}"
  center_text "${WHITE}${BOLD}          ╚═════╝ ╚══════╝  ╚═══╝      ╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝     ${RESET}"
  echo ""
  draw_line "━" "$CYAN"
}

# ─────────────────────────────────────────────────────────────
#   Dashboard Components
# ─────────────────────────────────────────────────────────────

section() {
  echo -e "\n ${MAGENTA}${BOLD}${STEP} ${WHITE}${1}${RESET}"
  draw_line "─" "$DIM"
}

msg_ok()   { echo -e "   ${GREEN}${BOLD}${OK}${RESET}  ${WHITE}${1}${RESET}"; }
msg_fail() { echo -e "   ${RED}${BOLD}${FAIL}${RESET}  ${RED}${1}${RESET}"; }
msg_info() { echo -e "   ${CYAN}${BOLD}${INFO}${RESET}  ${DIM}${1}${RESET}"; }
msg_warn() { echo -e "   ${YELLOW}${BOLD}${WARN}${RESET}  ${YELLOW}${1}${RESET}"; }

# ─────────────────────────────────────────────────────────────
#   Interactive Prompts (Fix for /dev/tty)
# ─────────────────────────────────────────────────────────────

prompt_confirm() {
  local q="$1" def="${2:-y}" ans
  local hint="[Y/n]"
  [[ "$def" == "n" ]] && hint="[y/N]"
  echo ""
  echo -ne "   ${BOLD}${WHITE}${q}${RESET} ${DIM}${hint}${RESET} ${CYAN}${ARROW}${RESET} "
  # Read from /dev/tty to support curl | bash
  read -r ans < /dev/tty
  ans="${ans:-$def}"
  [[ "${ans,,}" == "y" ]]
}

show_menu() {
  local title="$1"; shift
  local options=("$@")
  local count=${#options[@]}
  section "$title"
  echo ""
  for ((i=1; i<=count; i++)); do
    echo -e "     ${CYAN}${BOLD}${i}.${RESET} ${WHITE}${options[$((i-1))]}${RESET}"
  done
  echo ""
  echo -ne "   ${BOLD}${WHITE}Choice [1-${count}]${RESET} ${CYAN}${ARROW}${RESET} "
  # Read from /dev/tty to support curl | bash
  read -r choice < /dev/tty
  _MENU_CHOICE="${choice:-1}"
  return 0
}

# ─────────────────────────────────────────────────────────────
#   Execution Spinner
# ─────────────────────────────────────────────────────────────

spin_pid=""
spinner_start() {
  local label="$1"
  local frames=('⠋' '⠙' '⠹' '⠸' '⠼' '⠴' '⠦' '⠧' '⠇' '⠏')
  (
    while true; do
      for f in "${frames[@]}"; do
        echo -ne "\r   ${CYAN}${BOLD}${f}${RESET}  ${DIM}${label}...${RESET}"
        sleep 0.08
      done
    done
  ) &
  spin_pid=$!
}

spinner_stop() {
  if [[ -n "$spin_pid" ]]; then
    kill "$spin_pid" 2>/dev/null || true
    spin_pid=""
  fi
  echo -ne "\r\033[2K"
}

run_step() {
  local label="$1"; shift
  spinner_start "$label"
  local output exit_code
  output=$("$@" 2>&1)
  exit_code=$?
  spinner_stop
  if [[ $exit_code -eq 0 ]]; then
    msg_ok "$label"
  else
    msg_fail "$label"
    echo -e "   ${DIM}Error details:${RESET}"
    echo "$output" | head -10 | sed 's/^/      │ /'
    exit 1
  fi
}

show_success() {
  echo ""
  draw_line "━" "$GREEN"
  center_text "${GREEN}${BOLD}🎉 ${1}${RESET}"
  center_text "${DIM}${2}${RESET}"
  draw_line "━" "$GREEN"
  echo ""
}

