import requests
import json
import base64
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging
from decouple import config

logger = logging.getLogger(__name__)

class HubtelService:
    """Service class to handle Hubtel API interactions - Converted from PHP Laravel"""
    
    def __init__(self):
        self.client_id = config('HUBTEL_APPID', default=settings.HUBTEL_CONFIG.get('CLIENT_ID'))
        self.client_secret = config('HUBTEL_API_KEY', default=settings.HUBTEL_CONFIG.get('CLIENT_SECRET'))
        self.merchant_account_number = config('HUBTEL_MERCHANT_ACCOUNT', default='2020274')
        self.base_url = 'https://payproxyapi.hubtel.com'
        self.status_url = 'https://api-txnstatus.hubtel.com'
        self.callback_url = config('HUBTEL_CALLBACK', default=settings.HUBTEL_CONFIG.get('CALLBACK_URL'))
        self.return_url = config('HUBTEL_RETURN_URL', default=settings.HUBTEL_CONFIG.get('RETURN_URL'))
        self.cancellation_url = config('HUBTEL_CANCELLATION', default='https://glicocapital.com/?cancel')
    
    def _get_auth_header(self):
        """Generate Basic Auth header for Hubtel API"""
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"
    
    def _make_request(self, url, method='GET', data=None):
        """Make HTTP request to Hubtel API"""
        headers = {
            'Accept': 'application/json',
            'Authorization': self._get_auth_header(),
            'Content-Type': 'application/json',
        }
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Hubtel API request failed: {str(e)}")
            raise
    
    def initiate_payment(self, amount, description, reference, payment_type='initial'):
        """Initiate a payment transaction with Hubtel - matches PHP initiatePayment method"""
        try:
            # Prepare payment data matching PHP structure
            payment_data = {
                'totalAmount': float(amount),
                'description': description,
                'callbackUrl': f"{self.callback_url}/{payment_type}",
                'returnUrl': self.return_url,
                'merchantAccountNumber': self.merchant_account_number,
                'cancellationUrl': self.cancellation_url,
                'clientReference': reference
            }
            
            logger.info(f"Initiating payment: {payment_data}")
            
            # Make API call to Hubtel
            url = f"{self.base_url}/items/initiate"
            response_data = self._make_request(url, method='POST', data=payment_data)
            
            logger.info(f"Hubtel payment response: {response_data}")
            
            # Return checkout URL if successful
            if response_data.get('status') == 'Success':
                return response_data.get('data', {}).get('checkoutDirectUrl')
            else:
                return f"{response_data.get('status')}: {response_data.get('responseCode')}"
                
        except Exception as e:
            logger.error(f"Payment initiation failed: {str(e)}")
            raise
    
    def store_callback(self, callback_data, payment_type="initial"):
        """Process payment callback from Hubtel - matches PHP storeCallback method"""
        try:
            logger.info(f"Processing callback: {callback_data}")
            
            # Check if payment was successful
            if (callback_data.get('ResponseCode') == '0000' and 
                callback_data.get('Status') == 'Success'):
                
                # Extract client reference
                client_reference = callback_data.get('Data', {}).get('ClientReference')
                
                # Update transaction status
                from .models import PaymentTransaction
                try:
                    transaction = PaymentTransaction.objects.get(reference=client_reference)
                    transaction.status = callback_data.get('Data', {}).get('Status', 'completed')
                    transaction.callback_data = callback_data
                    transaction.save()
                    
                    logger.info(f"Payment callback processed successfully for reference: {client_reference}")
                    return True
                    
                except PaymentTransaction.DoesNotExist:
                    logger.warning(f"Transaction not found for reference: {client_reference}")
                    return False
            else:
                logger.error(f"Payment callback failed: {callback_data}")
                return False
                
        except Exception as e:
            logger.error(f"Callback processing failed: {str(e)}")
            return False
    
    def check_transaction(self, reference, payment_type):
        """Check transaction status - matches PHP checkTrnnsaction method"""
        try:
            # URL decode the reference
            import urllib.parse
            reference = urllib.parse.unquote(reference)
            
            # Build status check URL
            url = f"{self.status_url}/transactions/{self.merchant_account_number}/status?clientReference={reference}"
            
            logger.info(f"Checking transaction status for reference: {reference}")
            
            # Make API call
            response_data = self._make_request(url, method='GET')
            
            # Process response
            if response_data:
                logger.info('Transaction status check passed')
                
                # Update transaction in database
                from .models import PaymentTransaction
                try:
                    transaction = PaymentTransaction.objects.get(reference=reference)
                    
                    if response_data.get('data', {}).get('status'):
                        transaction.status = response_data.get('data', {}).get('status')
                        transaction.hubtel_response = response_data
                        transaction.save()
                        
                        logger.info(f"Transaction status updated: {transaction.status}")
                        return True
                    else:
                        logger.error('No status data in response')
                        return False
                        
                except PaymentTransaction.DoesNotExist:
                    logger.warning(f"Transaction not found for reference: {reference}")
                    return False
            else:
                logger.error(f"No response data for reference: {reference}")
                return False
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.info(f'Payment record not found for reference: {reference}')
                
                # Update transaction status to 'Not Found'
                from .models import PaymentTransaction
                try:
                    transaction = PaymentTransaction.objects.get(reference=reference)
                    transaction.status = 'Not Found'
                    transaction.hubtel_response = {'error': 'Record not found'}
                    transaction.save()
                except PaymentTransaction.DoesNotExist:
                    pass
                    
                return False
            else:
                logger.error(f'HTTP Error: {e.getMessage()}')
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f'Request Exception: {str(e)}')
            return False
    
    def send_sms(self, phone_number, message):
        """Send SMS using Arkesel API - matches PHP sendSms method"""
        try:
            sms_data = {
                'action': 'send-sms',
                'api_key': 'OjJFRHJiVlBwTWFvZ2JwYmo=',
                'to': phone_number,
                'from': 'GLICO GFIF',
                'sms': message,
            }
            
            response = requests.get('https://sms.arkesel.com/sms/api', params=sms_data)
            
            if response.status_code == 200:
                logger.info(f"SMS sent successfully to {phone_number}")
                return True
            else:
                logger.error(f"SMS sending failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"SMS sending failed: {str(e)}")
            return False
    
    # Additional methods for mobile money payments (from original Django service)
    def initiate_mobile_money_payment(self, transaction_data):
        """Initiate a mobile money payment transaction with Hubtel"""
        try:
            # Prepare payment data for mobile money
            payment_data = {
                "amount": float(transaction_data['amount']),
                "currency": transaction_data.get('currency', 'GHS'),
                "description": transaction_data.get('description', 'Payment for services'),
                "callback_url": self.callback_url,
                "return_url": self.return_url,
                "reference": transaction_data['reference'],
                "customer_name": transaction_data['customer_name'],
                "customer_email": transaction_data.get('customer_email', ''),
                "customer_phone": transaction_data['phone_number'],
                "channel": self._get_channel_code(transaction_data['network']),
            }
            
            logger.info(f"Initiating mobile money payment: {payment_data}")
            
            # Make API call
            response = self._make_request('pos/onlinecheckout', method='POST', data=payment_data)
            
            logger.info(f"Hubtel mobile money response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Mobile money payment initiation failed: {str(e)}")
            raise
    
    def verify_otp(self, transaction_id, otp_code):
        """Verify OTP with Hubtel"""
        try:
            otp_data = {
                "transaction_id": transaction_id,
                "otp": otp_code
            }
            
            logger.info(f"Verifying OTP: {otp_data}")
            
            response = self._make_request('pos/onlinecheckout/verify', method='POST', data=otp_data)
            
            logger.info(f"OTP verification response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"OTP verification failed: {str(e)}")
            raise
    
    def _get_channel_code(self, network):
        """Get Hubtel channel code for mobile money network"""
        network_mapping = {
            'MTN': 'mtn-gh',
            'Vodafone': 'vodafone-gh',
            'AirtelTigo': 'airtel-gh',
        }
        return network_mapping.get(network, 'mtn-gh') 