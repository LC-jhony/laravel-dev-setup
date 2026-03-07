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
DIM="\033[2m"

INSTALL_PATH="${HOME}/.laravel-dev-setup"
REPO_URL="https://github.com/LC-jhony/laravel-dev-setup.git"

clear
echo -e "${CYAN}${BOLD}🚀 LARAVEL DEV SETUP — Professional Bootstrap${RESET}"
echo -e "${DIM}--------------------------------------------------${RESET}"

# 1. OS Compatibility Check
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS_ID="${ID}"
    OS_VERSION="${VERSION_ID}"
else
    OS_ID="unknown"
    OS_VERSION="0.0"
fi

if [[ "$OS_ID" != "ubuntu" ]] || [[ $(echo -e "24.04\n${OS_VERSION}" | sort -V | head -n1) != "24.04" ]]; then
    echo -e "  ${RED}●${RESET} Error: This installer EXCLUSIVELY supports Ubuntu 24.04 or newer."
    echo -e "    Current OS: ${OS_ID} ${OS_VERSION}"
    exit 1
fi

# 2. Pre-flight checks & Auto-Installation
echo -ne "  ${CYAN}●${RESET} Preparing environment... "

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

# 3. Preparation
if [ -d "$INSTALL_PATH" ]; then
    echo -e "  ${YELLOW}●${RESET} Existing installation found. Updating... "
    rm -rf "$INSTALL_PATH"
fi

# 4. Install Rich
echo -ne "  ${CYAN}●${RESET} Installing Rich UI library... "
# Use --break-system-packages for newer Debian/Ubuntu if needed, or simple pip install
pip3 install rich --break-system-packages &>/dev/null || pip3 install rich &>/dev/null
echo -e "${GREEN}Success${RESET}"

# 5. Clone repository
echo -ne "  ${CYAN}●${RESET} Downloading components from GitHub... "
if git clone --depth 1 "$REPO_URL" "$INSTALL_PATH" &>/dev/null; then
    echo -e "${GREEN}Success${RESET}"
else
    echo -e "${RED}Failed${RESET}"
    exit 1
fi

# 6. Handover to main installer
echo -e "  ${CYAN}●${RESET} Launching interactive wizard..."
echo ""
cd "$INSTALL_PATH"

# THE FIX: We use </dev/tty to ensure the Python script 
# gets the keyboard even if this script was piped from curl.
python3 main.py </dev/tty
