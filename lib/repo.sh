#!/bin/bash
# ============================================================
#   lib/repo.sh — PHP repository setup
#   Ubuntu  : ondrej/php PPA
#   Debian  : packages.sury.org/php
# ============================================================

setup_repo() {
  if [[ "$DISTRO_TYPE" == "ubuntu" ]]; then
    _setup_repo_ubuntu
  else
    _setup_repo_debian
  fi
}

_setup_repo_ubuntu() {
  section "Adding PHP Repository (Ubuntu — ondrej/php PPA)"
  echo ""

  run_step "Installing software-properties-common" \
    $SUDO apt-get install -y software-properties-common

  run_step "Adding ondrej/php PPA" \
    bash -c "LC_ALL=C.UTF-8 $SUDO add-apt-repository -y ppa:ondrej/php"

  run_step "Updating package lists" \
    $SUDO apt-get update -qq
}

_setup_repo_debian() {
  section "Adding PHP Repository (Debian — sury.org)"
  echo ""

  run_step "Installing prerequisites" \
    $SUDO apt-get install -y \
      lsb-release ca-certificates curl apt-transport-https gnupg

  run_step "Downloading sury.org signing keyring" \
    bash -c "$SUDO curl -sSLo /tmp/debsuryorg-archive-keyring.deb \
      https://packages.sury.org/debsuryorg-archive-keyring.deb"

  run_step "Installing signing keyring" \
    $SUDO dpkg -i /tmp/debsuryorg-archive-keyring.deb

  run_step "Adding sury.org source list" \
    bash -c "$SUDO sh -c 'echo \
      \"deb [signed-by=/usr/share/keyrings/deb.sury.org-php.gpg] \
      https://packages.sury.org/php/ ${OS_CODENAME} main\" \
      > /etc/apt/sources.list.d/php.list'"

  run_step "Updating package lists" \
    $SUDO apt-get update -qq
}