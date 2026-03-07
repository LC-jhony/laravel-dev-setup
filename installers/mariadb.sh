#!/bin/bash
# ============================================================
#   installers/mariadb.sh — MariaDB installation (ULTRA ROBUST)
# ============================================================

install_mariadb() {
  section "Installing MariaDB"
  echo ""

  run_step "Installing mariadb-server & mariadb-client" \
    bash -c "DEBIAN_FRONTEND=noninteractive $SUDO apt-get install -y mariadb-server mariadb-client"

  # 1. Asegurar que no esté bloqueado (enmascarado)
  $SUDO systemctl unmask mariadb &>/dev/null || true
  $SUDO systemctl unmask mysql &>/dev/null || true

  # 2. Recargar configuración de servicios
  run_step "Reloading system daemon" \
    $SUDO systemctl daemon-reload

  # 3. Intentar arrancar con limpieza previa
  spinner_start "Starting mariadb service"
  
  # Detener cualquier rastro previo para evitar conflictos de socket
  $SUDO systemctl stop mariadb &>/dev/null || true
  
  if $SUDO systemctl start mariadb &>/dev/null; then
    spinner_stop
    msg_ok "Starting mariadb service"
  else
    # Si falla, intentar el comando tradicional de Debian
    if $SUDO service mariadb start &>/dev/null; then
      spinner_stop
      msg_ok "Starting mariadb service (via service manager)"
    else
      spinner_stop
      msg_fail "Starting mariadb service"
      echo -e "\n   ${RED}⚠ ERROR: MariaDB no pudo arrancar.${RESET}"
      echo -e "   ${DIM}Posibles causas: Puerto 3306 ocupado o falta de memoria.${RESET}"
      echo -e "   ${DIM}Revisa con: sudo journalctl -u mariadb -n 20${RESET}\n"
      exit 1
    fi
  fi

  run_step "Enabling mariadb service on boot" \
    $SUDO systemctl enable mariadb

  msg_ok "MariaDB installed and running"
  echo ""

  # ── Secure installation ──────────────────────────────────
  section "MariaDB Secure Installation"
  echo ""
  msg_info "This will run 'mariadb-secure-installation' interactively."
  echo ""

  if prompt_confirm "Run mariadb-secure-installation now?" "y"; then
    echo ""
    $SUDO mariadb-secure-installation
    echo ""
    msg_ok "MariaDB secure installation complete"
  else
    msg_warn "Skipped — run manually: sudo mariadb-secure-installation"
  fi
}
