#!/bin/bash
# ============================================================
#   lib/detect.sh — OS & PHP detection helpers
# ============================================================

# Populates: OS_ID, OS_CODENAME, OS_PRETTY, DISTRO_TYPE
detect_os() {
  if [[ -f /etc/os-release ]]; then
    # shellcheck source=/dev/null
    . /etc/os-release
    OS_ID="${ID}"
    OS_VERSION="${VERSION_ID}"
    OS_CODENAME="${VERSION_CODENAME:-$(lsb_release -sc 2>/dev/null || echo unknown)}"
    OS_PRETTY="${PRETTY_NAME:-${NAME:-unknown}}"
  else
    OS_ID="unknown"
    OS_VERSION="0.0"
    OS_CODENAME="unknown"
    OS_PRETTY="$(uname -sr)"
  fi

  # Strict Ubuntu 24.04+ check
  if [[ "$OS_ID" == "ubuntu" ]]; then
    # Check if version is 24.04 or greater
    # Using sort -V for version comparison
    if [[ $(echo -e "24.04\n${OS_VERSION}" | sort -V | head -n1) == "24.04" ]]; then
      DISTRO_TYPE="ubuntu"
    else
      echo -e "\n   ${RED}${FAIL}  Unsupported Ubuntu version: ${OS_VERSION}${RESET}"
      echo -e "   ${INFO}  This installer requires Ubuntu 24.04 or newer."
      exit 1
    fi
  else
    echo -e "\n   ${RED}${FAIL}  Unsupported distro: ${OS_ID}${RESET}"
    echo -e "   ${INFO}  This installer EXCLUSIVELY supports Ubuntu 24.04+."
    exit 1
  fi
}

# Populates: EXISTING_PHP (empty if none)
detect_existing_php() {
  EXISTING_PHP=""
  if command -v php &>/dev/null; then
    EXISTING_PHP=$(php -r 'echo PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;' 2>/dev/null || true)
  fi
}

# Check that we have sudo or are root
check_privileges() {
  SUDO=""
  if [[ $EUID -ne 0 ]]; then
    SUDO="sudo"
    if ! command -v sudo &>/dev/null; then
      msg_fail "Not running as root and 'sudo' is not installed."
      echo -e "   ${INFO}  Run this script as root or install sudo first."
      exit 1
    fi
    msg_warn "Not root — will use sudo for privileged commands"
  else
    msg_ok "Running as root"
  fi
}

# Verify apt-get is available
check_apt() {
  if ! command -v apt-get &>/dev/null; then
    msg_fail "apt-get not found — Debian/Ubuntu system required"
    exit 1
  fi
  msg_ok "Package manager: APT"
}