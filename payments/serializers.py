from rest_framework import serializers
from .models import PaymentTransaction, OTPVerification, User

class PaymentTransactionSerializer(serializers.ModelSerializer):
    """Serializer for PaymentTransaction model"""
    
    class Meta:
        model = PaymentTransaction
        fields = [
            'transaction_id',
            'reference',
            'amount',
            'currency',
            'payment_method',
            'phone_number',
            'network',
            'status',
            'hubtel_transaction_id',
            'customer_name',
            'customer_email',
            'description',
            'created_at',
            'updated_at',
            'completed_at',
        ]
        read_only_fields = [
            'transaction_id',
            'reference',
            'hubtel_transaction_id',
            'created_at',
            'updated_at',
            'completed_at',
        ]

class OTPVerificationSerializer(serializers.ModelSerializer):
    """Serializer for OTPVerification model"""
    
    class Meta:
        model = OTPVerification
        fields = [
            'otp_id',
            'transaction',
            'status',
            'attempts',
            'max_attempts',
            'created_at',
            'expires_at',
            'verified_at',
        ]
        read_only_fields = [
            'otp_id',
            'transaction',
            'status',
            'attempts',
            'max_attempts',
            'created_at',
            'expires_at',
            'verified_at',
        ]

class PaymentInitiationSerializer(serializers.Serializer):
    """Serializer for payment initiation request"""
    
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3, default='GHS')
    phone_number = serializers.CharField(max_length=20)
    network = serializers.ChoiceField(choices=[
        ('MTN', 'MTN'),
        ('Vodafone', 'Vodafone'),
        ('AirtelTigo', 'AirtelTigo'),
    ])
    customer_name = serializers.CharField(max_length=200)
    customer_email = serializers.EmailField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)

class OTPVerificationRequestSerializer(serializers.Serializer):
    """Serializer for OTP verification request"""
    
    transaction_id = serializers.UUIDField()
    otp_code = serializers.CharField(max_length=6, min_length=6)

class PaymentStatusResponseSerializer(serializers.Serializer):
    """Serializer for payment status response"""
    
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = PaymentTransactionSerializer(required=False)
    error = serializers.CharField(required=False)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'email', 'account_id', 'is_verified']

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone', 'email', 'account_id']

class UserPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField() 