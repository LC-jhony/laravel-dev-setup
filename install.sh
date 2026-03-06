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

# Find pip command
find_pip() {
    if command -v pip3 &> /dev/null; then
        echo "pip3"
    elif command -v pip &> /dev/null; then
        echo "pip"
    elif python3 -m pip --version &> /dev/null; then
        echo "python3 -m pip"
    else
        echo "pip not found. Trying ensurepip..."
        python3 -m ensurepip --upgrade 2>/dev/null || true
        python3 -m pip install --upgrade pip 2>/dev/null || true
        
        if python3 -m pip --version &> /dev/null; then
            echo "python3 -m pip"
        else
            echo "ERROR: Could not find or install pip"
            exit 1
        fi
    fi
}

PIP_CMD=$(find_pip)
echo "Using: $PIP_CMD"
echo ""

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install Textual
echo ""
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
echo "Verify installation:"
echo "  python3 -c 'import textual; print(textual.__version__)'"
echo ""
echo "Run the installer:"
echo "  python3 -m installer"
echo "  or"
echo "  textual run src/installer/app.py"
