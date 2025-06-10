#!/bin/bash

# Setup script for RAG Question Paper Validation System
echo "🚀 Setting up RAG Question Paper Validation System..."

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the simple_app directory"
    exit 1
fi

# Backend setup
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create uploads directory
mkdir -p uploads

echo "✅ Backend setup complete!"

# Frontend setup
echo "📦 Setting up frontend..."
cd ../frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

echo "✅ Frontend setup complete!"

cd ..

echo """
🎉 Setup complete! 

To start the application:

1. Start the backend:
   cd backend
   source venv/bin/activate
   python app.py

2. In a new terminal, start the frontend:
   cd frontend
   npm run dev

3. Open your browser to:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000

Happy validating! 🎓
"""
