#!/bin/bash
# Quick Start Script for File Integrity & Authenticity Verification Platform

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║  File Integrity & Authenticity Verification Platform  ║"
echo "║                   Quick Start Script                       ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if MongoDB is running
echo "Checking MongoDB..."
if brew services list | grep -q "mongodb-community.*started"; then
    echo "✓ MongoDB is running"
else
    echo "✗ MongoDB is not running"
    echo "  Starting MongoDB..."
    brew services start mongodb-community
    sleep 2
    echo "✓ MongoDB started"
fi
echo ""

# Check if dependencies are installed
echo "Checking dependencies..."
if python3 -c "import fastapi" 2>/dev/null; then
    echo "✓ Dependencies installed"
else
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi
echo ""

# Run system tests
echo "Running system tests..."
python3 test_system.py
TEST_RESULT=$?

if [ $TEST_RESULT -eq 0 ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                   SYSTEM READY!                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "To start the server, run:"
    echo "  python3 -m uvicorn gateway.main:app --reload"
    echo ""
    echo "To use the CLI, run:"
    echo "  python3 cli/client.py --help"
    echo ""
    echo "API Documentation will be available at:"
    echo "  http://localhost:8000/docs"
    echo ""
else
    echo ""
    echo "✗ Some tests failed. Please check the errors above."
    exit 1
fi
