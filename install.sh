#!/bin/bash
# ============================================================
#   install.sh — Optimized Interactive Wizard
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="${SCRIPT_DIR}/lib"
INSTALLERS_DIR="${SCRIPT_DIR}/installers"

# ── Load helpers ─────────────────────────────────────────────
for lib in ui detect repo; do
  source "${LIB_DIR}/${lib}.sh"
done

# ── Load installers ──────────────────────────────────────────
for installer in shell php mariadb node composer valet; do
  source "${INSTALLERS_DIR}/${installer}.sh"
done

trap 'spinner_stop; echo ""; msg_warn "Installation interrupted."; exit 130' INT TERM

# ═══════════════════════════════════════════════════════════════
#   PHASE 1: COMPONENT SELECTION
# ═══════════════════════════════════════════════════════════════

_draw_toggle() {
  local state="$1" num="$2" label="$3" desc="$4"
  if [[ "$state" == "1" ]]; then
    echo -e "   ${BRIGHT_GREEN}${BOLD}[✔]${RESET}  ${num}. ${BRIGHT_WHITE}${BOLD}${label}${RESET} ${DIM}— ${desc}${RESET}"
  else
    echo -e "   ${DIM}[ ]  ${num}. ${label} — ${desc}${RESET}"
  fi
}

select_components() {
  local -n _states=$1
  while true; do
    show_banner
    section "STEP 1: SELECT COMPONENTS"
    echo -e "   ${DIM}Type the number to toggle · Press ${BRIGHT_GREEN}'I'${DIM} to start installation · ${BRIGHT_RED}'Q'${DIM} to quit${RESET}"
    echo ""

    _draw_toggle "${_states[shell]}"    "1" "Shell Environment" "Zsh + Powerlevel10k + Tools"
    _draw_toggle "${_states[php]}"      "2" "PHP Engine"        "Customizable versions & extensions"
    _draw_toggle "${_states[mariadb]}"  "3" "MariaDB Database"  "SQL Server + Secure Setup"
    _draw_toggle "${_states[node]}"     "4" "Node.js (NVM)"     "Node.js LTS & Version Manager"
    _draw_toggle "${_states[composer]}" "5" "PHP Composer"      "Global dependency manager"
    _draw_toggle "${_states[valet]}"    "6" "Laravel Valet"     "Local development server"

    echo ""
    draw_line "─" "$DIM"
    echo -ne "   ${ARROW}  ${WHITE}Select option${RESET}: "
    read -r key

    case "${key,,}" in
      1) [[ "${_states[shell]}"    == "1" ]] && _states[shell]="0"    || _states[shell]="1" ;;
      2) [[ "${_states[php]}"      == "1" ]] && _states[php]="0"      || _states[php]="1" ;;
      3) [[ "${_states[mariadb]}"  == "1" ]] && _states[mariadb]="0"  || _states[mariadb]="1" ;;
      4) [[ "${_states[node]}"     == "1" ]] && _states[node]="0"     || _states[node]="1" ;;
      5) [[ "${_states[composer]}" == "1" ]] && _states[composer]="0" || _states[composer]="1" ;;
      6) [[ "${_states[valet]}"    == "1" ]] && _states[valet]="0"    || _states[valet]="1" ;;
      i) break ;;
      q) exit 0 ;;
    esac
  done
}

# ═══════════════════════════════════════════════════════════════
#   PHASE 2: CONFIGURATION (PHP VERSION SELECTION)
# ═══════════════════════════════════════════════════════════════

configure_php() {
  show_banner
  section "STEP 2: PHP CONFIGURATION"
  echo -e "   ${INFO}  You can now choose exactly which PHP version you want."
  echo ""

  show_menu "Select your PHP Version" \
    "PHP 8.5 (Latest)" \
    "PHP 8.4 (Recommended)" \
    "PHP 8.3 (Stable)" \
    "PHP 8.2 (Security fixes)" \
    "PHP 8.1 (Legacy)"

  case "$_MENU_CHOICE" in
    1) PHP_VERSION="8.5" ;;
    2) PHP_VERSION="8.4" ;;
    3) PHP_VERSION="8.3" ;;
    4) PHP_VERSION="8.2" ;;
    5) PHP_VERSION="8.1" ;;
    *) PHP_VERSION="8.4" ;;
  esac

  show_menu "Select Package Profile" \
    "Standard (Full Laravel Extensions)" \
    "Minimal (CLI only)"
  case "$_MENU_CHOICE" in
    1) SELECTED_PACKAGES=("${PHP_PACKAGES_DEFAULT[@]}") ;;
    *) SELECTED_PACKAGES=(base cli common) ;;
  esac
}

# ═══════════════════════════════════════════════════════════════
#   PHASE 3: SUMMARY & INSTALL
# ═══════════════════════════════════════════════════════════════

main() {
  detect_os
  detect_existing_php

  declare -A STATES=(
    [shell]="1" [php]="1" [mariadb]="1"
    [node]="1"  [composer]="1" [valet]="1"
  )

  # Step 1: Selection
  select_components STATES

  # Step 2: Configuration (Only if PHP is selected)
  PHP_VERSION="8.4"
  SELECTED_PACKAGES=("${PHP_PACKAGES_DEFAULT[@]}")
  if [[ "${STATES[php]}" == "1" ]]; then
    configure_php
  fi

  # Step 3: Final Confirmation
  show_banner
  section "STEP 3: FINAL REVIEW"
  echo ""
  draw_box_top
  [[ "${STATES[shell]}"    == "1" ]] && draw_box_line "  ${OK} Shell Setup (Zsh + P10k)"
  [[ "${STATES[php]}"      == "1" ]] && draw_box_line "  ${OK} PHP ${PHP_VERSION} (with Extensions)"
  [[ "${STATES[mariadb]}"  == "1" ]] && draw_box_line "  ${OK} MariaDB Database"
  [[ "${STATES[node]}"     == "1" ]] && draw_box_line "  ${OK} Node.js (via NVM)"
  [[ "${STATES[composer]}" == "1" ]] && draw_box_line "  ${OK} Composer Global"
  [[ "${STATES[valet]}"    == "1" ]] && draw_box_line "  ${OK} Laravel Valet"
  draw_box_bottom
  echo ""

  if ! prompt_confirm "Does everything look correct? Proceed with install?"; then
    msg_warn "Installation cancelled by user."
    exit 0
  fi

  # ── EXECUTION ───────────────────────────────────────────
  check_privileges
  # Keep-alive sudo: updates the timestamp every 60 seconds
  while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &
  
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

  show_success "COMPLETED" "Your Laravel environment is ready!"
}

main "$@"
