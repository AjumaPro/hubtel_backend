#!/usr/bin/env python3
"""
Script to create test payment transactions for testing export functionality
"""

import os
import sys
import django
from django.utils import timezone
from datetime import timedelta
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hubtel_project.settings')
django.setup()

from payments.models import PaymentTransaction, OTPVerification
from kyc.models import KYCSubmission

def create_test_kyc_data():
    """Create test KYC submissions with proper timezone handling"""
    
    # Check if KYC data already exists
    if KYCSubmission.objects.exists():
        print("Test KYC data already exists!")
        return
    
    # Sample KYC data
    test_kyc_data = [
        {
            'data': {
                'firstName': 'John',
                'lastName': 'Doe',
                'email': 'john.doe@example.com',
                'phone': '233244123456',
                'dateOfBirth': '1990-05-15',
                'nationality': 'Ghanaian',
                'idType': 'Ghana Card',
                'idNumber': 'GHA-123456789-0'
            },
            'status': 'SUCCESS',
            'notes': 'All documents verified successfully'
        },
        {
            'data': {
                'firstName': 'Jane',
                'lastName': 'Smith',
                'email': 'jane.smith@example.com',
                'phone': '233244789012',
                'dateOfBirth': '1985-08-22',
                'nationality': 'Ghanaian',
                'idType': 'Passport',
                'idNumber': 'G12345678'
            },
            'status': 'PENDING',
            'notes': 'Awaiting document verification'
        },
        {
            'data': {
                'firstName': 'Bob',
                'lastName': 'Johnson',
                'email': 'bob.johnson@example.com',
                'phone': '233244345678',
                'dateOfBirth': '1992-12-10',
                'nationality': 'Ghanaian',
                'idType': 'Driver License',
                'idNumber': 'DL-123456789'
            },
            'status': 'FAILED',
            'notes': 'Invalid ID document provided'
        }
    ]
    
    # Create KYC submissions with different timestamps
    for i, kyc_data in enumerate(test_kyc_data):
        # Create timezone-aware timestamps
        submitted_at = timezone.now() - timedelta(days=i, hours=i*2)
        
        submission = KYCSubmission.objects.create(
            user=None,  # Anonymous submission
            data=kyc_data['data'],
            status=kyc_data['status'],
            notes=kyc_data['notes'],
            submitted_at=submitted_at
        )
        
        print(f"Created KYC submission: {submission.id} - {kyc_data['data']['firstName']} {kyc_data['data']['lastName']}")
    
    print(f"\n✅ Created {len(test_kyc_data)} test KYC submissions!")

