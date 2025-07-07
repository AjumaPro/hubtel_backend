#!/bin/bash

echo "🚀 Setting up Hubtel Payment Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your Hubtel API credentials!"
fi

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Create superuser
echo "👤 Creating superuser..."
python manage.py createsuperuser --username admin --email admin@example.com --noinput

echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your Hubtel API credentials"
echo "2. Run: python manage.py runserver"
echo "3. Access admin at: http://localhost:8000/admin"
echo "4. API endpoints at: http://localhost:8000/api/payments/"
echo ""
echo "🔑 Default admin credentials:"
echo "Username: admin"
echo "Password: (you'll need to set this manually)"
echo ""
echo "💡 To set admin password, run:"
echo "python manage.py changepassword admin" 