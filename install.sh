#!/bin/bash
# ============================================================
#   install.sh — Premium Interactive Wizard
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="${SCRIPT_DIR}/lib"
INSTALLERS_DIR="${SCRIPT_DIR}/installers"

# ── Load modules ─────────────────────────────────────────────
for lib in ui detect repo; do
  source "${LIB_DIR}/${lib}.sh"
done

for installer in shell php mariadb node composer valet; do
  source "${INSTALLERS_DIR}/${installer}.sh"
done

trap 'spinner_stop; echo ""; msg_warn "Installation cancelled."; exit 130' INT TERM

# ═══════════════════════════════════════════════════════════════
#   COMPONENTS PANEL
# ═══════════════════════════════════════════════════════════════

_draw_panel_line() {
  local state="$1" num="$2" label="$3" desc="$4"
  if [[ "$state" == "1" ]]; then
    echo -e "   ${GREEN}${BOLD}│ [✔] ${num}.${RESET} ${WHITE}${BOLD}${label}${RESET} ${DIM}— ${desc}${RESET}"
  else
    echo -e "   ${DIM}│ [ ] ${num}. ${label} — ${desc}${RESET}"
  fi
}

dashboard_selection() {
  local -n _st=$1
  while true; do
    show_banner
    section "DASHBOARD: COMPONENT SELECTION"
    echo -e "   ${DIM}Toggle items with numbers · Press ${GREEN}${BOLD}'I'${DIM} to Install · ${RED}${BOLD}'Q'${DIM} to Quit${RESET}"
    echo ""
    _draw_panel_line "${_st[shell]}"    "1" "Shell Environment" "Zsh + P10k + Modern CLI Tools"
    _draw_panel_line "${_st[php]}"      "2" "PHP Engine"        "Custom Versions & Extensions"
    _draw_panel_line "${_st[mariadb]}"  "3" "MariaDB Database"  "SQL Server + Security Wizard"
    _draw_panel_line "${_st[node]}"     "4" "Node.js (NVM)"     "Node LTS & Package Manager"
    _draw_panel_line "${_st[composer]}" "5" "PHP Composer"      "Global Dependency Management"
    _draw_panel_line "${_st[valet]}"    "6" "Laravel Valet"     "Elite Local Development Server"
    echo ""
    echo -ne "   ${BOLD}${WHITE}Choice${RESET} ${CYAN}${ARROW}${RESET} "
    read -r key < /dev/tty

    case "${key,,}" in
      1) [[ "${_st[shell]}"    == "1" ]] && _st[shell]="0"    || _st[shell]="1" ;;
      2) [[ "${_st[php]}"      == "1" ]] && _st[php]="0"      || _st[php]="1" ;;
      3) [[ "${_st[mariadb]}"  == "1" ]] && _st[mariadb]="0"  || _st[mariadb]="1" ;;
      4) [[ "${_st[node]}"     == "1" ]] && _st[node]="0"     || _st[node]="1" ;;
      5) [[ "${_st[composer]}" == "1" ]] && _st[composer]="0" || _st[composer]="1" ;;
      6) [[ "${_st[valet]}"    == "1" ]] && _st[valet]="0"    || _st[valet]="1" ;;
      i) break ;;
      q) exit 0 ;;
    esac
  done
}

# ═══════════════════════════════════════════════════════════════
#   MAIN FLOW
# ═══════════════════════════════════════════════════════════════

main() {
  detect_os
  detect_existing_php

  declare -A STATES=( [shell]="1" [php]="1" [mariadb]="1" [node]="1" [composer]="1" [valet]="1" )

  # 1. Selection
  dashboard_selection STATES

  # 2. PHP Version Choice (If selected)
  PHP_VERSION="8.4"
  SELECTED_PACKAGES=("${PHP_PACKAGES_DEFAULT[@]}")
  if [[ "${STATES[php]}" == "1" ]]; then
    show_banner
    show_menu "PHP: SELECT VERSION" "8.5 (Latest)" "8.4 (Recommended)" "8.3" "8.2" "8.1"
    case "$_MENU_CHOICE" in
      1) PHP_VERSION="8.5" ;; 2) PHP_VERSION="8.4" ;; 3) PHP_VERSION="8.3" ;;
      4) PHP_VERSION="8.2" ;; 5) PHP_VERSION="8.1" ;; *) PHP_VERSION="8.4" ;;
    esac
  fi

  # 3. Final Auth Step
  show_banner
  section "AUTHENTICATION REQUIRED"
  echo -e "   ${INFO}  This installer needs administrative privileges to modify your system."
  echo -e "   ${INFO}  Please enter your system password when prompted below."
  echo ""
  
  # Trigger sudo explicitly with a nice message
  if ! sudo -v; then
    msg_fail "Authentication failed. Exiting."
    exit 1
  fi
  
  # Keep sudo alive
  while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

  # 4. Final Review
  show_banner
  section "FINAL REVIEW: READY TO DEPLOY"
  echo ""
  [[ "${STATES[shell]}"    == "1" ]] && msg_ok "Shell: Zsh + P10k"
  [[ "${STATES[php]}"      == "1" ]] && msg_ok "PHP: version ${PHP_VERSION}"
  [[ "${STATES[mariadb]}"  == "1" ]] && msg_ok "MariaDB: Database Server"
  [[ "${STATES[node]}"     == "1" ]] && msg_ok "Node.js: via NVM"
  [[ "${STATES[composer]}" == "1" ]] && msg_ok "Composer: Global"
  [[ "${STATES[valet]}"    == "1" ]] && msg_ok "Valet: Laravel Dev Environment"
  echo ""
  
  if ! prompt_confirm "Begin installation?"; then
    exit 0
  fi

  # 5. EXECUTION
  check_privileges
  check_apt

  [[ "${STATES[shell]}"    == "1" ]] && install_shell
  if [[ "${STATES[php]}"   == "1" ]]; then
    setup_repo
    install_php "$PHP_VERSION" "${SELECTED_PACKAGES[@]}"
    set_default_php "$PHP_VERSION"
  fi
  [[ "${STATES[mariadb]}"  == "1" ]] && install_mariadb
  [[ "${STATES[node]}"     == "1" ]] && install_node
  [[ "${STATES[composer]}" == "1" ]] && install_composer
  [[ "${STATES[valet]}"    == "1" ]] && install_valet

  show_success "COMPLETED" "System is optimized and ready for Laravel development."
}

main "$@"
