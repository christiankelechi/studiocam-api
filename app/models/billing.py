"""Billing, Subscriptions, and Invoices Data Models."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class PlanTier(BaseModel):
    """Subscription tier details."""
    id: str
    name: str
    price_usd: float
    price_ngn: float
    credits_monthly: int
    features: List[str]
    popular: bool = False


class Subscription(BaseModel):
    """User's active subscription status."""
    user_id: str
    plan_id: str
    plan_name: str
    status: str = "active"  # active, past_due, canceled
    current_period_end: datetime
    cancel_at_period_end: bool = False
    payment_method: str = "Paystack Card (ending **** 4242)"


class CheckoutSessionRequest(BaseModel):
    """Create checkout session for subscription upgrade."""
    plan_id: str
    gateway: str = "paystack"  # paystack or stripe
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class CheckoutSessionResponse(BaseModel):
    """Checkout session redirect URL or access code."""
    checkout_url: str
    session_id: str
    reference: str
    success: bool = True
    message: str = "Checkout session created successfully."


class CreditPurchaseRequest(BaseModel):
    """Pay-as-you-go credit pack purchase payload."""
    pack_id: str  # pack_200, pack_500, pack_1500
    credits_count: int
    amount: float
    currency: str = "USD"
    gateway: str = "paystack"


class PaystackVerifyRequest(BaseModel):
    """Verify a Paystack transaction reference."""
    reference: str


class Invoice(BaseModel):
    """Payment invoice record."""
    id: str
    user_id: str
    invoice_number: str
    date: datetime
    amount: float
    currency: str
    status: str = "paid"
    pdf_url: Optional[str] = None

