#!/bin/bash
# ============================================================
#   lib/valet.sh — Laravel Valet Linux installation
#
#   Requires: composer (lib/composer.sh)
#
#   Steps:
#     1. Install system dependencies
#     2. composer global require cpriego/valet-linux
#     3. valet install
#     4. mkdir ~/Sites && cd ~/Sites && valet park
#     5. composer global require laravel/installer
# ============================================================

VALET_SITES_DIR="${HOME}/Sites"

# System packages required by Valet Linux
VALET_DEPS=(
  network-manager
  libnss3-tools
  jq
  xsel
)

install_valet() {
  section "Installing Laravel Valet Linux"
  echo ""

  # ── Check composer ───────────────────────────────────────
  if ! command -v composer &>/dev/null; then
    msg_fail "Composer not found — install Composer first (it's a prerequisite)"
    exit 1
  fi
  msg_ok "Composer found: $(composer --version 2>/dev/null | awk '{print $1,$2,$3}')"
  echo ""

  # ── System dependencies ──────────────────────────────────
  section "Installing Valet System Dependencies"
  echo ""
  msg_info "Packages: ${VALET_DEPS[*]}"
  echo ""

  run_step "Installing system dependencies" \
    bash -c "DEBIAN_FRONTEND=noninteractive $SUDO apt-get install -y ${VALET_DEPS[*]}"

  # ── Add Composer global bin to PATH if not already there ─
  _ensure_composer_bin_in_path

  # ── Install valet-linux via Composer ─────────────────────
  section "Installing cpriego/valet-linux"
  echo ""

  run_step "composer global require cpriego/valet-linux" \
    bash -c "composer global require cpriego/valet-linux 2>&1"

  # ── Run valet install ────────────────────────────────────
  section "Running valet install"
  echo ""
  msg_info "This configures Nginx, PHP-FPM, and dnsmasq for Valet"
  echo ""

  run_step "valet install" \
    bash -c "valet install 2>&1"

  msg_ok "Valet installed and running"

  # ── Create Sites directory and park ──────────────────────
  section "Setting Up Sites Directory"
  echo ""

  if [[ ! -d "$VALET_SITES_DIR" ]]; then
    run_step "Creating ${VALET_SITES_DIR}" \
      mkdir -p "${VALET_SITES_DIR}"
    msg_ok "Directory created: ${VALET_SITES_DIR}"
  else
    msg_info "Directory already exists: ${VALET_SITES_DIR}"
  fi

  run_step "Running 'valet park' in ${VALET_SITES_DIR}" \
    bash -c "cd '${VALET_SITES_DIR}' && valet park 2>&1"

  msg_ok "Valet is now watching: ${VALET_SITES_DIR}"
  echo ""
  msg_info "Sites placed in ~/Sites will be accessible as <folder>.test"

  # ── Install Laravel installer ────────────────────────────
  section "Installing Laravel Installer"
  echo ""

  run_step "composer global require laravel/installer" \
    bash -c "composer global require laravel/installer 2>&1"

  echo ""
  msg_ok "Laravel installer ready"
  msg_info "Create a new app: laravel new myapp"
  msg_info "Or place it in ~/Sites and access it at myapp.test"
}

# ─────────────────────────────────────────────────────────────
#   Ensure ~/.config/composer/vendor/bin is in PATH
# ─────────────────────────────────────────────────────────────
_ensure_composer_bin_in_path() {
  local composer_bin
  composer_bin="$(composer config --global home 2>/dev/null)/vendor/bin"

  if [[ ":$PATH:" != *":${composer_bin}:"* ]]; then
    export PATH="${composer_bin}:${PATH}"
    msg_info "Added ${composer_bin} to PATH for this session"

    # Persist in shell rc files
    for rc in "${HOME}/.bashrc" "${HOME}/.zshrc" "${HOME}/.profile"; do
      if [[ -f "$rc" ]] && ! grep -q "composer/vendor/bin" "$rc" 2>/dev/null; then
        echo "" >> "$rc"
        echo "# Composer global binaries" >> "$rc"
        echo "export PATH=\"\${HOME}/.config/composer/vendor/bin:\${PATH}\"" >> "$rc"
        msg_ok "Added Composer bin to ${rc}"
      fi
    done
  else
    msg_ok "Composer global bin already in PATH"
  fi
}