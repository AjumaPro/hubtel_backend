# Hubtel Payment Backend

A Django REST API backend for processing mobile money payments through Hubtel API.

## 🚀 Features

- **Payment Processing**: Initiate mobile money payments via Hubtel API
- **OTP Verification**: Handle OTP verification for secure transactions
- **Transaction Tracking**: Complete transaction lifecycle management
- **Callback Handling**: Process payment callbacks from Hubtel
- **Admin Interface**: Django admin for transaction monitoring
- **RESTful API**: Clean REST API endpoints for frontend integration

## 📋 Prerequisites

- Python 3.8+
- Django 4.2+
- Hubtel API credentials

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hubtel_backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Hubtel credentials
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Hubtel API Configuration
HUBTEL_CLIENT_ID=your_hubtel_client_id_here
HUBTEL_CLIENT_SECRET=your_hubtel_client_secret_here
HUBTEL_API_BASE_URL=https://api.hubtel.com/v2

# Django Configuration
DEBUG=True
SECRET_KEY=your_django_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Payment Configuration
PAYMENT_CALLBACK_URL=https://your-domain.com/api/payments/callback/
PAYMENT_RETURN_URL=https://your-domain.com/api/payments/return/
```

### Hubtel API Setup

1. Register for a Hubtel account at [https://hubtel.com](https://hubtel.com)
2. Get your Client ID and Client Secret from the Hubtel dashboard
3. Configure your callback URLs in the Hubtel dashboard
4. Update the `.env` file with your credentials

## 📡 API Endpoints

### 1. Initiate Payment
```http
POST /api/payments/initiate/
Content-Type: application/json

{
    "amount": "100.00",
    "currency": "GHS",
    "phone_number": "233244123456",
    "network": "MTN",
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "description": "Payment for services"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Payment initiated successfully",
    "data": {
        "transaction_id": "uuid-here",
        "reference": "PAY-ABC12345",
        "amount": "100.00",
        "currency": "GHS",
        "status": "processing",
        "hubtel_transaction_id": "hubtel-tx-id",
        "requires_otp": true
    }
}
```

### 2. Verify OTP
```http
POST /api/payments/verify-otp/
Content-Type: application/json

{
    "transaction_id": "uuid-here",
    "otp_code": "123456"
}
```

**Response:**
```json
{
    "success": true,
    "message": "OTP verified successfully",
    "data": {
        "transaction_id": "uuid-here",
        "reference": "PAY-ABC12345",
        "status": "completed",
        "completed_at": "2024-01-01T12:00:00Z"
    }
}
```

### 3. Check Payment Status
```http
GET /api/payments/status/{transaction_id}/
```

**Response:**
```json
{
    "success": true,
    "data": {
        "transaction_id": "uuid-here",
        "reference": "PAY-ABC12345",
        "amount": "100.00",
        "currency": "GHS",
        "status": "completed",
        "customer_name": "John Doe",
        "created_at": "2024-01-01T12:00:00Z",
        "completed_at": "2024-01-01T12:05:00Z"
    }
}
```

### 4. Payment Callback
```http
POST /api/payments/callback/
Content-Type: application/json

{
    "Data": {
        "TransactionId": "hubtel-tx-id",
        "Status": "Success",
        "Reference": "PAY-ABC12345"
    }
}
```

## 🗄️ Database Models

### PaymentTransaction
- Stores payment transaction details
- Tracks transaction status and lifecycle
- Links to Hubtel transaction IDs

### OTPVerification
- Manages OTP verification process
- Tracks OTP attempts and expiration
- Links to payment transactions

## 🔐 Security Considerations

1. **API Keys**: Store Hubtel credentials in environment variables
2. **HTTPS**: Use HTTPS in production for all API calls
3. **CORS**: Configure CORS properly for your frontend domain
4. **Validation**: All input data is validated before processing
5. **Logging**: Comprehensive logging for debugging and monitoring

## 🚀 Deployment

### Production Setup

1. **Set DEBUG=False** in production
2. **Use a production database** (PostgreSQL recommended)
3. **Configure proper CORS settings**
4. **Set up HTTPS certificates**
5. **Use environment variables for all secrets**

### Example Production Settings

```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']
CORS_ALLOWED_ORIGINS = ['https://your-frontend-domain.com']

# Use PostgreSQL in production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📊 Monitoring

### Django Admin
Access the admin interface at `/admin/` to monitor:
- Payment transactions
- OTP verifications
- Transaction statuses
- Customer information

### Logging
The application logs all API interactions and errors. Check logs for:
- Payment initiation attempts
- OTP verification attempts
- Hubtel API responses
- Error messages

## 🐛 Troubleshooting

### Common Issues

1. **Invalid Hubtel Credentials**
   - Verify your Client ID and Client Secret
   - Check if your Hubtel account is active

2. **CORS Errors**
   - Ensure your frontend domain is in CORS_ALLOWED_ORIGINS
   - Check if CORS middleware is properly configured

3. **Payment Failures**
   - Check Hubtel API documentation for error codes
   - Verify phone number format (should include country code)
   - Ensure network provider is supported

4. **OTP Issues**
   - Check if OTP has expired (10 minutes)
   - Verify OTP code format (6 digits)
   - Check maximum attempts (3 attempts allowed)

## 📞 Support

For issues related to:
- **Hubtel API**: Contact Hubtel support
- **Django Backend**: Check Django documentation
- **Integration**: Review API documentation above

## 📄 License

This project is licensed under the MIT License. 