#!/bin/bash

# Multi Desk Backend Startup Script

echo "🚀 Starting Multi Desk Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi

# Navigate to backend directory
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if MongoDB is running (optional)
echo "🗄️  Checking MongoDB connection..."

# Set environment variables if .env file exists
if [ -f ".env" ]; then
    echo "🔐 Loading environment variables..."
    export $(cat .env | xargs)
fi

# Start the FastAPI server
echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📧 Email service configured with: $MAIL_USER"
echo "🔑 Ready to handle authentication requests..."

uvicorn main:app --host 0.0.0.0 --port 8000 --reload