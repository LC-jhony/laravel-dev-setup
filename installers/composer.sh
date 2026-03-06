#!/bin/bash
# ============================================================
#   lib/composer.sh — Composer installation
#
#   Downloads composer-setup.php, verifies SHA-384,
#   installs composer.phar and moves it to /usr/local/bin/composer
# ============================================================

COMPOSER_INSTALLER_URL="https://getcomposer.org/installer"
COMPOSER_INSTALLER_FILE="/tmp/composer-setup.php"
COMPOSER_BIN="/usr/local/bin/composer"

# SHA-384 hash from getcomposer.org/download
# Check latest at: https://composer.github.io/installer.sig
COMPOSER_EXPECTED_HASH="dac665fdc30fdd8ec78b38b9800061b4150413ff2e3b6f88543c636f7cd84f6db9189d43a81e5503cda447da73c7e5b6"

install_composer() {
  section "Installing Composer"
  echo ""

  # ── Check PHP is available ───────────────────────────────
  if ! command -v php &>/dev/null; then
    msg_fail "PHP is not available in PATH — install PHP first"
    exit 1
  fi
  msg_ok "PHP found: $(php --version | head -1)"
  echo ""

  # ── Download installer ───────────────────────────────────
  run_step "Downloading Composer installer" \
    bash -c "curl -sSL '${COMPOSER_INSTALLER_URL}' -o '${COMPOSER_INSTALLER_FILE}'"

  # ── Verify SHA-384 hash ──────────────────────────────────
  spinner_start "Verifying installer SHA-384 hash"
  local actual_hash
  actual_hash=$(php -r "echo hash_file('sha384', '${COMPOSER_INSTALLER_FILE}');")
  spinner_stop

  # Fetch latest hash dynamically as fallback
  local latest_hash
  latest_hash=$(curl -sSL https://composer.github.io/installer.sig 2>/dev/null || echo "")

  if [[ "$actual_hash" == "$COMPOSER_EXPECTED_HASH" ]] || \
     [[ -n "$latest_hash" && "$actual_hash" == "$latest_hash" ]]; then
    msg_ok "Installer hash verified"
  else
    msg_fail "Hash mismatch — installer may be corrupted or outdated"
    echo ""
    echo -e "   ${DIM}Expected : ${COMPOSER_EXPECTED_HASH}${RESET}"
    echo -e "   ${DIM}Got      : ${actual_hash}${RESET}"
    echo -e "   ${DIM}Latest   : ${latest_hash}${RESET}"
    rm -f "${COMPOSER_INSTALLER_FILE}"
    # Non-fatal: let user decide
    if ! prompt_confirm "Continue installation anyway?" "n"; then
      show_error "Composer installation aborted — hash mismatch"
      exit 1
    fi
    msg_warn "Continuing despite hash mismatch — proceed with caution"
  fi

  # ── Run installer ────────────────────────────────────────
  run_step "Running Composer installer" \
    bash -c "php '${COMPOSER_INSTALLER_FILE}' --install-dir=/tmp --filename=composer.phar"

  # ── Move to global PATH ──────────────────────────────────
  run_step "Installing Composer to ${COMPOSER_BIN}" \
    $SUDO mv /tmp/composer.phar "${COMPOSER_BIN}"

  run_step "Setting executable permissions" \
    $SUDO chmod +x "${COMPOSER_BIN}"

  # ── Cleanup ──────────────────────────────────────────────
  rm -f "${COMPOSER_INSTALLER_FILE}"

  echo ""
  msg_ok "Composer $(composer --version 2>/dev/null | awk '{print $3}') installed at ${COMPOSER_BIN}"
}