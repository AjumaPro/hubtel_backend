from django.contrib import admin
from .models import PaymentTransaction, OTPVerification

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'reference',
        'amount',
        'currency',
        'payment_method',
        'phone_number',
        'network',
        'status',
        'customer_name',
        'created_at',
    ]
    list_filter = [
        'status',
        'payment_method',
        'network',
        'currency',
        'created_at',
    ]
    search_fields = [
        'reference',
        'customer_name',
        'customer_email',
        'phone_number',
        'hubtel_transaction_id',
    ]
    readonly_fields = [
        'transaction_id',
        'reference',
        'created_at',
        'updated_at',
        'completed_at',
    ]
    ordering = ['-created_at']

@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = [
        'otp_id',
        'transaction',
        'status',
        'attempts',
        'max_attempts',
        'created_at',
        'expires_at',
    ]
    list_filter = [
        'status',
        'created_at',
        'expires_at',
    ]
    search_fields = [
        'otp_id',
        'transaction__reference',
        'transaction__customer_name',
    ]
    readonly_fields = [
        'otp_id',
        'transaction',
        'created_at',
        'expires_at',
        'verified_at',
    ]
    ordering = ['-created_at']
