#!/bin/bash

# Background Removal API Startup Script

echo "🚀 Starting Background Removal API..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  WARNING: .env file not found!"
    echo "📝 Creating .env from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env file created"
        echo ""
        echo "⚠️  IMPORTANT: Edit .env and add your REPLICATE_API_TOKEN"
        echo "   Get your token from: https://replicate.com/account/api-tokens"
        echo ""
        read -p "Press Enter after you've updated the .env file..."
    else
        echo "❌ .env.example not found. Please create .env manually with:"
        echo "   REPLICATE_API_TOKEN=your_token_here"
        exit 1
    fi
fi

# Start the API
echo ""
echo "🌟 Starting API server..."
echo "📚 Documentation will be available at: http://localhost:8000/docs"
echo ""
python main.py

