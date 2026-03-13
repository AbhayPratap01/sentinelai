#!/bin/bash
echo "Starting SentinelAI..."
echo ""

# Backend
echo "[1/2] Starting backend on http://localhost:8000"
cd backend
pip install -r requirements.txt -q
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

sleep 2

# Frontend
echo "[2/2] Starting frontend on http://localhost:3000"
cd frontend
npm install --silent
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "SentinelAI is running!"
echo "  Dashboard : http://localhost:3000"
echo "  API docs  : http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers."

wait $BACKEND_PID $FRONTEND_PID
