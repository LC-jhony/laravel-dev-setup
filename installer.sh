#!/bin/bash
# ============================================================
#   LARAVEL DEV SETUP — Professional Bootstrap Installer
#   Compatible with: Ubuntu, Debian, WSL
# ============================================================

set -e

# Colors for bootstrap
CYAN="\033[96m"
GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
RESET="\033[0m"
BOLD="\033[1m"

INSTALL_PATH="${HOME}/.laravel-dev-setup"
REPO_URL="https://github.com/LC-jhony/laravel-dev-setup.git"

clear
echo -e "${CYAN}${BOLD}🚀 LARAVEL DEV SETUP — Professional Bootstrap${RESET}"
echo -e "${DIM}--------------------------------------------------${RESET}"

# 1. Pre-flight checks
echo -ne "  ${CYAN}●${RESET} Checking prerequisites... "
for cmd in git curl sudo; do
    if ! command -v "$cmd" &>/dev/null; then
        echo -e "\n  ${RED}✖ Error: '$cmd' is not installed.${RESET}"
        exit 1
    fi
done
echo -e "${GREEN}Done${RESET}"

# 2. Preparation
if [ -d "$INSTALL_PATH" ]; then
    echo -e "  ${YELLOW}●${RESET} Existing installation found. Updating... "
    rm -rf "$INSTALL_PATH"
fi

# 3. Clone repository
echo -ne "  ${CYAN}●${RESET} Downloading components from GitHub... "
if git clone --depth 1 "$REPO_URL" "$INSTALL_PATH" &>/dev/null; then
    echo -e "${GREEN}Success${RESET}"
else
    echo -e "${RED}Failed${RESET}"
    exit 1
fi

# 4. Handover to main installer
echo -e "  ${CYAN}●${RESET} Launching interactive wizard..."
echo ""
cd "$INSTALL_PATH"
bash install.sh
