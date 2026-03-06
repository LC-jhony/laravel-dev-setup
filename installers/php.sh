#!/bin/bash
# ============================================================
#   installers/php.sh — PHP installation logic
# ============================================================

PHP_PACKAGES_DEFAULT=(curl pgsql fpm gd imap intl mbstring mysql opcache soap xml zip bcmath)

# ── Install PHP core and extensions ─────────────────────────
install_php() {
  local version="$1"; shift
  local packages=("$@")
  local apt_packages=()

  section "Installing PHP ${version}"
  echo ""

  # Map simplified package names to full apt package names
  for pkg in "${packages[@]}"; do
    case "$pkg" in
      base)    apt_packages+=("php${version}") ;;
      cli)     apt_packages+=("php${version}-cli") ;;
      common)  apt_packages+=("php${version}-common") ;;
      fpm)     apt_packages+=("php${version}-fpm") ;;
      *)       apt_packages+=("php${version}-${pkg}") ;;
    esac
  done

  # Ensure base, cli and common are always included if not specified
  [[ ! " ${packages[*]} " =~ " base " ]] && apt_packages+=("php${version}")
  [[ ! " ${packages[*]} " =~ " cli " ]] && apt_packages+=("php${version}-cli")
  [[ ! " ${packages[*]} " =~ " common " ]] && apt_packages+=("php${version}-common")

  run_step "Installing PHP ${version} packages" \
    $SUDO apt-get install -y "${apt_packages[@]}"

  msg_ok "PHP ${version} installed"
}

# ── Install PHP-FPM ─────────────────────────────────────────
install_fpm() {
  local version="$1"
  section "Installing PHP${version}-FPM"
  echo ""

  run_step "Installing php${version}-fpm" \
    $SUDO apt-get install -y "php${version}-fpm"

  run_step "Starting php${version}-fpm service" \
    $SUDO systemctl enable --now "php${version}-fpm"

  msg_ok "PHP-FPM ${version} is running"
}

# ── Integrate with Apache ───────────────────────────────────
integrate_apache() {
  local version="$1"
  section "Integrating PHP ${version} with Apache"
  echo ""

  if ! command -v apache2 &>/dev/null; then
    run_step "Installing Apache2" \
      $SUDO apt-get install -y apache2
  fi

  run_step "Installing libapache2-mod-php${version}" \
    $SUDO apt-get install -y "libapache2-mod-php${version}"

  run_step "Enabling Apache actions and proxy_fcgi modules" \
    $SUDO a2enmod actions proxy_fcgi alias

  run_step "Enabling PHP ${version} FPM configuration" \
    $SUDO a2enconf "php${version}-fpm"

  run_step "Restarting Apache2" \
    $SUDO systemctl restart apache2

  msg_ok "Apache integrated with PHP ${version} (via FPM)"
}

# ── Integrate with Nginx ────────────────────────────────────
integrate_nginx() {
  local version="$1"
  section "Integrating PHP ${version} with Nginx"
  echo ""

  if ! command -v nginx &>/dev/null; then
    run_step "Installing Nginx" \
      $SUDO apt-get install -y nginx
  fi

  msg_info "Nginx detected. PHP-FPM socket is at: /run/php/php${version}-fpm.sock"
  msg_ok "Nginx integration ready (use the socket in your server blocks)"
}

# ── Set as default PHP version ──────────────────────────────
set_default_php() {
  local version="$1"
  section "Setting PHP ${version} as System Default"
  echo ""

  run_step "Updating update-alternatives for php" \
    $SUDO update-alternatives --set php "/usr/bin/php${version}"

  if command -v "phpize${version}" &>/dev/null; then
    $SUDO update-alternatives --set phpize "/usr/bin/phpize${version}" 2>/dev/null || true
  fi
  if command -v "php-config${version}" &>/dev/null; then
    $SUDO update-alternatives --set php-config "/usr/bin/php-config${version}" 2>/dev/null || true
  fi

  msg_ok "System default PHP set to ${version}"
}

# ── Remove old PHP versions ─────────────────────────────────
remove_old_php() {
  local old_version="$1"
  section "Cleaning up old PHP ${old_version}"
  echo ""

  if prompt_confirm "Remove existing PHP ${old_version} packages?" "n"; then
    run_step "Removing php${old_version}*" \
      bash -c "$SUDO apt-get purge -y php${old_version}* && $SUDO apt-get autoremove -y"
    msg_ok "PHP ${old_version} removed"
  else
    msg_info "Kept existing PHP ${old_version}"
  fi
}
