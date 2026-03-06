#!/bin/bash
# ============================================================
#   lib/ui.sh — Terminal UI helpers
#   Colors · Banner · Boxes · Spinner · Prompts · Menus
# ============================================================

# ── Colors ───────────────────────────────────────────────────
RESET="\033[0m";  BOLD="\033[1m";  DIM="\033[2m"
BRIGHT_RED="\033[91m";    BRIGHT_GREEN="\033[92m"
BRIGHT_YELLOW="\033[93m"; BRIGHT_BLUE="\033[94m"
BRIGHT_MAGENTA="\033[95m"; BRIGHT_CYAN="\033[96m"
BRIGHT_WHITE="\033[97m";  WHITE="\033[37m"
BG_CYAN="\033[46m";       BLACK="\033[30m"

# ── Symbols ──────────────────────────────────────────────────
OK="${BRIGHT_GREEN}✔${RESET}";    FAIL="${BRIGHT_RED}✘${RESET}"
INFO="${BRIGHT_CYAN}●${RESET}";   WARN="${BRIGHT_YELLOW}▲${RESET}"
ARROW="${BRIGHT_BLUE}❯${RESET}";  GEAR="${BRIGHT_MAGENTA}⚙${RESET}"
BOX_H="─"; BOX_V="│"
BOX_TL="╭"; BOX_TR="╮"
BOX_BL="╰"; BOX_BR="╯"

# ── Terminal width ────────────────────────────────────────────
COLS=$(tput cols 2>/dev/null || echo 72)
[[ $COLS -gt 80 ]] && COLS=80

# ─────────────────────────────────────────────────────────────
#   Layout
# ─────────────────────────────────────────────────────────────

repeat_char() { printf "%${2}s" | tr ' ' "${1}"; }

