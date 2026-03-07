#!/bin/bash
# ============================================================
#   installers/php.sh — PHP installation via ondrej/php
# ============================================================

PHP_PACKAGES_DEFAULT=(
  cli common curl xml zip gd mbstring intl
  opcache readline bcmath soap igbinary msgpack
  redis sqlite3 mysql pgsql
)

# ─────────────────────────────────────────────────────────────
#   Main entry point for PHP installation
# ─────────────────────────────────────────────────────────────
install_php() {
  local version="$1"; shift
  local packages=("$@")

  section "Installing PHP ${version}"
  echo ""

  # Map selected package names to actual apt package names
  local apt_packages=()
  for pkg in "${packages[@]}"; do
    if [[ "$pkg" == "base" ]]; then
      apt_packages+=("php${version}")
    else
      apt_packages+=("php${version}-${pkg}")
    fi
  done

  msg_info "Packages: ${apt_packages[*]}"
  echo ""

  # Ensure DEBIAN_FRONTEND is noninteractive to avoid hangs on prompts
  run_step "Installing PHP ${version} and extensions" \
    bash -c "DEBIAN_FRONTEND=noninteractive $SUDO apt-get install -y ${apt_packages[*]}"
}

# ─────────────────────────────────────────────────────────────
#   PHP-FPM Installation
# ─────────────────────────────────────────────────────────────
install_fpm() {
  local version="$1"
  run_step "Installing php${version}-fpm" \
    bash -c "DEBIAN_FRONTEND=noninteractive $SUDO apt-get install -y php${version}-fpm"
}

# ─────────────────────────────────────────────────────────────
#   Web Server Integrations
# ─────────────────────────────────────────────────────────────

integrate_apache() {
  local version="$1"
  section "Integrating with Apache"
  run_step "Enabling proxy_fcgi and setenvif" \
    $SUDO a2enmod proxy_fcgi setenvif
  run_step "Enabling php${version}-fpm configuration" \
    $SUDO a2enconf "php${version}-fpm"
  run_step "Restarting Apache" \
    $SUDO systemctl restart apache2
}

integrate_nginx() {
  local version="$1"
  section "Integrating with Nginx"
  msg_info "Nginx configuration snippet for PHP ${version}-fpm:"
  echo ""
  echo -e "    ${BRIGHT_WHITE}fastcgi_pass unix:/var/run/php/php${version}-fpm.sock;${RESET}"
  echo ""
}

# ─────────────────────────────────────────────────────────────
#   Helpers
# ─────────────────────────────────────────────────────────────

set_default_php() {
  local version="$1"
  section "Setting PHP ${version} as default"
  run_step "Updating alternatives: php" \
    $SUDO update-alternatives --set php "/usr/bin/php${version}"
}

remove_old_php() {
  local version="$1"
  msg_warn "Existing PHP ${version} detected. Consider removing it later if not needed."
}
