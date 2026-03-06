#!/bin/bash

echo "======================================"
echo "  Laravel Dev Setup Installer"
echo "======================================"
echo ""

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found."
    echo "Please install Python 3.9+ first:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo "  Arch: sudo pacman -S python python-pip"
    exit 1
fi

# Determine the best pip command
if command -v pip &> /dev/null; then
    PIP_CMD="pip"
elif command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
else
    PIP_CMD="python3 -m pip"
fi

echo "Using Python: $(python3 --version)"
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
