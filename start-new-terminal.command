#!/bin/bash

# Super-Scraper Launcher - Opens in New Terminal Window
# Double-click this file to start the app in a new terminal

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Open a new Terminal window and run the start script
osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR' && ./start.sh\""

echo "Super-Scraper is starting in a new terminal window..."
