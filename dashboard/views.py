from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from payments.models import PaymentTransaction, OTPVerification
from kyc.models import KYCSubmission
from datetime import datetime, timedelta
import json

def dashboard_view(request):
    """Main dashboard view"""
    # Get recent data for dashboard
    recent_payments = PaymentTransaction.objects.all().order_by('-created_at')[:10]
    recent_kyc_submissions = KYCSubmission.objects.all().order_by('-submitted_at')[:10]
    
    # Calculate basic stats
    total_payments = PaymentTransaction.objects.count()
    successful_payments = PaymentTransaction.objects.filter(status='completed').count()
    failed_payments = PaymentTransaction.objects.filter(status='failed').count()
    pending_payments = PaymentTransaction.objects.filter(status__in=['pending', 'processing']).count()
    total_kyc = KYCSubmission.objects.count()
    successful_kyc = KYCSubmission.objects.filter(status='SUCCESS').count()
    failed_kyc = KYCSubmission.objects.filter(status='FAILED').count()
    
    context = {
        'recent_payments': recent_payments,
        'recent_kyc_submissions': recent_kyc_submissions,
        'total_payments': total_payments,
        'successful_payments': successful_payments,
        'failed_payments': failed_payments,
        'pending_payments': pending_payments,
        'total_kyc': total_kyc,
        'successful_kyc': successful_kyc,
        'failed_kyc': failed_kyc,
    }
    return render(request, 'dashboard/dashboard.html', context)

