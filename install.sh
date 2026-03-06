#!/bin/bash

set -e

echo "======================================"
echo "  Laravel Dev Setup Installer"
echo "======================================"
echo ""

# Detect Linux distribution and install Python
install_python() {
    echo "Installing Python 3..."
    
    if command -v apt-get &> /dev/null; then
        echo "Detected: Debian/Ubuntu"
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv git curl
    elif command -v dnf &> /dev/null; then
        echo "Detected: Fedora/RHEL"
        sudo dnf install -y python3 python3-pip git curl
    elif command -v yum &> /dev/null; then
        echo "Detected: CentOS"
        sudo yum install -y python3 python3-pip git curl
    elif command -v pacman &> /dev/null; then
        echo "Detected: Arch Linux"
        sudo pacman -Sy --noconfirm python python-pip git curl
    elif command -v zypper &> /dev/null; then
        echo "Detected: openSUSE"
        sudo zypper install -y python3 python3-pip git curl
    elif command -v apk &> /dev/null; then
        echo "Detected: Alpine"
        sudo apk add python3 py3-pip git curl
    else
        echo "Error: Could not detect your Linux distribution."
        echo "Please install Python 3.9+ manually."
        exit 1
    fi
}

# Check if python3 is available, install if not
if ! command -v python3 &> /dev/null; then
    install_python
fi

echo "Python version: $(python3 --version)"
echo ""

# Install pip if not available
if ! python3 -m pip --version &> /dev/null; then
    echo "Installing pip..."
    python3 -m ensurepip --upgrade || python3 -m pip install --upgrade pip
fi

echo "Using pip: $(python3 -m pip --version)"
echo ""

# Install Textual
echo "Installing textual and textual[dev]..."
python3 -m pip install textual "textual[dev]"

echo ""
echo "Installing project dependencies..."
python3 -m pip install -e .

echo ""
echo "======================================"
echo "  Installation complete!"
echo "======================================"
echo ""
echo "Run the installer:"
echo "  python3 -m installer"
