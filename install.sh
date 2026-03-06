#!/bin/bash

echo "======================================"
echo "  Laravel Dev Setup Installer"
echo "======================================"
echo ""

# Check if python3 exists
if command -v python3 &> /dev/null; then
    echo "✓ Python3 found: $(python3 --version)"
else
    echo "✗ Python3 not found. Installing..."
    
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
        echo "ERROR: Could not detect Linux distribution"
        exit 1
    fi
fi

echo ""
echo "Checking pip..."
if command -v pip3 &> /dev/null; then
    echo "✓ pip3 found"
    PIP_CMD="pip3"
elif python3 -m pip --version &> /dev/null; then
    echo "✓ pip via python3 -m pip"
    PIP_CMD="python3 -m pip"
else
    echo "Installing pip..."
    python3 -m ensurepip --upgrade || python3 -m pip install --upgrade pip
    PIP_CMD="python3 -m pip"
fi

echo ""
echo "Installing textual and textual[dev]..."
python3 -m pip install --user textual "textual[dev]" --break-system-packages 2>/dev/null || \
python3 -m pip install --user textual "textual[dev]" || \
sudo pip3 install textual "textual[dev]"

echo ""
echo "Installing project dependencies..."
python3 -m pip install -e . --break-system-packages 2>/dev/null || \
python3 -m pip install -e . || \
sudo pip3 install -e .

echo ""
echo "======================================"
echo "  Installation complete!"
echo "======================================"
echo ""
echo "Run with:"
echo "  python3 -m installer"
