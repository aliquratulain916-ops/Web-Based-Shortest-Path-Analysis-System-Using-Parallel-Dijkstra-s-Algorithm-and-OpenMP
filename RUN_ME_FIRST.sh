#!/bin/bash

# ============================================================
# Dijkstra's Algorithm - Automatic Setup Script
# Run this first on Mac/Linux
# ============================================================

echo ""
echo "============================================================"
echo "DIJKSTRA'S SHORTEST PATH - SETUP WIZARD"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo ""
    echo "Install Python with:"
    echo "  - Mac: brew install python3"
    echo "  - Linux: sudo apt-get install python3 python3-pip"
    echo ""
    exit 1
fi

echo "✓ Python found"
python3 --version
echo ""

# Install dependencies
echo "Installing dependencies... (this may take 2-3 minutes)"
echo ""
pip3 install -r requirements.txt --quiet

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    echo "Try: pip3 install --upgrade pip"
    exit 1
fi

echo ""
echo "✓ Dependencies installed successfully!"
echo ""
echo "============================================================"
echo "SETUP COMPLETE - Starting Application"
echo "============================================================"
echo ""

# Run the application
python3 main.py
