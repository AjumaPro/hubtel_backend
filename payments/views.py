from django.shortcuts import render
from rest_framework import status, views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
import uuid
import logging
from django.http import HttpResponse
import io
import pandas as pd
from reportlab.pdfgen import canvas

from .models import PaymentTransaction, OTPVerification
from .hubtel_service import HubtelService
from .serializers import PaymentTransactionSerializer, OTPVerificationSerializer

logger = logging.getLogger(__name__)

def generate_payment_reference(prefix="PAY"):
    """Generate a unique payment reference"""
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"

@api_view(['POST'])
@permission_classes([AllowAny])
def initiate_payment(request):
    """Initiate a payment transaction"""
    try:
        # Validate request data
        required_fields = ['amount', 'phone_number', 'network', 'customer_name']
        for field in required_fields:
            if field not in request.data:
                return Response({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate unique reference
        reference = generate_payment_reference()
        
        # Create transaction record
        transaction_data = {
            'reference': reference,
            'amount': request.data['amount'],
            'currency': request.data.get('currency', 'GHS'),
            'payment_method': 'mobile_money',
            'phone_number': request.data['phone_number'],
            'network': request.data['network'],
            'customer_name': request.data['customer_name'],
            'customer_email': request.data.get('customer_email', ''),
            'description': request.data.get('description', 'Payment for services'),
        }
        
        transaction = PaymentTransaction.objects.create(**transaction_data)
        
        # Initialize Hubtel service
        hubtel_service = HubtelService()
        
        # Prepare data for Hubtel API
        hubtel_data = {
            'amount': transaction.amount,
            'currency': transaction.currency,
            'reference': transaction.reference,
            'phone_number': transaction.phone_number,
            'network': transaction.network,
            'customer_name': transaction.customer_name,
            'customer_email': transaction.customer_email,
            'description': transaction.description,
        }
        
        # Call Hubtel API
        hubtel_response = hubtel_service.initiate_payment(hubtel_data)
        
        # Update transaction with Hubtel response
        transaction.hubtel_response = hubtel_response
        transaction.hubtel_transaction_id = hubtel_response.get('Data', {}).get('TransactionId')
        transaction.status = 'processing'
        transaction.save()
        
        # Create OTP verification record
        otp_data = hubtel_response.get('Data', {}).get('OtpData', {})
        if otp_data:
            otp_verification = OTPVerification.objects.create(
                transaction=transaction,
                otp_code=otp_data.get('OtpCode', ''),
                expires_at=timezone.now() + timedelta(minutes=10)
            )
        
        return Response({
            'success': True,
            'message': 'Payment initiated successfully',
            'data': {
                'transaction_id': str(transaction.transaction_id),
                'reference': transaction.reference,
                'amount': str(transaction.amount),
                'currency': transaction.currency,
                'status': transaction.status,
                'hubtel_transaction_id': transaction.hubtel_transaction_id,
                'requires_otp': bool(otp_data),
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Payment initiation failed: {str(e)}")
        return Response({
            'success': False,
            'message': 'Payment initiation failed',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def initiate_payment_legacy(request):
    """Initiate payment using legacy PHP-style method - matches PHP initiatePayment"""
    try:
        # Validate request data
        required_fields = ['amount', 'description']
        for field in required_fields:
            if field not in request.data:
                return Response({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        amount = request.data['amount']
        description = request.data['description']
        
        # Generate reference automatically if not provided
        if 'reference' in request.data:
            reference = request.data['reference']
        else:
            reference = generate_payment_reference()
        
        payment_type = request.data.get('type', 'initial')
        
        # Create transaction record for tracking
        transaction_data = {
            'reference': reference,
            'amount': amount,
            'currency': request.data.get('currency', 'GHS'),
            'payment_method': 'mobile_money',
            'customer_name': request.data.get('customer_name', 'Customer'),
            'customer_email': request.data.get('customer_email', ''),
            'description': description,
            'phone_number': request.data.get('phone_number', ''),
            'network': request.data.get('network', ''),
        }
        
        # Create transaction record
        transaction = PaymentTransaction.objects.create(**transaction_data)
        
        # Initialize Hubtel service
        hubtel_service = HubtelService()
        
        # Call Hubtel API using legacy method
        checkout_url = hubtel_service.initiate_payment(amount, description, reference, payment_type)
        
        if checkout_url and not checkout_url.startswith('Error'):
            # Update transaction with Hubtel response
            transaction.hubtel_response = {'checkout_url': checkout_url}
            transaction.status = 'processing'
            transaction.save()
            
            return Response({
                'success': True,
                'message': 'Payment initiated successfully',
                'data': {
                    'transaction_id': str(transaction.transaction_id),
                    'checkout_url': checkout_url,
                    'reference': reference,
                    'amount': amount,
                    'description': description,
                    'type': payment_type
                }
            }, status=status.HTTP_200_OK)
        else:
            # Mark transaction as failed
            transaction.status = 'failed'
            transaction.hubtel_response = {'error': checkout_url}
            transaction.save()
            
            return Response({
                'success': False,
                'message': 'Payment initiation failed',
                'error': checkout_url
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Legacy payment initiation failed: {str(e)}")
        return Response({
            'success': False,
            'message': 'Payment initiation failed',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def store_callback(request):
    """Store payment callback - matches PHP storeCallback method"""
    try:
        callback_data = request.data
        payment_type = request.data.get('type', 'initial')
        
        # Initialize Hubtel service
        hubtel_service = HubtelService()
        
        # Process callback
        success = hubtel_service.store_callback(callback_data, payment_type)
        
        if success:
            return Response({
                'success': True,
                'message': 'Callback processed successfully'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Callback processing failed'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Callback processing failed: {str(e)}")
        return Response({
            'success': False,
            'message': 'Callback processing failed',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def check_transaction(request, reference):
    """Check transaction status - matches PHP checkTrnnsaction method"""
    try:
        payment_type = request.GET.get('type', 'initial')
        
        # Initialize Hubtel service
        hubtel_service = HubtelService()
        
        # Check transaction status
        success = hubtel_service.check_transaction(reference, payment_type)
        
        if success:
            return Response({
                'success': True,
                'message': 'Transaction status checked successfully',
                'data': {
                    'reference': reference,
                    'type': payment_type,
                    'status': 'checked'
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Transaction not found or check failed',
                'data': {
                    'reference': reference,
                    'type': payment_type,
                    'status': 'not_found'
                }
            }, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        logger.error(f"Transaction check failed: {str(e)}")
        return Response({
            'success': False,
            'message': 'Transaction check failed',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def send_sms(request):
    """Send SMS - matches PHP sendSms method"""
    try:
        # Validate request data
        if 'phone_number' not in request.data or 'message' not in request.data:
            return Response({
                'success': False,
                'message': 'Missing phone_number or message'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        phone_number = request.data['phone_number']
        message = request.data['message']
        
        # Initialize Hubtel service
        hubtel_service = HubtelService()
        
        # Send SMS
        success = hubtel_service.send_sms(phone_number, message)
        
        if success:
            return Response({
                'success': True,
                'message': 'SMS sent successfully',
                'data': {
                    'phone_number': phone_number,
                    'message': message
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'SMS sending failed'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"SMS sending failed: {str(e)}")
        return Response({
            'success': False,
            'message': 'SMS sending failed',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """Verify OTP for payment transaction"""
    try:
        # Validate request data
        if 'transaction_id' not in request.data or 'otp_code' not in request.data:
            return Response({
                'success': False,
                'message': 'Missing transaction_id or otp_code'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        transaction_id = request.data['transaction_id']
        otp_code = request.data['otp_code']
        
        # Get transaction
        try:
            transaction = PaymentTransaction.objects.get(transaction_id=transaction_id)
        except PaymentTransaction.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Transaction not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get OTP verification
        try:
            otp_verification = OTPVerification.objects.get(
                transaction=transaction,
                status='pending'
            )
        except OTPVerification.DoesNotExist:
            return Response({
                'success': False,
                'message': 'OTP verification not found or already processed'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if OTP is expired
        if otp_verification.is_expired():
            otp_verification.status = 'expired'
            otp_verification.save()
            return Response({
                'success': False,
                'message': 'OTP has expired'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if max attempts exceeded
        if otp_verification.attempts >= otp_verification.max_attempts:
            return Response({
                'success': False,
                'message': 'Maximum OTP attempts exceeded'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Initialize Hubtel service
        hubtel_service = HubtelService()
        
        # Verify OTP with Hubtel
        hubtel_response = hubtel_service.verify_otp(
            transaction.hubtel_transaction_id,
            otp_code
        )
        
        # Update OTP verification
        otp_verification.hubtel_response = hubtel_response
        otp_verification.save()
        
        # Check verification result
        if hubtel_response.get('Status') == 'Success':
            otp_verification.mark_verified()
            transaction.mark_completed()
            
            return Response({
                'success': True,
                'message': 'OTP verified successfully',
                'data': {
                    'transaction_id': str(transaction.transaction_id),
                    'reference': transaction.reference,
                    'status': transaction.status,
                    'completed_at': transaction.completed_at.isoformat() if transaction.completed_at else None,
                }
            }, status=status.HTTP_200_OK)
        else:
            otp_verification.increment_attempts()
            return Response({
                'success': False,
                'message': 'Invalid OTP code',
                'attempts_remaining': otp_verification.max_attempts - otp_verification.attempts
            }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"OTP verification failed: {str(e)}")
        return Response({
            'success': False,
            'message': 'OTP verification failed',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def payment_status(request, transaction_id):
    """Get payment transaction status"""
    try:
        # Get transaction
        try:
            transaction = PaymentTransaction.objects.get(transaction_id=transaction_id)
        except PaymentTransaction.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Transaction not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Initialize Hubtel service
        hubtel_service = HubtelService()
        
        # Verify with Hubtel if transaction is still processing
        if transaction.status in ['pending', 'processing']:
            try:
                hubtel_response = hubtel_service.verify_payment(transaction.hubtel_transaction_id)
                transaction.hubtel_response = hubtel_response
                transaction.save()
                
                # Update status based on Hubtel response
                hubtel_status = hubtel_response.get('Data', {}).get('Status')
                if hubtel_status == 'Success':
                    transaction.mark_completed()
                elif hubtel_status == 'Failed':
                    transaction.mark_failed()
                    
            except Exception as e:
                logger.warning(f"Could not verify with Hubtel: {str(e)}")
        
        serializer = PaymentTransactionSerializer(transaction)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Payment status check failed: {str(e)}")
        return Response({
            'success': False,
            'message': 'Payment status check failed',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def payment_callback(request):
    """Handle payment callback from Hubtel"""
    try:
        callback_data = request.data
        logger.info(f"Received callback: {callback_data}")
        
        # Initialize Hubtel service
        hubtel_service = HubtelService()
        
        # Process callback data
        processed_data = hubtel_service.process_callback(callback_data)
        
        # Find transaction
        reference = processed_data.get('reference')
        if reference:
            try:
                transaction = PaymentTransaction.objects.get(reference=reference)
                transaction.callback_data = callback_data
                transaction.save()
                
                # Update status based on callback
                status = processed_data.get('status')
                if status == 'Success':
                    transaction.mark_completed()
                elif status == 'Failed':
                    transaction.mark_failed()
                    
            except PaymentTransaction.DoesNotExist:
                logger.warning(f"Transaction not found for reference: {reference}")
        
        return Response({
            'success': True,
            'message': 'Callback processed successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Callback processing failed: {str(e)}")
        return Response({
            'success': False,
            'message': 'Callback processing failed',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def generate_reference(request):
    """Generate a payment reference for any payment type"""
    try:
        # Get optional prefix from request
        prefix = request.data.get('prefix', 'PAY')
        payment_type = request.data.get('payment_type', 'general')
        
        # Generate reference
        reference = generate_payment_reference(prefix)
        
        # Create a basic transaction record for tracking
        transaction_data = {
            'reference': reference,
            'amount': request.data.get('amount', 0.00),
            'currency': request.data.get('currency', 'GHS'),
            'payment_method': request.data.get('payment_method', 'mobile_money'),
            'customer_name': request.data.get('customer_name', 'Customer'),
            'customer_email': request.data.get('customer_email', ''),
            'description': request.data.get('description', f'{payment_type} payment'),
            'phone_number': request.data.get('phone_number', ''),
            'network': request.data.get('network', ''),
            'status': 'pending'
        }
        
        # Create transaction record
        transaction = PaymentTransaction.objects.create(**transaction_data)
        
        return Response({
            'success': True,
            'message': 'Payment reference generated successfully',
            'data': {
                'transaction_id': str(transaction.transaction_id),
                'reference': reference,
                'payment_type': payment_type,
                'prefix': prefix,
                'amount': str(transaction.amount),
                'currency': transaction.currency,
                'status': transaction.status
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Reference generation failed: {str(e)}")
        return Response({
            'success': False,
            'message': 'Reference generation failed',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    html = """
    <!DOCTYPE html>
    <html lang='en'>
    <head>
      <meta charset='UTF-8'>
      <meta name='viewport' content='width=device-width, initial-scale=1.0'>
      <title>Payments API Root</title>
      <link href='https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css' rel='stylesheet'>
      <style>
        .fade-in { animation: fadeIn 0.7s; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px);} to { opacity: 1; transform: none; } }
        .endpoint-badge { @apply inline-block px-2 py-1 rounded text-xs font-semibold bg-blue-100 text-blue-800 mr-2; }
        .endpoint-method { @apply font-bold px-2 py-1 rounded text-xs; }
      </style>
    </head>
    <body class='bg-gradient-to-br from-blue-50 to-purple-100 min-h-screen flex items-center justify-center'>
      <div class='w-full max-w-3xl mx-auto p-4'>
        <div class='bg-white/90 shadow-2xl rounded-2xl p-8 fade-in'>
          <div class='flex items-center gap-4 mb-6'>
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="24" cy="24" r="24" fill="#1a237e"/><text x="50%" y="55%" text-anchor="middle" fill="#fff" font-size="22" font-family="Segoe UI,Arial,sans-serif" dy=".3em">GC</text></svg>
            <div>
              <h1 class='text-3xl font-extrabold text-blue-900 tracking-tight'>Payments API</h1>
              <p class='text-gray-500 text-sm'>Glico Capital &mdash; Hubtel Integration</p>
            </div>
          </div>
          <div class='mb-8'>
            <h2 class='text-xl font-semibold text-blue-800 mb-2'>Endpoints</h2>
            <div class='grid grid-cols-1 sm:grid-cols-2 gap-3'>
              <div class='bg-gradient-to-r from-blue-100 to-blue-50 rounded-lg p-4 flex flex-col gap-1'>
                <span class='endpoint-method bg-blue-600 text-white'>POST</span>
                <span class='endpoint-badge'>/api/payments/initiate-legacy/</span>
                <span class='text-xs text-gray-500'>Initiate payment (legacy)</span>
              </div>
              <div class='bg-gradient-to-r from-purple-100 to-purple-50 rounded-lg p-4 flex flex-col gap-1'>
                <span class='endpoint-method bg-purple-600 text-white'>POST</span>
                <span class='endpoint-badge'>/api/payments/initiate/</span>
                <span class='text-xs text-gray-500'>Initiate payment (modern)</span>
              </div>
              <div class='bg-gradient-to-r from-green-100 to-green-50 rounded-lg p-4 flex flex-col gap-1'>
                <span class='endpoint-method bg-green-600 text-white'>POST</span>
                <span class='endpoint-badge'>/api/payments/verify-otp/</span>
                <span class='text-xs text-gray-500'>Verify OTP</span>
              </div>
              <div class='bg-gradient-to-r from-yellow-100 to-yellow-50 rounded-lg p-4 flex flex-col gap-1'>
                <span class='endpoint-method bg-yellow-600 text-white'>GET</span>
                <span class='endpoint-badge'>/api/payments/status/&lt;transaction_id&gt;/</span>
                <span class='text-xs text-gray-500'>Check payment status</span>
              </div>
              <div class='bg-gradient-to-r from-pink-100 to-pink-50 rounded-lg p-4 flex flex-col gap-1'>
                <span class='endpoint-method bg-pink-600 text-white'>POST</span>
                <span class='endpoint-badge'>/api/payments/store-callback/</span>
                <span class='text-xs text-gray-500'>Store payment callback</span>
              </div>
              <div class='bg-gradient-to-r from-indigo-100 to-indigo-50 rounded-lg p-4 flex flex-col gap-1'>
                <span class='endpoint-method bg-indigo-600 text-white'>GET</span>
                <span class='endpoint-badge'>/api/payments/check-transaction/&lt;reference&gt;/</span>
                <span class='text-xs text-gray-500'>Check transaction by reference</span>
              </div>
              <div class='bg-gradient-to-r from-gray-100 to-gray-50 rounded-lg p-4 flex flex-col gap-1'>
                <span class='endpoint-method bg-gray-600 text-white'>POST</span>
                <span class='endpoint-badge'>/api/payments/send-sms/</span>
                <span class='text-xs text-gray-500'>Send SMS</span>
              </div>
              <div class='bg-gradient-to-r from-teal-100 to-teal-50 rounded-lg p-4 flex flex-col gap-1'>
                <span class='endpoint-method bg-teal-600 text-white'>POST</span>
                <span class='endpoint-badge'>/api/payments/generate-reference/</span>
                <span class='text-xs text-gray-500'>Generate payment reference</span>
              </div>
            </div>
          </div>
          <div class='mb-10'>
            <h2 class='text-xl font-semibold text-blue-800 mb-2'>API Explorer</h2>
            <div class='grid grid-cols-1 md:grid-cols-2 gap-6'>
              <form id='initiateForm' class='space-y-2 bg-blue-50 rounded-lg p-4 shadow-sm' onsubmit='return apiCall("initiate")'>
                <div class='font-bold text-blue-900 mb-1'>Initiate Payment</div>
                <input name='amount' placeholder='Amount' required type='number' step='0.01' class='w-full border px-2 py-1 rounded focus:ring-2 focus:ring-blue-300' />
                <input name='description' placeholder='Description' required class='w-full border px-2 py-1 rounded focus:ring-2 focus:ring-blue-300' />
                <input name='reference' placeholder='Reference' required class='w-full border px-2 py-1 rounded focus:ring-2 focus:ring-blue-300' />
                <input name='type' value='initial' class='w-full border px-2 py-1 rounded focus:ring-2 focus:ring-blue-300' />
                <button type='submit' class='w-full bg-blue-700 text-white px-4 py-2 rounded hover:bg-blue-800 transition'>Send</button>
              </form>
              <form id='checkForm' class='space-y-2 bg-green-50 rounded-lg p-4 shadow-sm' onsubmit='return apiCall("check")'>
                <div class='font-bold text-green-900 mb-1'>Check Transaction</div>
                <input name='reference' placeholder='Reference' required class='w-full border px-2 py-1 rounded focus:ring-2 focus:ring-green-300' />
                <button type='submit' class='w-full bg-green-700 text-white px-4 py-2 rounded hover:bg-green-800 transition'>Check</button>
              </form>
              <form id='smsForm' class='space-y-2 bg-purple-50 rounded-lg p-4 shadow-sm' onsubmit='return apiCall("sms")'>
                <div class='font-bold text-purple-900 mb-1'>Send SMS</div>
                <div class='flex flex-col md:flex-row gap-2'>
                  <input name='phone_number' placeholder='Phone Number' required class='flex-1 border px-2 py-1 rounded focus:ring-2 focus:ring-purple-300' />
                  <input name='message' placeholder='Message' required class='flex-1 border px-2 py-1 rounded focus:ring-2 focus:ring-purple-300' />
                  <button type='submit' class='bg-purple-700 text-white px-4 py-2 rounded hover:bg-purple-800 transition'>Send</button>
                </div>
              </form>
              <form id='referenceForm' class='space-y-2 bg-teal-50 rounded-lg p-4 shadow-sm' onsubmit='return apiCall("reference")'>
                <div class='font-bold text-teal-900 mb-1'>Generate Reference</div>
                <input name='prefix' placeholder='Prefix (optional)' class='w-full border px-2 py-1 rounded focus:ring-2 focus:ring-teal-300' />
                <input name='payment_type' placeholder='Payment Type (optional)' class='w-full border px-2 py-1 rounded focus:ring-2 focus:ring-teal-300' />
                <input name='amount' placeholder='Amount (optional)' type='number' step='0.01' class='w-full border px-2 py-1 rounded focus:ring-2 focus:ring-teal-300' />
                <button type='submit' class='w-full bg-teal-700 text-white px-4 py-2 rounded hover:bg-teal-800 transition'>Generate</button>
              </form>
            </div>
            <div class='mt-6'>
              <div class='flex items-center gap-2 mb-1'>
                <span class='font-semibold text-gray-700'>API Response</span>
                <button onclick='copyResult()' class='ml-2 px-2 py-1 text-xs bg-gray-200 rounded hover:bg-gray-300 transition'>Copy</button>
              </div>
              <pre id='apiResult' class='bg-gray-900 text-green-200 p-4 rounded-lg text-xs overflow-x-auto min-h-[60px] transition-all duration-300'></pre>
            </div>
          </div>
          <div class='mt-8 text-sm text-gray-400 text-center'>
            &copy; 2024 Glico Capital. Powered by Django & Hubtel API.
          </div>
        </div>
      </div>
      <script>
      function apiCall(type) {
        let url, data = {}, method = 'POST';
        if(type==='initiate') {
          url = '/api/payments/initiate-legacy/';
          let f = document.getElementById('initiateForm');
          data = {amount: f.amount.value, description: f.description.value, reference: f.reference.value, type: f.type.value};
        } else if(type==='check') {
          url = '/api/payments/check-transaction/' + document.getElementById('checkForm').reference.value + '/';
          method = 'GET';
        } else if(type==='sms') {
          url = '/api/payments/send-sms/';
          let f = document.getElementById('smsForm');
          data = {phone_number: f.phone_number.value, message: f.message.value};
        } else if(type==='reference') {
          url = '/api/payments/generate-reference/';
          let f = document.getElementById('referenceForm');
          data = {
            prefix: f.prefix.value || 'PAY',
            payment_type: f.payment_type.value || 'general',
            amount: f.amount.value || 0.00
          };
        }
        document.getElementById('apiResult').textContent = 'Loading...';
        fetch(url, {
          method: method,
          headers: {'Content-Type': 'application/json'},
          body: method==='POST' ? JSON.stringify(data) : undefined
        }).then(r=>r.json()).then(j=>{
          document.getElementById('apiResult').textContent = JSON.stringify(j, null, 2);
        }).catch(e=>{
          document.getElementById('apiResult').textContent = 'Error: ' + e;
        });
        return false;
      }
      function copyResult() {
        const el = document.getElementById('apiResult');
        if (el.textContent) {
          navigator.clipboard.writeText(el.textContent);
        }
      }
      </script>
    </body>
    </html>
    """
    return HttpResponse(html)

@api_view(['GET'])
def transaction_detail(request, transaction_id):
    """Get detailed transaction data"""
    try:
        transaction = PaymentTransaction.objects.get(id=transaction_id)
        return Response({
            'id': transaction.id,
            'reference': transaction.reference,
            'customer_name': transaction.customer_name,
            'amount': transaction.amount,
            'currency': transaction.currency,
            'status': transaction.status,
            'created_at': transaction.created_at,
            'updated_at': transaction.updated_at,
        })
    except PaymentTransaction.DoesNotExist:
        return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)

class PaymentExportExcelView(views.APIView):
    permission_classes = [AllowAny]  # Changed for testing

    def get(self, request):
        try:
            transactions = PaymentTransaction.objects.all()
            if not transactions.exists():
                return Response({'message': 'No payment transactions found'}, status=status.HTTP_404_NOT_FOUND)
            
            records = []
            for tx in transactions:
                record = {
                    'id': tx.id,
                    'reference': tx.reference,
                    'customer_name': tx.customer_name,
                    'amount': tx.amount,
                    'currency': tx.currency,
                    'status': tx.status,
                    'created_at': tx.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': tx.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                }
                records.append(record)
            
            df = pd.DataFrame(records)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Payment Transactions')
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="payment_transactions.xlsx"'
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentExportPDFView(views.APIView):
    permission_classes = [AllowAny]  # Changed for testing

    def get(self, request):
        try:
            transactions = PaymentTransaction.objects.all()
            if not transactions.exists():
                return Response({'message': 'No payment transactions found'}, status=status.HTTP_404_NOT_FOUND)
            
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer)
            y = 800
            page = 1
            
            # Add title
            p.drawString(50, y, "GLICO Capital - Payment Transactions Report")
            y -= 30
            
            for tx in transactions:
                # Add page number
                p.drawString(50, y, f"Page {page}")
                y -= 20
                
                # Add transaction header
                p.drawString(50, y, f"Transaction ID: {tx.id} | Reference: {tx.reference}")
                y -= 20
                
                # Add transaction details
                details = [
                    f"Customer: {tx.customer_name}",
                    f"Amount: {tx.currency} {tx.amount}",
                    f"Status: {tx.status}",
                    f"Created: {tx.created_at}",
                    f"Updated: {tx.updated_at}",
                ]
                
                for detail in details:
                    if y < 100:  # Start new page
                        p.showPage()
                        page += 1
                        y = 800
                        p.drawString(50, y, f"Page {page}")
                        y -= 20
                    
                    p.drawString(70, y, detail)
                    y -= 15
                
                y -= 20  # Space between transactions
                
                if y < 100:  # Start new page
                    p.showPage()
                    page += 1
                    y = 800
            
            p.save()
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="payment_transactions.pdf"'
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
