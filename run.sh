#!/bin/bash

# AI Hotel Receptionist - Quick Start Script
# This script checks environment and starts the application

echo "=========================================="
echo "AI Hotel Receptionist - Starting..."
echo "=========================================="
echo ""

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not activated!"
    echo "Please run:"
    echo "  source venv/bin/activate  (Mac/Linux)"
    echo "  venv\\Scripts\\activate    (Windows)"
    echo ""
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Please copy .env.example to .env and configure it:"
    echo "  cp .env.example .env"
    echo ""
    exit 1
fi

# Check if database exists
if [ ! -f hotel_receptionist.db ]; then
    echo "📊 Database not found. Initializing..."
    python scripts/init_database.py
    echo ""
fi

# Start the application
echo "🚀 Starting AI Hotel Receptionist..."
echo ""
echo "Access the application at:"
echo "  - Main Page: http://localhost:8000"
echo "  - Chat UI: http://localhost:8000/api/chat-ui"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python main.py
