#!/bin/bash
# ============================================================
#   lib/repo.sh — PHP repository setup (FIXED)
# ============================================================

setup_repo() {
  # Use DEBIAN_FRONTEND to ensure non-interactive APT calls
  export DEBIAN_FRONTEND=noninteractive

  if [[ "$DISTRO_TYPE" == "ubuntu" ]]; then
    _setup_repo_ubuntu
  else
    _setup_repo_debian
  fi
}

_setup_repo_ubuntu() {
  section "Adding PHP Repository (Ondrej PPA)"
  echo ""

  run_step "Prerequisites" \
    $SUDO apt-get install -y software-properties-common

  # LC_ALL=C.UTF-8 is common for PPA issues
  # -y confirms the prompt to press ENTER
  run_step "Adding PPA" \
    bash -c "LC_ALL=C.UTF-8 $SUDO add-apt-repository -y ppa:ondrej/php"

  run_step "Syncing package list" \
    $SUDO apt-get update -qq
}

_setup_repo_debian() {
  section "Adding PHP Repository (Sury.org)"
  echo ""

  run_step "Prerequisites" \
    $SUDO apt-get install -y lsb-release ca-certificates curl apt-transport-https gnupg

  run_step "Fetching Keyring" \
    bash -c "$SUDO curl -sSLo /usr/share/keyrings/deb.sury.org-php.gpg https://packages.sury.org/php/apt.gpg"

  run_step "Adding Sources" \
    bash -c "echo \"deb [signed-by=/usr/share/keyrings/deb.sury.org-php.gpg] https://packages.sury.org/php/ ${OS_CODENAME} main\" | $SUDO tee /etc/apt/sources.list.d/php.list"

  run_step "Syncing package list" \
    $SUDO apt-get update -qq
}
