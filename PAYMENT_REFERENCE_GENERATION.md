# Payment Reference Generation System

## Overview

The payment system has been updated to automatically generate references for ALL payments, ensuring consistent tracking and management of payment transactions.

## Key Changes Made

### 1. Automatic Reference Generation

- **All payment endpoints now generate references automatically**
- **Consistent reference format**: `PAY-XXXXXXXX` (8-character unique identifier)
- **No manual reference required**: References are generated if not provided
- **Customizable prefix**: Can use different prefixes for different payment types

### 2. Updated Endpoints

#### `POST /api/payments/initiate/` (Modern Payment)
- ✅ **Automatic reference generation**
- ✅ **Full transaction tracking**
- ✅ **OTP support**
- ✅ **Mobile money integration**

#### `POST /api/payments/initiate-legacy/` (Legacy Payment)
- ✅ **Now generates references automatically**
- ✅ **Reference is optional** - will be generated if not provided
- ✅ **Full transaction tracking**
- ✅ **Backward compatible**

#### `POST /api/payments/generate-reference/` (NEW)
- ✅ **Dedicated reference generation endpoint**
- ✅ **Customizable prefix**
- ✅ **Payment type specification**
- ✅ **Transaction record creation**

### 3. Reference Generation Function

```python
def generate_payment_reference(prefix="PAY"):
    """Generate a unique payment reference"""
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"
```

## API Usage Examples

### 1. Generate Reference Only

```bash
POST /api/payments/generate-reference/
Content-Type: application/json

{
    "prefix": "INV",
    "payment_type": "investment",
    "amount": 1000.00,
    "currency": "GHS",
    "customer_name": "John Doe"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Payment reference generated successfully",
    "data": {
        "transaction_id": "uuid-here",
        "reference": "INV-A1B2C3D4",
        "payment_type": "investment",
        "prefix": "INV",
        "amount": "1000.00",
        "currency": "GHS",
        "status": "pending"
    }
}
```

### 2. Legacy Payment (Reference Optional)

```bash
POST /api/payments/initiate-legacy/
Content-Type: application/json

{
    "amount": 500.00,
    "description": "Investment payment",
    "type": "initial"
    // "reference" field is now optional
}
```

**Response:**
```json
{
    "success": true,
    "message": "Payment initiated successfully",
    "data": {
        "transaction_id": "uuid-here",
        "checkout_url": "https://checkout.hubtel.com/...",
        "reference": "PAY-E5F6G7H8",  // Auto-generated
        "amount": "500.00",
        "description": "Investment payment",
        "type": "initial"
    }
}
```

### 3. Modern Payment (Always Generates Reference)

```bash
POST /api/payments/initiate/
Content-Type: application/json

{
    "amount": 750.00,
    "phone_number": "233244123456",
    "network": "MTN",
    "customer_name": "Jane Smith",
    "description": "Portfolio investment"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Payment initiated successfully",
    "data": {
        "transaction_id": "uuid-here",
        "reference": "PAY-I9J0K1L2",  // Auto-generated
        "amount": "750.00",
        "currency": "GHS",
        "status": "processing",
        "hubtel_transaction_id": "hubtel-id-here",
        "requires_otp": true
    }
}
```

## Reference Format

### Standard Format
- **Pattern**: `{PREFIX}-{8_CHAR_HEX}`
- **Example**: `PAY-A1B2C3D4`

### Custom Prefixes
- **Investment**: `INV-A1B2C3D4`
- **Redemption**: `RED-A1B2C3D4`
- **Deposit**: `DEP-A1B2C3D4`
- **Withdrawal**: `WTH-A1B2C3D4`

## Benefits

### 1. **Consistent Tracking**
- All payments have unique references
- No duplicate references possible
- Easy to track and manage

### 2. **Flexible Usage**
- References can be generated independently
- Custom prefixes for different payment types
- Backward compatible with existing systems

### 3. **Better Management**
- Full transaction records for all payments
- Status tracking from creation to completion
- Audit trail for all payment activities

### 4. **Developer Friendly**
- Simple API endpoints
- Clear response formats
- Comprehensive error handling

## Database Schema

### PaymentTransaction Model
```python
class PaymentTransaction(models.Model):
    transaction_id = models.UUIDField(primary_key=True)
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='GHS')
    payment_method = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default='pending')
    # ... other fields
```

## Testing

### 1. Generate Reference
```bash
curl -X POST http://localhost:8000/api/payments/generate-reference/ \
  -H "Content-Type: application/json" \
  -d '{"prefix": "TEST", "payment_type": "test"}'
```

### 2. Initiate Payment (Legacy)
```bash
curl -X POST http://localhost:8000/api/payments/initiate-legacy/ \
  -H "Content-Type: application/json" \
  -d '{"amount": 100, "description": "Test payment"}'
```

### 3. Check Transaction
```bash
curl -X GET http://localhost:8000/api/payments/check-transaction/PAY-A1B2C3D4/
```

## Web Interface

Visit `http://localhost:8000/api/payments/` to access the interactive API explorer with forms for testing all endpoints including the new reference generation.

## Migration Notes

- **No breaking changes**: Existing code continues to work
- **References are now optional**: Legacy endpoints work without reference
- **Auto-generation**: References are created automatically if not provided
- **Full backward compatibility**: All existing integrations continue to work

## Security Considerations

- References are cryptographically secure (UUID-based)
- No sequential patterns that could be guessed
- Unique constraint prevents duplicates
- Audit trail for all reference generation 