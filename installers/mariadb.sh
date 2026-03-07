#!/bin/bash
# ============================================================
#   installers/mariadb.sh — MariaDB installation (ROBUST)
# ============================================================

install_mariadb() {
  section "Installing MariaDB"
  echo ""

  run_step "Installing mariadb-server & mariadb-client" \
    bash -c "DEBIAN_FRONTEND=noninteractive $SUDO apt-get install -y mariadb-server mariadb-client"

  # Detectar si usamos systemd o init.d (WSL support)
  if pidof systemd &>/dev/null; then
    run_step "Enabling mariadb service on boot" \
      $SUDO systemctl enable mariadb
    
    # Intentar iniciar con systemctl, si falla usar service (más robusto en algunos entornos)
    spinner_start "Starting mariadb service"
    if $SUDO systemctl start mariadb &>/dev/null; then
      spinner_stop
      msg_ok "Starting mariadb service"
    else
      if $SUDO service mariadb start &>/dev/null; then
        spinner_stop
        msg_ok "Starting mariadb service (via service manager)"
      else
        spinner_stop
        msg_fail "Starting mariadb service"
        echo -e "   ${DIM}Tip: Try running 'sudo journalctl -xeu mariadb.service' to see errors.${RESET}"
        exit 1
      fi
    fi
  else
    # Fallback para sistemas sin systemd (como WSL tradicional)
    run_step "Starting mariadb service (SysV)" \
      $SUDO service mariadb start
  fi

  msg_ok "MariaDB installed and running"
  echo ""

  # ── Secure installation ──────────────────────────────────
  section "MariaDB Secure Installation"
  echo ""
  msg_info "This will run 'mariadb-secure-installation' interactively."
  msg_info "You will be asked to set a root password and harden the setup."
  echo ""

  if prompt_confirm "Run mariadb-secure-installation now?" "y"; then
    echo ""
    draw_line "─" "$DIM"
    echo ""
    # Forzar modo interactivo real
    $SUDO mariadb-secure-installation
    echo ""
    draw_line "─" "$DIM"
    echo ""
    msg_ok "MariaDB secure installation complete"
  else
    msg_warn "Skipped — run manually: sudo mariadb-secure-installation"
  fi
}
