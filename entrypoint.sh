#!/bin/bash
# Start Flask Backend in background
gunicorn --bind 127.0.0.1:5001 --chdir backend app:app &

# Wait for backend to initialize
sleep 2

# Start Streamlit Frontend
export FLASK_API_URL="http://127.0.0.1:5001/api/v1"
PORT="${PORT:-7860}"
streamlit run Frontend/ui.py --server.port "$PORT" --server.address 0.0.0.0
