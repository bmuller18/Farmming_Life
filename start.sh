#!/bin/bash

# Farming Life - Startup Script
# Inicia Backend (Flask) + Frontend (HTTP Server)

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Starting Farming Life..."
echo ""

# Activate virtual environment
source "$PROJECT_DIR/env/bin/activate"

# Start Backend
echo "📡 Starting Backend (Flask) on http://localhost:5000..."
cd "$PROJECT_DIR"
python backend/app.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Start Frontend
echo "🌐 Starting Frontend (HTTP Server) on http://localhost:8000..."
cd "$PROJECT_DIR/frontend"
python -m http.server 8000 > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

echo ""
echo "✅ Servers running!"
echo ""
echo "📍 Open your browser:"
echo "   → http://localhost:8000 (Frontend)"
echo ""
echo "🔗 API: http://localhost:5000/api"
echo ""
echo "📋 Logs:"
echo "   Backend:  tail -f /tmp/backend.log"
echo "   Frontend: tail -f /tmp/frontend.log"
echo ""
echo "🛑 To stop: kill $BACKEND_PID $FRONTEND_PID"
echo "   Or: pkill -f 'python.*app.py' && pkill -f 'http.server'"
echo ""

# Keep script running
wait
