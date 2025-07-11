# PostgreSQL Migration Guide

This guide will help you migrate the GLICO Capital application from SQLite to PostgreSQL.

## 🎯 Overview

The application has been updated to support both SQLite (development) and PostgreSQL (production). This guide covers the complete migration process.

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+ installed and running
- Access to PostgreSQL server
- Virtual environment activated

## 🚀 Quick Migration (Automated)

### Step 1: Run Setup Script
```bash
cd hubtel_backend
./setup_postgres.sh
```

### Step 2: Configure Environment
Edit the `.env` file created by the setup script:
```bash
# Database Configuration
USE_POSTGRESQL=True
DB_NAME=glico_capital
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
```

### Step 3: Create Database
```bash
createdb glico_capital
```

### Step 4: Run Migration
```bash
python migrate_to_postgres.py
```

### Step 5: Test Setup
```bash
python test_postgres.py
```

## 🔧 Manual Migration

### Step 1: Install PostgreSQL Dependencies
```bash
pip install psycopg2-binary==2.9.9
```

### Step 2: Install PostgreSQL Server

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**CentOS/RHEL:**
```bash
sudo yum install postgresql postgresql-server
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Step 3: Create Database and User
```bash
# Connect to PostgreSQL as superuser
sudo -u postgres psql

# Create database and user
CREATE DATABASE glico_capital;
CREATE USER glico_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE glico_capital TO glico_user;
\q
```

### Step 4: Configure Environment
Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

Edit `.env` with your PostgreSQL credentials:
```bash
# Database Configuration
USE_POSTGRESQL=True
DB_NAME=glico_capital
DB_USER=glico_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
DB_SSLMODE=disable
```

### Step 5: Backup SQLite Data
```bash
# The migration script will automatically create a backup
# Manual backup if needed:
cp db.sqlite3 db.sqlite3.backup
```

### Step 6: Run Django Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 7: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 8: Test Application
```bash
python manage.py runserver
```

## 🔍 Verification Steps

### 1. Check Database Connection
```bash
python test_postgres.py
```

### 2. Verify Dashboard
- Access the dashboard at `http://localhost:8000/dashboard/`
- Check that database status shows "PostgreSQL: Connected"

### 3. Test API Endpoints
```bash
# Test payment initiation
curl -X POST http://localhost:8000/api/payments/initiate/ \
  -H "Content-Type: application/json" \
  -d '{"amount": "100.00", "description": "Test payment"}'

# Test KYC submission
curl -X POST http://localhost:8000/api/kyc/submit/ \
  -H "Content-Type: application/json" \
  -d '{"firstName": "John", "lastName": "Doe"}'
```

### 4. Check Django Admin
- Access admin at `http://localhost:8000/admin/`
- Verify all models are accessible
- Check that data is being saved correctly

## 🛠️ Troubleshooting

### Common Issues

#### 1. Connection Refused
```
Error: connection to server at "localhost" (127.0.0.1), port 5432 failed
```
**Solution:**
- Ensure PostgreSQL is running: `sudo systemctl status postgresql`
- Start PostgreSQL: `sudo systemctl start postgresql`
- Check port: `netstat -an | grep 5432`

#### 2. Authentication Failed
```
Error: FATAL: password authentication failed for user "postgres"
```
**Solution:**
- Reset PostgreSQL password: `sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'new_password';"`
- Update `.env` file with correct password

#### 3. Database Does Not Exist
```
Error: database "glico_capital" does not exist
```
**Solution:**
- Create database: `createdb glico_capital`
- Or connect as superuser: `sudo -u postgres createdb glico_capital`

#### 4. Permission Denied
```
Error: permission denied for database "glico_capital"
```
**Solution:**
- Grant permissions: `GRANT ALL PRIVILEGES ON DATABASE glico_capital TO your_user;`
- Check user roles: `\du` in psql

#### 5. Migration Errors
```
Error: relation "django_migrations" does not exist
```
**Solution:**
- Run migrations: `python manage.py migrate`
- Check migration status: `python manage.py showmigrations`

### Performance Optimization

#### 1. Connection Pooling
For production, consider using connection pooling:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
        'OPTIONS': {
            'sslmode': config('DB_SSLMODE', default='disable'),
        },
        'CONN_MAX_AGE': 600,  # 10 minutes
    }
}
```

#### 2. Index Optimization
PostgreSQL automatically creates indexes for primary keys and unique constraints. Consider additional indexes for frequently queried fields.

## 🔄 Rollback Plan

If you need to rollback to SQLite:

### 1. Update Environment
```bash
# In .env file
USE_POSTGRESQL=False
```

### 2. Restore SQLite Backup
```bash
cp db.sqlite3.backup db.sqlite3
```

### 3. Restart Application
```bash
python manage.py runserver
```

## 📊 Monitoring

### Database Monitoring
- Use PostgreSQL's built-in monitoring: `pg_stat_activity`
- Monitor slow queries: `pg_stat_statements`
- Check connection count: `SELECT count(*) FROM pg_stat_activity;`

### Application Monitoring
- Check Django logs for database errors
- Monitor dashboard for database status
- Use Django Debug Toolbar for query analysis

## 🔐 Security Considerations

### 1. Database Security
- Use strong passwords for database users
- Limit database access to application servers only
- Enable SSL in production: `sslmode=require`

### 2. Environment Variables
- Never commit `.env` files to version control
- Use different credentials for development and production
- Rotate passwords regularly

### 3. Backup Strategy
- Set up automated PostgreSQL backups
- Test backup restoration procedures
- Store backups securely

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review PostgreSQL logs: `tail -f /var/log/postgresql/postgresql-*.log`
3. Check Django logs for detailed error messages
4. Verify environment variables are set correctly
5. Test database connection manually: `psql -h localhost -U your_user -d glico_capital`

## 🎉 Success Checklist

- [ ] PostgreSQL server is running
- [ ] Database connection test passes
- [ ] Django migrations completed successfully
- [ ] Application starts without errors
- [ ] Dashboard shows "PostgreSQL: Connected"
- [ ] API endpoints are working
- [ ] Admin interface is accessible
- [ ] Data is being saved correctly
- [ ] Performance is acceptable
- [ ] Backup strategy is in place

Congratulations! Your application is now running on PostgreSQL. 🎉 