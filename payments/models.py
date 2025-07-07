from django.db import models
from django.utils import timezone
import uuid

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
