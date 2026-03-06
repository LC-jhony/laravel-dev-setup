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
    OS_CODENAME="${VERSION_CODENAME:-$(lsb_release -sc 2>/dev/null || echo unknown)}"
    OS_PRETTY="${PRETTY_NAME:-${NAME:-unknown}}"
  else
    OS_ID="unknown"
    OS_CODENAME="unknown"
    OS_PRETTY="$(uname -sr)"
  fi

  case "$OS_ID" in
    ubuntu|linuxmint|pop|elementary|zorin|neon)
      DISTRO_TYPE="ubuntu"
      ;;
    debian|raspbian|kali|devuan)
      DISTRO_TYPE="debian"
      ;;
    *)
      echo -e "\n   ${FAIL}  ${BRIGHT_RED}Unsupported distro: ${OS_ID}${RESET}"
      echo -e "   ${INFO}  This installer supports Ubuntu and Debian (and derivatives)."
      exit 1
      ;;
  esac
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