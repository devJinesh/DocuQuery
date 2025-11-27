#!/bin/bash

echo "================================================"
echo "Starting DocuQuery Application"
echo "================================================"
echo

# Function to cleanup on exit
cleanup() {
    echo
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup INT TERM

# Start backend
echo "Starting backend server..."
cd backend
venv/bin/python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend
echo "Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo
echo "================================================"
echo "Application Running!"
echo "================================================"
echo
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo
echo "Press Ctrl+C to stop all servers"
echo

# Wait for processes
wait
