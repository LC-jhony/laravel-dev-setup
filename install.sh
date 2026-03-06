#!/bin/bash

echo "======================================"
echo "  Laravel Dev Setup Installer"
echo "======================================"
echo ""

# Check if rich and questionary are installed
if ! python3 -c "import rich" 2>/dev/null; then
    echo "Error: Rich is not installed."
    echo "Please install it first:"
    echo "  pip install rich questionary"
    exit 1
fi

if ! python3 -c "import questionary" 2>/dev/null; then
    echo "Error: Questionary is not installed."
    echo "Please install it first:"
    echo "  pip install rich questionary"
    exit 1
fi

echo "Starting Laravel Dev Setup Installer..."
echo ""

# Run the installer
python3 -m installer
