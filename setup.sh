#!/usr/bin/env bash
set -euo pipefail

echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y ffmpeg libsndfile1 build-essential

echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing Python requirements..."
pip install -r requirements.txt

echo "Setup complete."
