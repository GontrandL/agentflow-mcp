#!/bin/bash

# SmartOrchestrator Dashboard Startup Script

echo "╔══════════════════════════════════════════════════════════╗"
echo "║    SmartOrchestrator Metrics Dashboard                  ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if logs directory exists
if [ ! -d "logs" ]; then
    echo "Creating logs directory..."
    mkdir -p logs
fi

# Check if Flask is installed
if ! python -c "import flask" 2>/dev/null; then
    echo "ERROR: Flask not installed"
    echo "Please install dependencies:"
    echo "  pip install -r agentflow/requirements.txt"
    exit 1
fi

# Check if metrics file exists
if [ ! -f "logs/orchestrator_metrics.json" ]; then
    echo "⚠️  No metrics file found yet."
    echo "   Run SmartOrchestrator first to generate data:"
    echo "   python test_dashboard_integration.py"
    echo ""
fi

echo "Starting dashboard server..."
echo "Dashboard URL: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the Flask server
python dashboard_server.py
