"""
PayFast Payment Gateway Integration for iPhone Store
"""

import hashlib
import urllib.parse
from django.conf import settings
from django.urls import reverse


class PayFastConfig:
    """PayFast configuration settings"""
    
    # PayFast URLs
    SANDBOX_URL = 'https://sandbox.payfast.co.za/eng/process'
    LIVE_URL = 'https://www.payfast.co.za/eng/process'
    
    SANDBOX_VALIDATE_URL = 'https://sandbox.payfast.co.za/eng/query/validate'
    LIVE_VALIDATE_URL = 'https://www.payfast.co.za/eng/query/validate'
    
    @classmethod
    def get_process_url(cls):
        """Get the PayFast process URL based on mode"""
        # Set PAYFAST_MODE = 'live' in production settings
        mode = getattr(settings, 'PAYFAST_MODE', 'sandbox')
        return cls.LIVE_URL if mode == 'live' else cls.SANDBOX_URL
    
    @classmethod
    def get_merchant_id(cls):
        """Get merchant ID from settings"""
        return getattr(settings, 'PAYFAST_MERCHANT_ID', '')
    
    @classmethod
    def get_merchant_key(cls):
        """Get merchant key from settings"""
        return getattr(settings, 'PAYFAST_MERCHANT_KEY', '')
    
    @classmethod
    def get_passphrase(cls):
        """Get passphrase from settings (optional but recommended)"""
        return getattr(settings, 'PAYFAST_PASSPHRASE', '')


class PayFastPayment:
    """PayFast payment handler"""
    
    def __init__(self, order, request):
        self.order = order
        self.request = request
        self.config = PayFastConfig()
    
    def get_callback_urls(self):
        """Generate return, cancel and notify URLs"""
        # Build absolute URIs
        return_url = self.request.build_absolute_uri(
            reverse('store:payment_success')
        )
        cancel_url = self.request.build_absolute_uri(
            reverse('store:payment_cancel')
        )
        notify_url = self.request.build_absolute_uri(
            reverse('store:payment_notify')
        )
        
        return {
            'return_url': return_url,
            'cancel_url': cancel_url,
            'notify_url': notify_url,
        }
    
    def get_payment_data(self):
        """Generate PayFast payment form data"""
        order = self.order
        
        # Ensure amount has exactly 2 decimal places
        amount = f"{float(order.total_amount):.2f}"
        
        # Build payment data
        data = {
            'merchant_id': self.config.get_merchant_id(),
            'merchant_key': self.config.get_merchant_key(),
            'return_url': self.get_callback_urls()['return_url'],
            'cancel_url': self.get_callback_urls()['cancel_url'],
            'notify_url': self.get_callback_urls()['notify_url'],
            'name_first': order.user.first_name if order.user and order.user.first_name else 'Customer',
            'name_last': order.user.last_name if order.user and order.user.last_name else '',
            'email_address': order.email,
            'm_payment_id': str(order.id),  # Our internal order ID
            'amount': amount,
            'item_name': f'Order {order.order_number} - iPhone Store',
            'item_description': f'Purchase of iPhone products - Order #{order.order_number}',
            'custom_int1': str(order.get_item_count()) if hasattr(order, 'get_item_count') else '1',
            'custom_str1': order.order_number,
        }
        
        # Remove empty values
        data = {k: v for k, v in data.items() if v}
        
        return data
    
    def generate_signature(self, data):
        """Generate PayFast signature for data verification"""
        # Sort parameters alphabetically
        sorted_params = sorted(data.items())
        
        # Build parameter string
        param_string = '&'.join([f'{k}={urllib.parse.quote(str(v), safe="")}' 
                                 for k, v in sorted_params])
        
        # Add passphrase if configured
        passphrase = self.config.get_passphrase()
        if passphrase:
            param_string += f'&passphrase={urllib.parse.quote(passphrase, safe="")}'
        
        # Generate MD5 hash
        signature = hashlib.md5(param_string.encode()).hexdigest()
        
        return signature
    
    def get_payment_form(self):
        """Get complete payment form data with signature"""
        data = self.get_payment_data()
        data['signature'] = self.generate_signature(data)
        
        return {
            'action_url': self.config.get_process_url(),
            'fields': data
        }


def verify_payfast_signature(data, signature):
    """
    Verify PayFast signature for ITN callbacks
    
    Args:
        data: Dictionary of POST data from PayFast (excluding 'signature' key)
        signature: The signature provided by PayFast
    
    Returns:
        bool: True if signature is valid
    """
    config = PayFastConfig()
    
    # Create ordered parameter string
    sorted_params = sorted(data.items())
    param_string = '&'.join([f'{k}={urllib.parse.quote(str(v), safe="")}' 
                             for k, v in sorted_params])
    
    # Add passphrase if configured
    passphrase = config.get_passphrase()
    if passphrase:
        param_string += f'&passphrase={urllib.parse.quote(passphrase, safe="")}'
    
    # Generate signature
    calculated_signature = hashlib.md5(param_string.encode()).hexdigest()
    
    return calculated_signature == signature


def validate_payfast_ip(ip_address):
    """
    Validate that the request comes from a valid PayFast IP address
    
    Note: In production, you should verify the IP is from PayFast's servers
    """
    # PayFast IP ranges (these should be updated from PayFast documentation)
    valid_ips = [
        '196.40.96.0/20',  # PayFast production range
        '197.97.80.0/20',  # PayFast sandbox range
    ]
    
    # For now, return True to allow testing
    # In production, implement proper IP validation
    return True
