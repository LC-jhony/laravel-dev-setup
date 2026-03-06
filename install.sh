#!/bin/bash

echo "Installing Textual dependencies..."
pip install textual "textual[dev]"

echo "Installing project dependencies..."
pip install -e .
