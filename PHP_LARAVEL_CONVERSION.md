# PHP Laravel to Django Conversion Guide

This document explains how the PHP Laravel `PaymentService` has been converted to Django Python for Hubtel payment integration.

## 🔄 **Conversion Overview**

The original PHP Laravel `PaymentService` class has been converted to Django with equivalent functionality:

### **Original PHP Methods → Django Equivalents**

| PHP Method | Django View | Endpoint | Description |
|------------|-------------|----------|-------------|
| `initiatePayment()` | `initiate_payment_legacy()` | `POST /api/payments/initiate-legacy/` | Start payment with checkout URL |
| `storeCallback()` | `store_callback()` | `POST /api/payments/store-callback/` | Process payment callbacks |
| `checkTrnnsaction()` | `check_transaction()` | `GET /api/payments/check-transaction/{reference}/` | Check transaction status |
| `sendSms()` | `send_sms()` | `POST /api/payments/send-sms/` | Send SMS notifications |

## 🛠️ **Environment Variables**

Update your `.env` file with these PHP Laravel-style variables:

```env
# PHP Laravel-style Hubtel Configuration
HUBTEL_APPID=your_hubtel_app_id_here
HUBTEL_API_KEY=your_hubtel_api_key_here
HUBTEL_MERCHANT_ACCOUNT=2020274
HUBTEL_CALLBACK=https://admin.glicocapital.com/callback
HUBTEL_RETURN_URL=https://glicocapital.com/?return
HUBTEL_CANCELLATION=https://glicocapital.com/?cancel
```

## 📡 **API Endpoints**

### 1. **Initiate Payment (Legacy PHP Style)**

**Endpoint:** `POST /api/payments/initiate-legacy/`

**Request:**
```json
{
    "amount": "100.00",
    "description": "Payment for services",
    "reference": "PAY-ABC12345",
    "type": "initial"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Payment initiated successfully",
    "data": {
        "checkout_url": "https://checkout.hubtel.com/...",
        "reference": "PAY-ABC12345",
        "amount": "100.00",
        "description": "Payment for services",
        "type": "initial"
    }
}
```

### 2. **Store Callback**

**Endpoint:** `POST /api/payments/store-callback/`

**Request:**
```json
{
    "ResponseCode": "0000",
    "Status": "Success",
    "Data": {
        "ClientReference": "PAY-ABC12345",
        "Status": "Success"
    },
    "type": "initial"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Callback processed successfully"
}
```

### 3. **Check Transaction Status**

**Endpoint:** `GET /api/payments/check-transaction/{reference}/?type=initial`

**Response:**
```json
{
    "success": true,
    "message": "Transaction status checked successfully",
    "data": {
        "reference": "PAY-ABC12345",
        "type": "initial",
        "status": "checked"
    }
}
```

### 4. **Send SMS**

**Endpoint:** `POST /api/payments/send-sms/`

**Request:**
```json
{
    "phone_number": "233244123456",
    "message": "Your payment has been processed successfully"
}
```

**Response:**
```json
{
    "success": true,
    "message": "SMS sent successfully",
    "data": {
        "phone_number": "233244123456",
        "message": "Your payment has been processed successfully"
    }
}
```

## 🔧 **Service Class Methods**

### **HubtelService Class**

The `HubtelService` class in `payments/hubtel_service.py` contains all the converted methods:

```python
class HubtelService:
    def __init__(self):
        # Initialize with environment variables
        self.client_id = config('HUBTEL_APPID')
        self.client_secret = config('HUBTEL_API_KEY')
        self.merchant_account_number = config('HUBTEL_MERCHANT_ACCOUNT')
        # ... other configurations
    
    def initiate_payment(self, amount, description, reference, payment_type='initial'):
        """Matches PHP initiatePayment() method"""
        # Implementation details...
    
    def store_callback(self, callback_data, payment_type="initial"):
        """Matches PHP storeCallback() method"""
        # Implementation details...
    
    def check_transaction(self, reference, payment_type):
        """Matches PHP checkTrnnsaction() method"""
        # Implementation details...
    
    def send_sms(self, phone_number, message):
        """Matches PHP sendSms() method"""
        # Implementation details...
```

## 🔄 **Migration from PHP to Django**

### **Step 1: Update Environment Variables**

Replace your Laravel `.env` variables:

```env
# Old Laravel
HUBTEL_APPID=your_app_id
HUBTEL_API_KEY=your_api_key

# New Django
HUBTEL_APPID=your_app_id
HUBTEL_API_KEY=your_api_key
HUBTEL_MERCHANT_ACCOUNT=2020274
```

### **Step 2: Update API Calls**

**Old PHP Laravel:**
```php
$paymentService = new PaymentService($client);
$checkoutUrl = $paymentService->initiatePayment($id, $amount, $description, $reference, $type);
```

**New Django Python:**
```python
import requests

response = requests.post('http://localhost:8000/api/payments/initiate-legacy/', {
    'amount': amount,
    'description': description,
    'reference': reference,
    'type': type
})

checkout_url = response.json()['data']['checkout_url']
```

### **Step 3: Update Callback Handling**

**Old PHP Laravel:**
```php
$paymentService->storeCallback($data, $type);
```

**New Django Python:**
```python
response = requests.post('http://localhost:8000/api/payments/store-callback/', {
    'ResponseCode': data['ResponseCode'],
    'Status': data['Status'],
    'Data': data['Data'],
    'type': type
})
```

## 🗄️ **Database Models**

The Django models provide equivalent functionality to Laravel models:

### **PaymentTransaction Model**
- Stores payment transaction details
- Tracks status and callback data
- Links to Hubtel transaction IDs

### **OTPVerification Model**
- Manages OTP verification process
- Tracks attempts and expiration

## 🔐 **Security Considerations**

1. **Environment Variables**: All sensitive data stored in `.env`
2. **API Authentication**: Basic Auth with Hubtel credentials
3. **Input Validation**: Comprehensive validation on all endpoints
4. **Error Handling**: Robust error handling and logging

## 🚀 **Deployment**

### **Development:**
```bash
cd hubtel_backend
python manage.py runserver
```

### **Production:**
```bash
# Set DEBUG=False in .env
# Configure production database
# Set up HTTPS
python manage.py runserver 0.0.0.0:8000
```

## 📊 **Monitoring**

### **Django Admin:**
- Access at `/admin/`
- Monitor all transactions
- View callback data
- Track payment statuses

### **Logging:**
- All API interactions logged
- Error tracking and debugging
- Payment status monitoring

## 🔧 **Testing**

### **Test Payment Initiation:**
```bash
curl -X POST http://localhost:8000/api/payments/initiate-legacy/ \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "100.00",
    "description": "Test payment",
    "reference": "TEST-123",
    "type": "initial"
  }'
```

### **Test Callback Processing:**
```bash
curl -X POST http://localhost:8000/api/payments/store-callback/ \
  -H "Content-Type: application/json" \
  -d '{
    "ResponseCode": "0000",
    "Status": "Success",
    "Data": {
      "ClientReference": "TEST-123",
      "Status": "Success"
    },
    "type": "initial"
  }'
```

## 📞 **Support**

For issues with:
- **Hubtel API**: Contact Hubtel support
- **Django Backend**: Check Django documentation
- **Conversion**: Review this documentation

The Django backend now provides full compatibility with the original PHP Laravel `PaymentService` functionality! 