#!/bin/bash

# Quick start script for development
echo "🚀 Starting RAG Question Paper Validation System..."

# Check if backend virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "❌ Backend not set up. Please run ./setup.sh first"
    exit 1
fi

# Check if frontend node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "❌ Frontend not set up. Please run ./setup.sh first"
    exit 1
fi

# Start backend in background
echo "🔧 Starting backend server..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo """
✅ Both servers are starting up!

- Backend: http://localhost:5001
- Frontend: http://localhost:5174

Press Ctrl+C to stop both servers
"""

# Function to cleanup on exit
cleanup() {
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on exit
trap cleanup INT TERM

# Wait for user to stop
wait
