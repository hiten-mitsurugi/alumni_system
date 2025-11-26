#!/bin/bash

echo "========================================"
echo "Starting Alumni System for LAN Access"
echo "========================================"
echo ""

# Get local IP address
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    IP=$(ipconfig getifaddr en0 || ipconfig getifaddr en1)
else
    # Linux
    IP=$(hostname -I | awk '{print $1}')
fi

echo "Your Local IP: $IP"
echo ""
echo "Frontend will be accessible at: http://$IP:5173"
echo "Backend will be accessible at: http://$IP:8000"
echo ""
echo "========================================"
echo ""

# Start backend
cd Backend
python manage.py runserver 0.0.0.0:8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
cd Frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "Both services started!"
echo "Share this URL with others on your network: http://$IP:5173"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
