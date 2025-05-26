#!/bin/bash

# Test Script for Inbox Clarity Backend

echo "🧪 Running Inbox Clarity Backend Tests"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Using test configuration."
    export GEMINI_API_KEY="test-key"
    export GOOGLE_CLIENT_ID="test-client-id"
    export GOOGLE_CLIENT_SECRET="test-client-secret"
    export SUPABASE_URL="https://test.supabase.co"
    export SUPABASE_SERVICE_ROLE_KEY="test-service-key"
    export SECRET_KEY="test-secret-key"
    export ENCRYPTION_KEY="test-encryption-key"
fi

# Run tests
echo "🚀 Running unit tests..."
python -m pytest test_app.py -v

# Check test results
if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed. Please check the output above."
    exit 1
fi

# Optional: Run app in test mode
echo ""
echo "🔧 Testing app startup..."
timeout 5s python app.py &
APP_PID=$!
sleep 2

# Check if app is running
if kill -0 $APP_PID 2>/dev/null; then
    echo "✅ App starts successfully!"
    kill $APP_PID
else
    echo "❌ App failed to start. Check configuration."
    exit 1
fi

echo ""
echo "🎉 All tests completed successfully!"
echo "   Backend is ready for deployment."
