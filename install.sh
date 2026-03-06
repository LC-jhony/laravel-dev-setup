#!/bin/bash
# ============================================================
#   install.sh — Linux Dev Environment Installer
#
#   Usage:
#     bash install.sh
#     sudo bash install.sh
#
#   Structure:
#     install.sh              ← entry point (you are here)
#     lib/
#       ui.sh                 ← colors, banner, spinner, menus
#       detect.sh             ← OS & PHP detection
#       repo.sh               ← ondrej/php PPA & sury.org
#     installers/
#       shell.sh              ← git · unzip · zsh · zinit · p10k
#       php.sh                ← PHP via ondrej/php
#       mariadb.sh            ← MariaDB server + client
#       node.sh               ← NVM + Node.js 24
#       composer.sh           ← Composer
#       valet.sh              ← Laravel Valet + laravel/installer
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="${SCRIPT_DIR}/lib"
INSTALLERS_DIR="${SCRIPT_DIR}/installers"

# ── Load helpers ─────────────────────────────────────────────
for lib in ui detect repo; do
  file="${LIB_DIR}/${lib}.sh"
  [[ ! -f "$file" ]] && { echo "ERROR: Missing lib/${lib}.sh" >&2; exit 1; }
  # shellcheck source=/dev/null
  source "$file"
done

# ── Load installers ──────────────────────────────────────────
for installer in shell php mariadb node composer valet; do
  file="${INSTALLERS_DIR}/${installer}.sh"
  [[ ! -f "$file" ]] && { echo "ERROR: Missing installers/${installer}.sh" >&2; exit 1; }
  # shellcheck source=/dev/null
  source "$file"
done

trap 'spinner_stop; echo ""; msg_warn "Interrupted."; echo ""; exit 130' INT TERM

# ═══════════════════════════════════════════════════════════════
#   TOGGLE MENU
# ═══════════════════════════════════════════════════════════════

_toggle_line() {
  local state="$1" num="$2" label="$3" note="$4"
  if [[ "$state" == "1" ]]; then
    echo -e "   ${BRIGHT_GREEN}${BOLD}[✔]${RESET}  ${DIM}${num}.${RESET}  ${BRIGHT_WHITE}${BOLD}${label}${RESET}  ${DIM}${note}${RESET}"
  else
    echo -e "   ${DIM}[ ]  ${num}.  ${WHITE}${label}${RESET}  ${DIM}${note}${RESET}"
  fi
}

show_component_menu() {
  local -n _states=$1
  while true; do
    clear
    show_banner
    section "Select Components to Install"
    echo ""
    echo -e "   ${DIM}Toggle on/off with numbers · ${BRIGHT_GREEN}I${DIM} install · ${BRIGHT_RED}Q${DIM} quit${RESET}"
    echo ""

    _toggle_line "${_states[shell]}"    "1" "Shell Setup"    "git · unzip · zsh · zinit · powerlevel10k"
    _toggle_line "${_states[php]}"      "2" "PHP"            "8.5 / 8.4 / 8.3 … via ondrej/php"
    _toggle_line "${_states[mariadb]}"  "3" "MariaDB"        "server + client + secure-install"
    _toggle_line "${_states[node]}"     "4" "Node.js"        "NVM ${NVM_VERSION} + Node.js ${NODE_VERSION}"
    _toggle_line "${_states[composer]}" "5" "Composer"       "latest via getcomposer.org"
    _toggle_line "${_states[valet]}"    "6" "Laravel Valet"  "valet-linux + laravel/installer"

    echo ""
    draw_line "─" "$DIM"
    echo ""
    echo -ne "   ${ARROW}  ${WHITE}Choice${RESET}: "
    read -r key

    case "${key,,}" in
      1) [[ "${_states[shell]}"    == "1" ]] && _states[shell]="0"    || _states[shell]="1" ;;
      2) [[ "${_states[php]}"      == "1" ]] && _states[php]="0"      || _states[php]="1" ;;
      3) [[ "${_states[mariadb]}"  == "1" ]] && _states[mariadb]="0"  || _states[mariadb]="1" ;;
      4) [[ "${_states[node]}"     == "1" ]] && _states[node]="0"     || _states[node]="1" ;;
      5) [[ "${_states[composer]}" == "1" ]] && _states[composer]="0" || _states[composer]="1" ;;
      6) [[ "${_states[valet]}"    == "1" ]] && _states[valet]="0"    || _states[valet]="1" ;;
      i) break ;;
      q) echo ""; msg_warn "Exiting installer."; echo ""; exit 0 ;;
    esac
  done
}

