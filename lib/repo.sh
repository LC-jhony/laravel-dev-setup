#!/bin/bash
# ============================================================
#   lib/repo.sh — PHP repository setup (FIXED)
# ============================================================

setup_repo() {
  # Use DEBIAN_FRONTEND to ensure non-interactive APT calls
  export DEBIAN_FRONTEND=noninteractive
  _setup_repo_ubuntu
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
