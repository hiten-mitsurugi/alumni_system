#!/bin/bash

echo "Starting Alumni System Development Environment..."

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Kill any existing processes on our ports
echo "Checking for existing processes..."
pkill -f "npm run dev" 2>/dev/null || true
pkill -f "daphne" 2>/dev/null || true
sleep 2

# Start Frontend
echo "Starting Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"
cd ..

# Wait a moment
sleep 3

# Start Backend
echo "Starting Backend..."
cd backend
source env/bin/activate
daphne -b 0.0.0.0 -p 8000 alumni_system.asgi:application &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"
cd ..

echo ""
echo "Alumni System is now running:"
echo "Frontend: http://localhost:5173"
echo "Backend: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop both services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down services..."
    kill $FRONTEND_PID 2>/dev/null || true
    kill $BACKEND_PID 2>/dev/null || true
    pkill -f "npm run dev" 2>/dev/null || true
    pkill -f "daphne" 2>/dev/null || true
    echo "Services stopped."
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Wait for background processes
wait