# ═══════════════════════════════════════════════════════════════
#   PHP SUB-WIZARD
# ═══════════════════════════════════════════════════════════════

run_php_wizard() {
  show_menu "Select PHP Version" \
    "PHP 8.5  — Latest Stable (Nov 2025)" \
    "PHP 8.4  — LTS  ★ Recommended" \
    "PHP 8.3  — Active support" \
    "PHP 8.2  — Security fixes only" \
    "PHP 8.1  — Legacy"
  case $? in
    1) PHP_VERSION="8.5" ;; 2) PHP_VERSION="8.4" ;;
    3) PHP_VERSION="8.3" ;; 4) PHP_VERSION="8.2" ;;
    5) PHP_VERSION="8.1" ;; *) PHP_VERSION="8.4" ;;
  esac

  show_menu "Select Package Profile" \
    "Default  — Standard web stack (recommended)" \
    "Minimal  — cli + common only" \
    "Custom   — Enter package names manually"
  case $? in
    1) SELECTED_PACKAGES=("${PHP_PACKAGES_DEFAULT[@]}") ;;
    2) SELECTED_PACKAGES=(base cli common) ;;
    3)
      echo ""
      msg_info "Available: curl pgsql fpm gd imap intl mbstring mysql opcache soap xml zip"
      echo ""
      prompt_input "Packages (space-separated, no php8.x- prefix)" "cli common curl xml zip" PKG_RAW
      read -ra SELECTED_PACKAGES <<< "base $PKG_RAW"
      ;;
    *) SELECTED_PACKAGES=("${PHP_PACKAGES_DEFAULT[@]}") ;;
  esac

  show_menu "Web Server Integration" \
    "None      — CLI only" \
    "Apache    — FPM + a2enconf" \
    "Nginx     — FPM + config snippet" \
    "FPM only  — service only"
  case $? in
    1) WEB_SERVER="None" ;;    2) WEB_SERVER="Apache" ;;
    3) WEB_SERVER="Nginx" ;;   4) WEB_SERVER="FPM only" ;;
    *) WEB_SERVER="None" ;;
  esac
}

# ═══════════════════════════════════════════════════════════════
#   SUMMARY
# ═══════════════════════════════════════════════════════════════

show_global_summary() {
  local -n _st=$1
  section "Installation Plan"
  echo ""
  draw_box_top
  draw_box_line "${BOLD}${BRIGHT_WHITE}  Selected Components${RESET}"
  draw_box_line ""
  [[ "${_st[shell]}"    == "1" ]] && draw_box_line "  ${OK}  ${BRIGHT_CYAN}Shell Setup${RESET}      ${DIM}zsh · zinit · powerlevel10k · fzf · zoxide${RESET}"
  [[ "${_st[php]}"      == "1" ]] && draw_box_line "  ${OK}  ${BRIGHT_CYAN}PHP ${PHP_VERSION}${RESET}          ${DIM}web: ${WEB_SERVER}${RESET}"
  [[ "${_st[mariadb]}"  == "1" ]] && draw_box_line "  ${OK}  ${BRIGHT_CYAN}MariaDB${RESET}          ${DIM}server + client + secure-install${RESET}"
  [[ "${_st[node]}"     == "1" ]] && draw_box_line "  ${OK}  ${BRIGHT_CYAN}Node.js ${NODE_VERSION}${RESET}       ${DIM}via NVM ${NVM_VERSION}${RESET}"
  [[ "${_st[composer]}" == "1" ]] && draw_box_line "  ${OK}  ${BRIGHT_CYAN}Composer${RESET}         ${DIM}→ /usr/local/bin/composer${RESET}"
  [[ "${_st[valet]}"    == "1" ]] && draw_box_line "  ${OK}  ${BRIGHT_CYAN}Laravel Valet${RESET}    ${DIM}cpriego/valet-linux + laravel/installer${RESET}"
  draw_box_line ""
  draw_box_line "  ${DIM}OS   :${RESET}  ${BRIGHT_WHITE}${OS_PRETTY} [${OS_CODENAME}]${RESET}"
  draw_box_line "  ${DIM}Arch :${RESET}  ${BRIGHT_WHITE}$(uname -m)${RESET}"
  draw_box_line ""
  draw_box_bottom
  echo ""
}

