#!/bin/bash

# Super-Scraper Launcher Script
# This script starts the Streamlit application

echo "🚀 Starting Super-Scraper..."
echo "================================"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys"
fi

# Start Streamlit app
echo ""
echo "✅ Starting Streamlit application..."
echo "📊 The app will open in your browser automatically"
echo "🔗 URL: http://localhost:8502"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================"
echo ""

# Clear log file
> debug.log

# Backend Logs Window (Agents & Errors)
echo "📜 Opening Backend Log window..."
osascript -e "tell application \"Terminal\" to do script \"cd \\\"$SCRIPT_DIR\\\" && echo '--- BACKEND LOGS (Agents & Errors) ---' && tail -f debug.log | grep --line-buffered -E 'DEBUG|Error|Traceback|Exception'\""

# Frontend Logs Window (Server & Requests)
echo "📜 Opening Frontend Log window..."
osascript -e "tell application \"Terminal\" to do script \"cd \\\"$SCRIPT_DIR\\\" && echo '--- FRONTEND LOGS (Server) ---' && tail -f debug.log | grep --line-buffered -v -E 'DEBUG|Error|Traceback|Exception'\""

# Run Streamlit and redirect output to log file
./venv/bin/streamlit run app.py > debug.log 2>&1
