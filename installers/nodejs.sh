#!/bin/bash
# ============================================================
#   lib/node.sh — NVM + Node.js installation
#
#   Installs NVM v0.40.4, then Node.js 24 via nvm
# ============================================================

NVM_VERSION="v0.40.4"
NODE_VERSION="24"
NVM_INSTALL_URL="https://raw.githubusercontent.com/nvm-sh/nvm/${NVM_VERSION}/install.sh"

install_node() {
  section "Installing NVM + Node.js ${NODE_VERSION}"
  echo ""

  # ── Install NVM ──────────────────────────────────────────
  msg_info "NVM ${NVM_VERSION} will be installed for the current user"
  echo ""

  # NVM installer requires curl or wget
  if ! command -v curl &>/dev/null; then
    run_step "Installing curl (required for NVM)" \
      $SUDO apt-get install -y curl
  fi

  run_step "Downloading & installing NVM ${NVM_VERSION}" \
    bash -c "curl -o- ${NVM_INSTALL_URL} | bash"

  # ── Load NVM in current shell ────────────────────────────
  export NVM_DIR="${HOME}/.nvm"

  if [[ -f "${NVM_DIR}/nvm.sh" ]]; then
    # shellcheck source=/dev/null
    . "${NVM_DIR}/nvm.sh"
    msg_ok "NVM loaded in current session"
  else
    msg_fail "NVM directory not found at ${NVM_DIR}"
    msg_warn "Try restarting your terminal and running: nvm install ${NODE_VERSION}"
    return 1
  fi

  # ── Install Node.js ──────────────────────────────────────
  run_step "Installing Node.js ${NODE_VERSION}" \
    bash -c ". \"${NVM_DIR}/nvm.sh\" && nvm install ${NODE_VERSION}"

  run_step "Setting Node.js ${NODE_VERSION} as default" \
    bash -c ". \"${NVM_DIR}/nvm.sh\" && nvm alias default ${NODE_VERSION}"

  echo ""
  msg_ok "Node.js $(. "${NVM_DIR}/nvm.sh" && node --version 2>/dev/null || echo '(restart shell to verify)') installed"
  msg_ok "NPM   $(. "${NVM_DIR}/nvm.sh" && npm --version 2>/dev/null || echo '(restart shell to verify)') installed"

  echo ""
  msg_info "NVM is loaded automatically on new shells via ~/.bashrc / ~/.zshrc"
  msg_warn "Run 'source ~/.bashrc' or restart your terminal to use 'node' and 'nvm'"
}