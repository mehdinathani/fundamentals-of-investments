#!/bin/bash
# Start PSX Investment System
# Backend: http://localhost:8000
# Frontend: http://localhost:5173

echo "Starting PSX Investment System..."
echo ""

# Start backend
echo "[1/2] Starting backend..."
cd "$(dirname "$0")"
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
sleep 2

# Check backend
if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "  ✅ Backend running on http://localhost:8000"
else
    echo "  ❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend
echo "[2/2] Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "  ✅ Frontend running on http://localhost:5173"
echo ""
echo "  📊 PSX Invest System is ready!"
echo "  Press Ctrl+C to stop both servers."

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
