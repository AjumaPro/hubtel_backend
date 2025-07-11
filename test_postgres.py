#!/usr/bin/env python3
"""
Test script to verify PostgreSQL setup and functionality
"""

import os
import sys
import django
from django.conf import settings
from django.db import connection

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hubtel_project.settings')
    django.setup()

def test_postgresql_connection():
    """Test PostgreSQL connection"""
    print("🔍 Testing PostgreSQL connection...")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ PostgreSQL connection successful!")
            print(f"   Version: {version}")
            return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def test_database_operations():
    """Test basic database operations"""
    print("\n🔍 Testing database operations...")
    
    try:
        # Test creating a table (if it doesn't exist)
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_table (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Test inserting data
            cursor.execute("""
                INSERT INTO test_table (name) VALUES (%s)
                ON CONFLICT DO NOTHING;
            """, ['test_record'])
            
            # Test selecting data
            cursor.execute("SELECT COUNT(*) FROM test_table;")
            count = cursor.fetchone()[0]
            
            print(f"✅ Database operations successful!")
            print(f"   Test table created/verified")
            print(f"   Test record count: {count}")
            return True
    except Exception as e:
        print(f"❌ Database operations failed: {e}")
        return False

def test_django_models():
    """Test Django model operations"""
    print("\n🔍 Testing Django models...")
    
    try:
        from payments.models import PaymentTransaction
        from kyc.models import KYCSubmission
        
        # Test model imports
        print("✅ Model imports successful")
        
        # Test database connection through Django
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM django_migrations;")
            migration_count = cursor.fetchone()[0]
            print(f"   Migration count: {migration_count}")
        
        return True
    except Exception as e:
        print(f"❌ Django model test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print("🧪 GLICO Capital - PostgreSQL Test")
    print("=" * 50)
    
    # Setup Django
    setup_django()
    
    # Check database configuration
    db_engine = settings.DATABASES['default']['ENGINE']
    print(f"📊 Database Engine: {db_engine}")
    
    if 'postgresql' not in db_engine:
        print("⚠️  Database is not configured for PostgreSQL")
        print("   Please set USE_POSTGRESQL=True in your .env file")
        return False
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    if test_postgresql_connection():
        tests_passed += 1
    
    if test_database_operations():
        tests_passed += 1
    
    if test_django_models():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! PostgreSQL is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check your PostgreSQL setup.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 