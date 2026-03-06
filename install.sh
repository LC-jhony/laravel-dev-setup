#!/bin/bash

echo "======================================"
echo "  Laravel Dev Setup Installer"
echo "======================================"
echo ""

# Check if textual is installed
if ! python3 -c "import textual" 2>/dev/null; then
    echo "Error: Textual is not installed."
    echo "Please install it first:"
    echo "  pip install textual textual[dev]"
    exit 1
fi

echo "Starting Laravel Dev Setup Installer..."
echo ""

# Run the installer
python3 -m installer