def create_test_transactions():
    """Create test payment transactions with OTP and Hubtel data"""
    
    # Check if transactions already exist
    if PaymentTransaction.objects.exists():
        print("Test transactions already exist!")
        return
    
    # Sample Hubtel response data
    hubtel_responses = [
        {
            "status": "success",
            "message": "Transaction processed successfully",
            "transaction_id": "HUBTEL-001-2024",
            "amount": "100.00",
            "currency": "GHS",
            "customer_name": "John Doe",
            "phone_number": "233244123456",
            "network": "MTN",
            "timestamp": "2024-01-15T10:30:00Z"
        },
        {
            "status": "pending",
            "message": "Transaction pending OTP verification",
            "transaction_id": "HUBTEL-002-2024",
            "amount": "250.50",
            "currency": "GHS",
            "customer_name": "Jane Smith",
            "phone_number": "233244789012",
            "network": "VODAFONE",
            "timestamp": "2024-01-15T11:45:00Z"
        },
        {
            "status": "failed",
            "message": "Insufficient funds",
            "transaction_id": "HUBTEL-003-2024",
            "amount": "75.25",
            "currency": "GHS",
            "customer_name": "Bob Johnson",
            "phone_number": "233244345678",
            "network": "AIRTEL",
            "error_code": "INSUFFICIENT_FUNDS",
            "timestamp": "2024-01-15T12:15:00Z"
        }
    ]
    
    # Sample callback data
    callback_data = [
        {
            "callback_type": "payment_success",
            "transaction_id": "HUBTEL-001-2024",
            "status": "completed",
            "amount": "100.00",
            "currency": "GHS",
            "customer_phone": "233244123456",
            "network": "MTN",
            "timestamp": "2024-01-15T10:32:15Z"
        },
        {
            "callback_type": "otp_required",
            "transaction_id": "HUBTEL-002-2024",
            "status": "pending",
            "message": "OTP sent to customer",
            "timestamp": "2024-01-15T11:46:30Z"
        },
        {
            "callback_type": "payment_failed",
            "transaction_id": "HUBTEL-003-2024",
            "status": "failed",
            "error_message": "Insufficient funds in customer account",
            "error_code": "INSUFFICIENT_FUNDS",
            "timestamp": "2024-01-15T12:16:45Z"
        }
    ]
    
    # Create test transactions
    test_transactions = [
        {
            'reference': 'PAY-TEST001',
            'amount': 100.00,
            'currency': 'GHS',
            'payment_method': 'mobile_money',
            'customer_name': 'John Doe',
            'customer_email': 'john@example.com',
            'phone_number': '233244123456',
            'network': 'MTN',
            'description': 'Test payment 1',
            'status': 'completed',
            'hubtel_transaction_id': 'HUBTEL-001-2024',
            'hubtel_response': hubtel_responses[0],
            'callback_data': callback_data[0],
            'completed_at': timezone.now() - timedelta(days=1, hours=2),
        },
        {
            'reference': 'PAY-TEST002',
            'amount': 250.50,
            'currency': 'GHS',
            'payment_method': 'mobile_money',
            'customer_name': 'Jane Smith',
            'customer_email': 'jane@example.com',
            'phone_number': '233244789012',
            'network': 'VODAFONE',
            'description': 'Test payment 2',
            'status': 'processing',
            'hubtel_transaction_id': 'HUBTEL-002-2024',
            'hubtel_response': hubtel_responses[1],
            'callback_data': callback_data[1],
        },
        {
            'reference': 'PAY-TEST003',
            'amount': 75.25,
            'currency': 'GHS',
            'payment_method': 'mobile_money',
            'customer_name': 'Bob Johnson',
            'customer_email': 'bob@example.com',
            'phone_number': '233244345678',
            'network': 'AIRTEL',
            'description': 'Test payment 3',
            'status': 'failed',
            'hubtel_transaction_id': 'HUBTEL-003-2024',
            'hubtel_response': hubtel_responses[2],
            'callback_data': callback_data[2],
        },
        {
            'reference': 'PAY-TEST004',
            'amount': 500.00,
            'currency': 'GHS',
            'payment_method': 'mobile_money',
            'customer_name': 'Alice Brown',
            'customer_email': 'alice@example.com',
            'phone_number': '233244901234',
            'network': 'MTN',
            'description': 'Test payment 4',
            'status': 'completed',
            'completed_at': timezone.now() - timedelta(days=2, hours=1),
        },
        {
            'reference': 'PAY-TEST005',
            'amount': 150.75,
            'currency': 'GHS',
            'payment_method': 'mobile_money',
            'customer_name': 'Charlie Wilson',
            'customer_email': 'charlie@example.com',
            'phone_number': '233244567890',
            'network': 'VODAFONE',
            'description': 'Test payment 5',
            'status': 'pending',
        }
    ]
    
    # Create transactions with different timestamps
    for i, transaction_data in enumerate(test_transactions):
        # Create transaction with different timestamps using timezone-aware datetimes
        created_at = timezone.now() - timedelta(days=i, hours=i)
        updated_at = created_at + timedelta(minutes=30)
        
        # Remove completed_at from transaction_data if it exists and create transaction
        completed_at = transaction_data.pop('completed_at', None)
        
        transaction = PaymentTransaction.objects.create(
            **transaction_data,
            created_at=created_at,
            updated_at=updated_at
        )
        
        # Set completed_at if it exists (ensure it's timezone-aware)
        if completed_at:
            # Ensure completed_at is timezone-aware
            if timezone.is_naive(completed_at):
                completed_at = timezone.make_aware(completed_at)
            transaction.completed_at = completed_at
            transaction.save()
        
        # Create OTP verification for some transactions
        if i < 3:  # First 3 transactions get OTP data
            otp_created_at = created_at + timedelta(minutes=5)
            otp_expires_at = otp_created_at + timedelta(minutes=10)
            
            otp_verification = OTPVerification.objects.create(
                transaction=transaction,
                otp_code='123456',
                status='verified' if i == 0 else 'pending' if i == 1 else 'failed',
                attempts=i,
                max_attempts=3,
                created_at=otp_created_at,
                expires_at=otp_expires_at,
                verified_at=otp_created_at + timedelta(minutes=2) if i == 0 else None,
                hubtel_response={
                    "otp_status": "sent" if i < 2 else "failed",
                    "message": "OTP sent successfully" if i < 2 else "OTP verification failed",
                    "timestamp": otp_created_at.isoformat()
                }
            )
            print(f"Created OTP verification for transaction: {transaction.reference}")
        
        print(f"Created transaction: {transaction.reference} - {transaction.customer_name}")
    
    print(f"\n✅ Created {len(test_transactions)} test transactions with enhanced data!")
    print("You can now test the enhanced transaction details view.")

if __name__ == '__main__':
    create_test_kyc_data()
    create_test_transactions() 