#!/bin/bash
# ============================================================
#   lib/mariadb.sh — MariaDB installation
#
#   Installs: mariadb-server mariadb-client
#   Runs:     mariadb-secure-installation (interactive)
# ============================================================

install_mariadb() {
  section "Installing MariaDB"
  echo ""

  run_step "Installing mariadb-server & mariadb-client" \
    bash -c "DEBIAN_FRONTEND=noninteractive $SUDO apt-get install -y mariadb-server mariadb-client"

  run_step "Enabling mariadb service on boot" \
    $SUDO systemctl enable mariadb

  run_step "Starting mariadb service" \
    $SUDO systemctl start mariadb

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
    $SUDO mariadb-secure-installation
    echo ""
    draw_line "─" "$DIM"
    echo ""
    msg_ok "MariaDB secure installation complete"
  else
    msg_warn "Skipped — run manually: sudo mariadb-secure-installation"
  fi
}