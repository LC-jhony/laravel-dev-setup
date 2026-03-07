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

# 1. Pre-flight checks & Auto-Installation
echo -ne "  ${CYAN}●${RESET} Preparing environment... "

# Required packages for the bootstrapper to work
REQUIRED_PKGS=("git" "curl" "python3" "python3-pip" "unzip" "sudo")
MISSING_PKGS=()

for pkg in "${REQUIRED_PKGS[@]}"; do
    if [[ "$pkg" == "python3-pip" ]]; then
        if ! command -v pip3 &>/dev/null; then MISSING_PKGS+=("$pkg"); fi
    elif ! command -v "$pkg" &>/dev/null; then
        MISSING_PKGS+=("$pkg")
    fi
done

if [ ${#MISSING_PKGS[@]} -gt 0 ]; then
    echo -e "\n  ${YELLOW}●${RESET} Installing missing tools: ${MISSING_PKGS[*]}..."
    sudo apt-get update &>/dev/null
    sudo apt-get install -y "${MISSING_PKGS[@]}" &>/dev/null
    echo -e "  ${GREEN}●${RESET} Tools installed successfully."
else
    echo -e "${GREEN}Ready${RESET}"
fi

# 2. Preparation
if [ -d "$INSTALL_PATH" ]; then
    echo -e "  ${YELLOW}●${RESET} Existing installation found. Updating... "
    rm -rf "$INSTALL_PATH"
fi

# 3. Install Rich
echo -ne "  ${CYAN}●${RESET} Installing Rich UI library... "
pip3 install rich --break-system-packages &>/dev/null || pip3 install rich &>/dev/null
echo -e "${GREEN}Success${RESET}"

# 4. Clone repository
echo -ne "  ${CYAN}●${RESET} Downloading components from GitHub... "
if git clone --depth 1 "$REPO_URL" "$INSTALL_PATH" &>/dev/null; then
    echo -e "${GREEN}Success${RESET}"
else
    echo -e "${RED}Failed${RESET}"
    exit 1
fi

# 5. Handover to main installer
echo -e "  ${CYAN}●${RESET} Launching interactive wizard..."
echo ""
cd "$INSTALL_PATH"
python3 main.py