center_text() {
  local text="$1"
  local clean; clean=$(echo -e "$text" | sed 's/\x1b\[[0-9;]*m//g')
  local pad=$(( (COLS - ${#clean}) / 2 ))
  [[ $pad -lt 0 ]] && pad=0
  printf "%${pad}s%b\n" "" "$text"
}

draw_line() {
  local char="${1:-─}" color="${2:-$DIM}"
  echo -e "${color}$(repeat_char "$char" "$COLS")${RESET}"
}

draw_box_top()    { echo -e "${DIM}${BOX_TL}$(repeat_char "$BOX_H" $((COLS-2)))${BOX_TR}${RESET}"; }
draw_box_bottom() { echo -e "${DIM}${BOX_BL}$(repeat_char "$BOX_H" $((COLS-2)))${BOX_BR}${RESET}"; }

draw_box_line() {
  local text="$1"
  local clean; clean=$(echo -e "$text" | sed 's/\x1b\[[0-9;]*m//g')
  local rpad=$(( COLS - 4 - ${#clean} ))
  [[ $rpad -lt 0 ]] && rpad=0
  echo -e "${DIM}${BOX_V}${RESET} ${text}$(printf "%${rpad}s") ${DIM}${BOX_V}${RESET}"
}

# ─────────────────────────────────────────────────────────────
#   Banner
# ─────────────────────────────────────────────────────────────

show_banner() {
  clear
  echo ""
  center_text "${BRIGHT_CYAN}${BOLD}██████╗ ██╗  ██╗██████╗ ${RESET}"
  center_text "${BRIGHT_CYAN}${BOLD}██╔══██╗██║  ██║██╔══██╗${RESET}"
  center_text "${BRIGHT_CYAN}${BOLD}██████╔╝███████║██████╔╝${RESET}"
  center_text "${BRIGHT_CYAN}${BOLD}██╔═══╝ ██╔══██║██╔═══╝ ${RESET}"
  center_text "${BRIGHT_CYAN}${BOLD}██║     ██║  ██║██║     ${RESET}"
  center_text "${BRIGHT_CYAN}${BOLD}╚═╝     ╚═╝  ╚═╝╚═╝     ${RESET}"
  echo ""
  center_text "${DIM}${WHITE}Installer for Linux — v1.2.0${RESET}"
  echo ""
  draw_line "─" "$DIM"
  echo ""
}

# ─────────────────────────────────────────────────────────────
#   Section & Messages
# ─────────────────────────────────────────────────────────────

section() {
  echo ""
  echo -e " ${BRIGHT_MAGENTA}${BOLD}▌${RESET} ${BOLD}${BRIGHT_WHITE}${1}${RESET}"
  echo -e " ${DIM}$(repeat_char "─" $((COLS-3)))${RESET}"
}

msg_ok()   { echo -e "   ${OK}  ${WHITE}${1}${RESET}"; }
msg_fail() { echo -e "   ${FAIL}  ${BRIGHT_RED}${1}${RESET}"; }
msg_info() { echo -e "   ${INFO}  ${BRIGHT_CYAN}${1}${RESET}"; }
msg_warn() { echo -e "   ${WARN}  ${BRIGHT_YELLOW}${1}${RESET}"; }

# ─────────────────────────────────────────────────────────────
#   Spinner
# ─────────────────────────────────────────────────────────────

spin_pid=""

spinner_start() {
  local label="$1"
  local frames=('⠋' '⠙' '⠹' '⠸' '⠼' '⠴' '⠦' '⠧' '⠇' '⠏')
  (
    while true; do
      for f in "${frames[@]}"; do
        echo -ne "\r   ${BRIGHT_CYAN}${f}${RESET}  ${WHITE}${label}...${RESET}   "
        sleep 0.08
      done
    done
  ) &
  spin_pid=$!
  disown "$spin_pid" 2>/dev/null || true
}

spinner_stop() {
  if [[ -n "$spin_pid" ]]; then
    kill "$spin_pid" 2>/dev/null || true
    spin_pid=""
  fi
  echo -ne "\r\033[2K"
}

# Run a real command behind a spinner; exit on failure
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
    echo ""
    echo -e "   ${DIM}Error output:${RESET}"
    echo "$output" | head -20 | sed 's/^/     /'
    show_error "Step failed: $label"
    exit 1
  fi
}

# ─────────────────────────────────────────────────────────────
#   Prompts
# ─────────────────────────────────────────────────────────────

prompt_input() {
  local question="$1" default="$2" var_name="$3" result
  if [[ -n "$default" ]]; then
    echo -ne "   ${ARROW}  ${WHITE}${question} ${DIM}[${default}]${RESET}: "
  else
    echo -ne "   ${ARROW}  ${WHITE}${question}${RESET}: "
  fi
  read -r result
  result="${result:-$default}"
  eval "$var_name=\"\$result\""
}

prompt_confirm() {
  local question="$1" default="${2:-y}" answer
  if [[ "$default" == "y" ]]; then
    echo -ne "   ${ARROW}  ${WHITE}${question} ${DIM}[${BRIGHT_GREEN}Y${DIM}/n]${RESET}: "
  else
    echo -ne "   ${ARROW}  ${WHITE}${question} ${DIM}[y/${BRIGHT_RED}N${DIM}]${RESET}: "
  fi
  read -r answer
  answer="${answer:-$default}"
  [[ "${answer,,}" == "y" ]]
}

show_menu() {
  local title="$1"; shift
  local options=("$@")
  local count=${#options[@]}
  section "$title"
  echo ""
  for ((i=1; i<=count; i++)); do
    echo -e "   ${DIM}  ${i}. ${RESET}${WHITE}${options[$((i-1))]}${RESET}"
  done
  echo ""
  echo -ne "   ${ARROW}  ${WHITE}Your choice${RESET} ${DIM}[1-${count}]${RESET}: "
  read -r choice
  if [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= count )); then
    return "$choice"
  fi
  return 1
}

# ─────────────────────────────────────────────────────────────
#   Summary / Done / Error screens
# ─────────────────────────────────────────────────────────────

show_summary() {
  local php_version="$1" os_info="$2" arch="$3" web_server="$4"
  shift 4
  local packages=("$@")

  section "Installation Summary"
  echo ""
  draw_box_top
  draw_box_line "${BOLD}${BRIGHT_WHITE}  Configuration${RESET}"
  draw_box_line ""
  draw_box_line "  ${DIM}PHP Version   :${RESET}  ${BRIGHT_CYAN}${BOLD}${php_version}${RESET}"
  draw_box_line "  ${DIM}Repository    :${RESET}  ${WHITE}ondrej/php  (PPA / sury.org)${RESET}"
  draw_box_line "  ${DIM}Web Server    :${RESET}  ${BRIGHT_WHITE}${web_server}${RESET}"
  draw_box_line ""
  draw_box_line "  ${DIM}Packages      :${RESET}"
  # Print packages in rows of 3
  local row=()
  for pkg in "${packages[@]}"; do
    row+=("$pkg")
    if [[ ${#row[@]} -eq 3 ]]; then
      draw_box_line "    ${BRIGHT_YELLOW}${row[0]}${RESET}  ${BRIGHT_YELLOW}${row[1]}${RESET}  ${BRIGHT_YELLOW}${row[2]}${RESET}"
      row=()
    fi
  done
  [[ ${#row[@]} -gt 0 ]] && draw_box_line "    ${BRIGHT_YELLOW}${row[*]}${RESET}"
  draw_box_line ""
  draw_box_line "  ${DIM}OS Detected   :${RESET}  ${BRIGHT_WHITE}${os_info}${RESET}"
  draw_box_line "  ${DIM}Architecture  :${RESET}  ${BRIGHT_WHITE}${arch}${RESET}"
  draw_box_line ""
  draw_box_bottom
  echo ""
}

show_done() {
  local version="$1"
  echo ""
  draw_line "═" "$BRIGHT_GREEN"
  center_text ""
  center_text "${BRIGHT_GREEN}${BOLD}  Installation Complete!${RESET}"
  center_text "${DIM}PHP ${version} is ready to use${RESET}"
  center_text ""
  draw_line "═" "$BRIGHT_GREEN"
  echo ""
  center_text "${DIM}Run ${BRIGHT_CYAN}php --version${DIM} to verify${RESET}"
  echo ""
  if command -v "php${version}" &>/dev/null; then
    echo -e "   ${INFO}  $("php${version}" --version | head -1)"
    echo ""
  elif command -v php &>/dev/null; then
    echo -e "   ${INFO}  $(php --version | head -1)"
    echo ""
  fi
}

show_error() {
  spinner_stop
  echo ""
  draw_line "═" "$BRIGHT_RED"
  center_text "${BRIGHT_RED}${BOLD}  Installation Failed${RESET}"
  center_text "${DIM}${1}${RESET}"
  draw_line "═" "$BRIGHT_RED"
  echo ""
}