# ═══════════════════════════════════════════════════════════════
#   MAIN
# ═══════════════════════════════════════════════════════════════

main() {
  show_banner
  detect_os
  detect_existing_php

  declare -A STATES=(
    [shell]="1" [php]="1" [mariadb]="1"
    [node]="1"  [composer]="1" [valet]="1"
  )

  show_component_menu STATES

  PHP_VERSION="8.4"
  SELECTED_PACKAGES=("${PHP_PACKAGES_DEFAULT[@]}")
  WEB_SERVER="None"
  [[ "${STATES[php]}" == "1" ]] && run_php_wizard

  clear
  show_banner
  show_global_summary STATES

  if ! prompt_confirm "Proceed with installation?"; then
    echo ""; msg_warn "Cancelled."; echo ""; exit 0
  fi

  # Pre-flight
  section "Pre-flight Checks"
  echo ""
  check_privileges
  check_apt
  msg_ok "OS: ${OS_PRETTY} (${DISTRO_TYPE}) [${OS_CODENAME}]"
  msg_ok "Architecture: $(uname -m)"
  [[ -n "$EXISTING_PHP" ]] && msg_warn "PHP ${EXISTING_PHP} already detected"
  msg_ok "Pre-flight checks passed"

  # ── Install in dependency order ───────────────────────────
  [[ "${STATES[shell]}"    == "1" ]] && install_shell

  if [[ "${STATES[php]}" == "1" ]]; then
    setup_repo
    install_php "$PHP_VERSION" "${SELECTED_PACKAGES[@]}"
    case "$WEB_SERVER" in
      Apache)     install_fpm "$PHP_VERSION"; integrate_apache "$PHP_VERSION" ;;
      Nginx)      install_fpm "$PHP_VERSION"; integrate_nginx  "$PHP_VERSION" ;;
      "FPM only") install_fpm "$PHP_VERSION" ;;
      None) printf '%s\n' "${SELECTED_PACKAGES[@]}" | grep -q "^fpm$" \
              && install_fpm "$PHP_VERSION" || true ;;
    esac
    set_default_php "$PHP_VERSION"
    [[ -n "$EXISTING_PHP" && "$EXISTING_PHP" != "$PHP_VERSION" ]] \
      && remove_old_php "$EXISTING_PHP"
  fi

  [[ "${STATES[mariadb]}"  == "1" ]] && install_mariadb
  [[ "${STATES[node]}"     == "1" ]] && install_node
  [[ "${STATES[composer]}" == "1" ]] && install_composer
  [[ "${STATES[valet]}"    == "1" ]] && install_valet

  # ── Done ─────────────────────────────────────────────────
  echo ""
  draw_line "═" "$BRIGHT_GREEN"
  center_text ""
  center_text "${BRIGHT_GREEN}${BOLD}  All components installed successfully!${RESET}"
  center_text ""
  draw_line "═" "$BRIGHT_GREEN"
  echo ""
  section "Quick Reference"
  echo ""
  [[ "${STATES[shell]}"    == "1" ]] && msg_info "Shell    →  restart terminal  ·  p10k configure"
  [[ "${STATES[php]}"      == "1" ]] && msg_info "PHP      →  php --version"
  [[ "${STATES[mariadb]}"  == "1" ]] && msg_info "MariaDB  →  sudo mariadb -u root -p"
  [[ "${STATES[node]}"     == "1" ]] && msg_info "Node.js  →  node --version  (restart shell first)"
  [[ "${STATES[composer]}" == "1" ]] && msg_info "Composer →  composer --version"
  [[ "${STATES[valet]}"    == "1" ]] && msg_info "Valet    →  valet --version  ·  ~/Sites/<name>.test"
  [[ "${STATES[valet]}"    == "1" ]] && msg_info "Laravel  →  laravel new myapp"
  echo ""
  [[ "${STATES[shell]}" == "1" ]] && {
    draw_line "─" "$DIM"
    center_text "${BRIGHT_YELLOW}${BOLD}  Restart your terminal to activate Zsh + Powerlevel10k${RESET}"
    draw_line "─" "$DIM"
    echo ""
  }
}

main "$@"