@api_view(['GET'])
def dashboard_stats(request):
    """Get dashboard statistics"""
    try:
        # Payment stats
        total_payments = PaymentTransaction.objects.count()
        successful_payments = PaymentTransaction.objects.filter(status='completed').count()
        failed_payments = PaymentTransaction.objects.filter(status='failed').count()
        total_amount = sum(payment.amount for payment in PaymentTransaction.objects.filter(status='completed'))
        
        # KYC stats
        total_kyc = KYCSubmission.objects.count()
        successful_kyc = KYCSubmission.objects.filter(status='SUCCESS').count()
        failed_kyc = KYCSubmission.objects.filter(status='FAILED').count()
        pending_kyc = KYCSubmission.objects.filter(status='PENDING').count()
        
        # Recent activity
        recent_payments = PaymentTransaction.objects.all().order_by('-created_at')[:5]
        recent_kyc = KYCSubmission.objects.all().order_by('-submitted_at')[:5]
        
        return Response({
            'payments': {
                'total': total_payments,
                'successful': successful_payments,
                'failed': failed_payments,
                'total_amount': total_amount,
                'recent': [
                    {
                        'id': p.id,
                        'amount': p.amount,
                        'status': p.status,
                        'created_at': p.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    } for p in recent_payments
                ]
            },
            'kyc': {
                'total': total_kyc,
                'successful': successful_kyc,
                'failed': failed_kyc,
                'pending': pending_kyc,
                'recent': [
                    {
                        'id': k.id,
                        'name': f"{k.data.get('firstName', '')} {k.data.get('lastName', '')}",
                        'status': k.status,
                        'submitted_at': k.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
                    } for k in recent_kyc
                ]
            }
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def transaction_details(request, transaction_id):
    """Get detailed transaction information"""
    try:
        transaction = PaymentTransaction.objects.get(id=transaction_id)
        
        # Get OTP verification data if exists
        otp_data = None
        try:
            otp_verification = OTPVerification.objects.filter(transaction=transaction).first()
            if otp_verification:
                otp_data = {
                    'otp_id': str(otp_verification.otp_id),
                    'status': otp_verification.status,
                    'attempts': otp_verification.attempts,
                    'max_attempts': otp_verification.max_attempts,
                    'created_at': otp_verification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'expires_at': otp_verification.expires_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'verified_at': otp_verification.verified_at.strftime('%Y-%m-%d %H:%M:%S') if otp_verification.verified_at else None,
                    'is_expired': otp_verification.is_expired(),
                }
        except Exception:
            pass
        
        # Calculate time differences
        created_time = transaction.created_at
        updated_time = transaction.updated_at
        completed_time = transaction.completed_at
        
        processing_duration = None
        if completed_time and created_time:
            processing_duration = (completed_time - created_time).total_seconds()
        
        # Format Hubtel response for display
        hubtel_response_formatted = None
        if transaction.hubtel_response:
            hubtel_response_formatted = json.dumps(transaction.hubtel_response, indent=2)
        
        callback_data_formatted = None
        if transaction.callback_data:
            callback_data_formatted = json.dumps(transaction.callback_data, indent=2)
        
        return Response({
            'transaction': {
                'id': transaction.id,
                'transaction_id': str(transaction.transaction_id),
                'reference': transaction.reference,
                'amount': str(transaction.amount),
                'currency': transaction.currency,
                'payment_method': transaction.payment_method,
                'phone_number': transaction.phone_number,
                'network': transaction.network,
                'status': transaction.status,
                'hubtel_transaction_id': transaction.hubtel_transaction_id,
                'customer_name': transaction.customer_name,
                'customer_email': transaction.customer_email,
                'description': transaction.description,
                'created_at': transaction.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': transaction.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'completed_at': transaction.completed_at.strftime('%Y-%m-%d %H:%M:%S') if transaction.completed_at else None,
                'processing_duration_seconds': processing_duration,
                'processing_duration_formatted': f"{processing_duration:.1f} seconds" if processing_duration else None,
            },
            'otp_data': otp_data,
            'hubtel_response': hubtel_response_formatted,
            'callback_data': callback_data_formatted,
            'status_info': {
                'is_completed': transaction.status == 'completed',
                'is_failed': transaction.status == 'failed',
                'is_pending': transaction.status in ['pending', 'processing'],
                'has_hubtel_id': bool(transaction.hubtel_transaction_id),
                'has_otp': bool(otp_data),
            }
        })
    except PaymentTransaction.DoesNotExist:
        return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def analytics_data(request):
    """Get analytics data for charts"""
    try:
        # Get date range from request
        days = int(request.GET.get('days', 30))
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Payment analytics
        payments_data = []
        kyc_data = []
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            next_date = current_date + timedelta(days=1)
            
            # Payments for this date
            daily_payments = PaymentTransaction.objects.filter(
                created_at__gte=current_date,
                created_at__lt=next_date
            )
            payment_count = daily_payments.count()
            payment_amount = sum(p.amount for p in daily_payments if p.status == 'completed')
            
            # KYC for this date
            daily_kyc = KYCSubmission.objects.filter(
                submitted_at__gte=current_date,
                submitted_at__lt=next_date
            )
            kyc_count = daily_kyc.count()
            kyc_success = daily_kyc.filter(status='SUCCESS').count()
            kyc_failed = daily_kyc.filter(status='FAILED').count()
            
            payments_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'count': payment_count,
                'amount': payment_amount
            })
            
            kyc_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'total': kyc_count,
                'success': kyc_success,
                'failed': kyc_failed
            })
        
        # Status distribution
        payment_status_dist = {
            'success': PaymentTransaction.objects.filter(status='completed').count(),
            'failed': PaymentTransaction.objects.filter(status='failed').count(),
            'pending': PaymentTransaction.objects.filter(status='pending').count()
        }
        
        kyc_status_dist = {
            'success': KYCSubmission.objects.filter(status='SUCCESS').count(),
            'failed': KYCSubmission.objects.filter(status='FAILED').count(),
            'pending': KYCSubmission.objects.filter(status='PENDING').count()
        }
        
        return Response({
            'payments_timeline': payments_data,
            'kyc_timeline': kyc_data,
            'payment_status_distribution': payment_status_dist,
            'kyc_status_distribution': kyc_status_dist
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
def settings_view(request):
    """Handle dashboard settings"""
    if request.method == 'GET':
        # Return current settings
        settings = {
            'dashboard_refresh_interval': 30,  # seconds
            'notifications_enabled': True,
            'export_format': 'excel',
            'date_range_default': 30,
            'theme': 'light'
        }
        return Response(settings)
    
    elif request.method == 'POST':
        # Update settings
        try:
            data = request.data
            # Here you would typically save to database or config file
            # For now, just return success
            return Response({'message': 'Settings updated successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def system_info(request):
    """Get system information"""
    try:
        from django.conf import settings
        import platform
        from django.db import connection
        
        # Get database information
        db_engine = settings.DATABASES['default']['ENGINE']
        db_name_raw = settings.DATABASES['default'].get('NAME', 'Unknown')
        # Convert PosixPath to string if needed
        db_name = str(db_name_raw) if db_name_raw else 'Unknown'
        
        # Determine database type and status
        if 'postgresql' in db_engine:
            db_type = 'PostgreSQL'
            try:
                # Test database connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT version();")
                    db_version = cursor.fetchone()[0]
                db_status = 'Connected'
            except Exception as e:
                db_status = f'Error: {str(e)}'
                db_version = 'Unknown'
        elif 'sqlite' in db_engine:
            db_type = 'SQLite'
            try:
                # Test database connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT sqlite_version();")
                    db_version = cursor.fetchone()[0]
                db_status = 'Connected'
            except Exception as e:
                db_status = f'Error: {str(e)}'
                db_version = 'Unknown'
        else:
            db_type = 'Unknown'
            db_status = 'Unknown'
            db_version = 'Unknown'
        
        info = {
            'django_version': '4.2.0',  # You can get this dynamically
            'python_version': platform.python_version(),
            'database_engine': db_engine,
            'database_type': db_type,
            'database_name': db_name,
            'database_version': db_version,
            'database_status': db_status,
            'debug_mode': settings.DEBUG,
            'timezone': settings.TIME_ZONE,
            'static_url': settings.STATIC_URL,
            'media_url': settings.MEDIA_URL
        }
        return Response(info)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 