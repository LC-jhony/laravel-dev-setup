#!/bin/bash

set -e

echo "======================================"
echo "  Laravel Dev Setup Installer"
echo "======================================"
echo ""

# Detect Linux distribution and set package manager
install_system_deps() {
    if command -v apt-get &> /dev/null; then
        echo "Detected: Debian/Ubuntu"
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv
    elif command -v dnf &> /dev/null; then
        echo "Detected: Fedora/RHEL"
        sudo dnf install -y python3 python3-pip
    elif command -v yum &> /dev/null; then
        echo "Detected: CentOS"
        sudo yum install -y python3 python3-pip
    elif command -v pacman &> /dev/null; then
        echo "Detected: Arch Linux"
        sudo pacman -Sy --noconfirm python python-pip
    elif command -v zypper &> /dev/null; then
        echo "Detected: openSUSE"
        sudo zypper install -y python3 python3-pip
    elif command -v apk &> /dev/null; then
        echo "Detected: Alpine"
        sudo apk add python3 py3-pip
    else
        echo "Error: Could not detect your Linux distribution."
        echo "Please install Python 3.9+ and pip manually."
        exit 1
    fi
}

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found. Installing system dependencies..."
    install_system_deps
fi

echo "Using Python: $(python3 --version)"
echo ""

# Find pip command
find_pip() {
    if command -v pip &> /dev/null; then
        echo "pip"
    elif command -v pip3 &> /dev/null; then
        echo "pip3"
    elif python3 -m pip --version &> /dev/null; then
        echo "python3 -m pip"
    else
        echo "pip not found. Trying to install..."
        python3 -m ensurepip --upgrade 2>/dev/null || python3 -m pip install --upgrade pip 2>/dev/null
        if python3 -m pip --version &> /dev/null; then
            echo "python3 -m pip"
        else
            echo "Error: Could not install pip. Please install it manually."
            exit 1
        fi
    fi
}

PIP_CMD=$(find_pip)
echo "Using pip: $PIP_CMD"
echo ""

echo "Installing Textual dependencies..."
$PIP_CMD install --upgrade pip
$PIP_CMD install textual "textual[dev]"

echo ""
echo "Installing project dependencies..."
$PIP_CMD install -e .

echo ""
echo "======================================"
echo "  Installation complete!"
echo "======================================"
echo "Run the installer with:"
echo "  python -m installer"
echo "  or"
echo "  textual run src/installer/app.py"
