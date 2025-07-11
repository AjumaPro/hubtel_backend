#!/usr/bin/env python3
"""
Migration script to transition from SQLite to PostgreSQL
This script helps migrate data from SQLite to PostgreSQL
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hubtel_project.settings')
    django.setup()

def check_postgresql_connection():
    """Check if PostgreSQL connection is working"""
    from django.db import connection
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

def backup_sqlite_data():
    """Create a backup of SQLite data"""
    import shutil
    from pathlib import Path
    
    sqlite_file = Path(settings.BASE_DIR) / "db.sqlite3"
    backup_file = Path(settings.BASE_DIR) / "db.sqlite3.backup"
    
    if sqlite_file.exists():
        shutil.copy2(sqlite_file, backup_file)
        print(f"✅ SQLite backup created: {backup_file}")
        return True
    else:
        print("⚠️  No SQLite database found to backup")
        return False

def migrate_to_postgresql():
    """Migrate from SQLite to PostgreSQL"""
    print("🚀 Starting migration to PostgreSQL...")
    
    # Check PostgreSQL connection
    if not check_postgresql_connection():
        print("❌ Cannot proceed without PostgreSQL connection")
        return False
    
    # Create backup
    backup_sqlite_data()
    
    # Run migrations
    print("📦 Running Django migrations...")
    try:
        execute_from_command_line(['manage.py', 'makemigrations'])
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def create_superuser():
    """Create a superuser for the new database"""
    print("👤 Creating superuser...")
    try:
        execute_from_command_line(['manage.py', 'createsuperuser', '--noinput'])
        print("✅ Superuser created successfully!")
        return True
    except Exception as e:
        print(f"⚠️  Superuser creation failed: {e}")
        print("   You can create one manually with: python manage.py createsuperuser")
        return False

def main():
    """Main migration function"""
    print("=" * 50)
    print("🔄 GLICO Capital - SQLite to PostgreSQL Migration")
    print("=" * 50)
    
    # Setup Django
    setup_django()
    
    # Check if we're using PostgreSQL
    db_engine = settings.DATABASES['default']['ENGINE']
    if 'postgresql' not in db_engine:
        print("❌ Database is not configured for PostgreSQL")
        print("   Please set USE_POSTGRESQL=True in your .env file")
        return False
    
    # Perform migration
    if migrate_to_postgresql():
        create_superuser()
        print("\n🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("1. Test your application")
        print("2. Verify all data is accessible")
        print("3. Update your .env file with production settings")
        print("4. Remove the old SQLite backup when confident")
        return True
    else:
        print("\n❌ Migration failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 