from django.db import models
from django.utils import timezone
import uuid
from django.contrib.auth.hashers import make_password, check_password

class PaymentTransaction(models.Model):
    """Model to store payment transaction details"""
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('mobile_money', 'Mobile Money'),
        ('card', 'Card'),
        ('bank', 'Bank Transfer'),
    ]
    
    # Basic transaction info
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='GHS')
    
    # Payment details
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    network = models.CharField(max_length=20, blank=True, null=True)  # MTN, Vodafone, AirtelTigo
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    hubtel_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Customer info
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Hubtel response data
    hubtel_response = models.JSONField(blank=True, null=True)
    callback_data = models.JSONField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'
        indexes = [
            models.Index(fields=['reference']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['hubtel_transaction_id']),
        ]
    
    def __str__(self):
        return f"{self.reference} - {self.amount} {self.currency}"
    
    def mark_completed(self):
        """Mark transaction as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def mark_failed(self):
        """Mark transaction as failed"""
        self.status = 'failed'
        self.save()

class OTPVerification(models.Model):
    """Model to store OTP verification details"""
    
    OTP_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('expired', 'Expired'),
        ('failed', 'Failed'),
    ]
    
    # OTP details
    otp_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    transaction = models.ForeignKey(PaymentTransaction, on_delete=models.CASCADE, related_name='otp_verifications')
    otp_code = models.CharField(max_length=6)
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=OTP_STATUS_CHOICES, default='pending')
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=3)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(blank=True, null=True)
    
    # Hubtel response
    hubtel_response = models.JSONField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'OTP Verification'
        verbose_name_plural = 'OTP Verifications'
        indexes = [
            models.Index(fields=['transaction']),
            models.Index(fields=['status']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"OTP for {self.transaction.reference}"
    
    def is_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.expires_at
    
    def increment_attempts(self):
        """Increment failed attempts"""
        self.attempts += 1
        if self.attempts >= self.max_attempts:
            self.status = 'failed'
        self.save()
    
    def mark_verified(self):
        """Mark OTP as verified"""
        self.status = 'verified'
        self.verified_at = timezone.now()
        self.save()

class User(models.Model):
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    account_id = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)  # hashed
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.phone} ({self.email})"
    
    class Meta:
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['email']),
            models.Index(fields=['account_id']),
        ]
