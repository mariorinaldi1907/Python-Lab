"""
Date: 2026-07-11
Built a payment processor using the strategy pattern so I can swap payment methods at runtime without changing client code.
"""

"""
Payment processing system using the Strategy pattern.

I wanted a clean way to handle multiple payment methods without cluttering
my checkout logic with if/else chains. Strategy pattern lets me encapsulate
each payment algorithm and swap them dynamically.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime


class PaymentStrategy(ABC):
    """
    Abstract base class for all payment strategies.
    
    Each concrete strategy implements process_payment with its own logic
    for handling transactions (credit card, PayPal, crypto, etc.)
    """
    
    @abstractmethod
    def process_payment(self, amount: float, details: Dict[str, Any]) -> Dict[str, Any]:
        """Process a payment and return transaction details."""
        pass
    
    @abstractmethod
    def validate_details(self, details: Dict[str, Any]) -> bool:
        """Validate payment details before processing."""
        pass


class CreditCardPayment(PaymentStrategy):
    """
    Credit card payment strategy.
    
    In a real app, this would integrate with Stripe or another gateway.
    Here I'm just simulating the validation and processing flow.
    """
    
    def validate_details(self, details: Dict[str, Any]) -> bool:
        """Check that we have card number, expiry, and CVV."""
        required_fields = ['card_number', 'expiry', 'cvv']
        return all(field in details for field in required_fields)
    
    def process_payment(self, amount: float, details: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate credit card processing."""
        if not self.validate_details(details):
            return {'success': False, 'error': 'Invalid card details'}
        
        # Mask card number for display (keeping last 4 digits)
        masked_card = '*' * 12 + details['card_number'][-4:]
        
        return {
            'success': True,
            'transaction_id': f"CC-{datetime.now().timestamp()}",
            'amount': amount,
            'method': 'Credit Card',
            'card_last_four': details['card_number'][-4:],
            'masked_card': masked_card,
            'timestamp': datetime.now().isoformat()
        }


class PayPalPayment(PaymentStrategy):
    """
    PayPal payment strategy.
    
    Would normally use PayPal SDK, but here I'm mocking the OAuth flow
    and payment authorization process.
    """
    
    def validate_details(self, details: Dict[str, Any]) -> bool:
        """Check for email and authorization token."""
        return 'email' in details and 'auth_token' in details
    
    def process_payment(self, amount: float, details: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate PayPal payment processing."""
        if not self.validate_details(details):
            return {'success': False, 'error': 'Invalid PayPal credentials'}
        
        return {
            'success': True,
            'transaction_id': f"PP-{datetime.now().timestamp()}",
            'amount': amount,
            'method': 'PayPal',
            'email': details['email'],
            'timestamp': datetime.now().isoformat()
        }


class CryptoPayment(PaymentStrategy):
    """
    Cryptocurrency payment strategy.
    
    Simulates blockchain transaction confirmation. In reality, you'd wait
    for network confirmations, but here I'm just showing the pattern.
    """
    
    def validate_details(self, details: Dict[str, Any]) -> bool:
        """Check for wallet address and currency type."""
        return 'wallet_address' in details and 'currency' in details
    
    def process_payment(self, amount: float, details: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate crypto payment processing."""
        if not self.validate_details(details):
            return {'success': False, 'error': 'Invalid crypto wallet details'}
        
        # In real life, I'd convert USD to crypto amount based on exchange rate
        return {
            'success': True,
            'transaction_id': f"CRYPTO-{datetime.now().timestamp()}",
            'amount': amount,
            'method': f"{details['currency']} Payment",
            'wallet': details['wallet_address'][:10] + '...',
            'confirmations': 3,  # Mock blockchain confirmations
            'timestamp': datetime.now().isoformat()
        }


class PaymentProcessor:
    """
    Context class that uses a PaymentStrategy.
    
    This is the main interface clients interact with. They set a strategy
    and process payments without knowing the implementation details.
    """
    
    def __init__(self, strategy: PaymentStrategy = None):
        """Initialize with an optional default strategy."""
        self._strategy = strategy
    
    def set_strategy(self, strategy: PaymentStrategy) -> None:
        """
        Switch payment strategy at runtime.
        
        This is the key benefit — I can change payment methods on the fly
        without modifying the processor code.
        """
        self._strategy = strategy
    
    def execute_payment(self, amount: float, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a payment using the current strategy.
        
        Delegates to the strategy's process_payment method. If no strategy
        is set, returns an error.
        """
        if not self._strategy:
            return {'success': False, 'error': 'No payment strategy set'}
        
        print(f"\n{'='*60}")
        print(f"Processing ${amount:.2f} payment...")
        
        result = self._strategy.process_payment(amount, details)
        
        if result['success']:
            print(f"✓ Payment successful via {result['method']}")
            print(f"  Transaction ID: {result['transaction_id']}")
        else:
            print(f"✗ Payment failed: {result.get('error', 'Unknown error')}")
        
        print(f"{'='*60}")
        
        return result


if __name__ == "__main__":
    # Demo showing how the strategy pattern makes payment handling flexible
    
    processor = PaymentProcessor()
    
    # Scenario 1: Customer pays with credit card
    processor.set_strategy(CreditCardPayment())
    processor.execute_payment(
        149.99,
        {
            'card_number': '4532123456789012',
            'expiry': '12/25',
            'cvv': '123'
        }
    )
    
    # Scenario 2: Same processor, different strategy — PayPal
    processor.set_strategy(PayPalPayment())
    processor.execute_payment(
        89.50,
        {
            'email': 'mario@example.com',
            'auth_token': 'mock_oauth_token_xyz'
        }
    )
    
    # Scenario 3: Crypto payment (because why not)
    processor.set_strategy(CryptoPayment())
    processor.execute_payment(
        250.00,
        {
            'wallet_address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
            'currency': 'Bitcoin'
        }
    )
    
    # Scenario 4: Error handling — invalid card details
    processor.set_strategy(CreditCardPayment())
    processor.execute_payment(
        99.99,
        {
            'card_number': '4532123456789012'
            # Missing expiry and CVV on purpose
        }
    )