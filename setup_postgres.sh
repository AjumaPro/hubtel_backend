#!/bin/bash

# GLICO Capital - PostgreSQL Setup Script
# This script helps set up PostgreSQL for the Django application

set -e

echo "🚀 GLICO Capital - PostgreSQL Setup"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: Please run this script from the hubtel_backend directory"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Virtual environment not detected"
    echo "   It's recommended to activate your virtual environment first"
fi

# Install PostgreSQL dependencies
echo "📦 Installing PostgreSQL dependencies..."
pip install psycopg2-binary==2.9.9

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env file created from template"
        echo "   Please edit .env file with your PostgreSQL credentials"
    else
        echo "❌ .env.example not found"
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi

# Check PostgreSQL installation
echo "🔍 Checking PostgreSQL installation..."
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL client found"
    psql --version
else
    echo "⚠️  PostgreSQL client not found"
    echo "   Please install PostgreSQL client tools:"
    echo "   - macOS: brew install postgresql"
    echo "   - Ubuntu: sudo apt-get install postgresql-client"
    echo "   - CentOS: sudo yum install postgresql"
fi

# Check if PostgreSQL server is running
echo "🔍 Checking PostgreSQL server connection..."
if command -v pg_isready &> /dev/null; then
    if pg_isready -h localhost -p 5432 &> /dev/null; then
        echo "✅ PostgreSQL server is running"
    else
        echo "⚠️  PostgreSQL server is not running or not accessible"
        echo "   Please start PostgreSQL server:"
        echo "   - macOS: brew services start postgresql"
        echo "   - Ubuntu: sudo systemctl start postgresql"
        echo "   - CentOS: sudo systemctl start postgresql"
    fi
else
    echo "⚠️  pg_isready not found, cannot check server status"
fi

echo ""
echo "🎉 Setup completed!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your PostgreSQL credentials"
echo "2. Set USE_POSTGRESQL=True in .env file"
echo "3. Create PostgreSQL database:"
echo "   createdb glico_capital"
echo "4. Run migration script:"
echo "   python migrate_to_postgres.py"
echo "5. Test the application:"
echo "   python manage.py runserver"
echo ""
echo "For help, see the README.md file" 