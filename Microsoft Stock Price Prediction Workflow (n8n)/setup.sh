#!/bin/bash
# Setup script for Microsoft Stock Price Prediction Workflow (n8n)

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "[✔] Python virtual environment and dependencies installed."
echo "[✔] You can now run: docker-compose -f docker-compose.production.yml up -d"
