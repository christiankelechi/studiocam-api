"""Billing & Payments (Paystack & Stripe) API Router."""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_user
from app.models.auth import UserInDB
from app.models.billing import (
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    CreditPurchaseRequest,
    Invoice,
    PaystackVerifyRequest,
    PlanTier,
    Subscription,
)
from app.services.billing_service import billing_service

router = APIRouter(prefix="/billing", tags=["Billing & Payments"])


@router.get("/plans", response_model=List[PlanTier])
def get_plans():
    """Retrieve available subscription pricing tiers."""
    return billing_service.list_plans()


@router.get("/subscription", response_model=Subscription)
def get_user_subscription(user: UserInDB = Depends(get_current_user)):
    """Retrieve user's active subscription status."""
    return billing_service.get_subscription(user.id)


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
def create_checkout_session(payload: CheckoutSessionRequest, user: UserInDB = Depends(get_current_user)):
    """Initialize Paystack or Stripe checkout redirect session."""
    return billing_service.create_checkout_session(user, payload)


@router.post("/buy-credits")
def buy_credits(payload: CreditPurchaseRequest, user: UserInDB = Depends(get_current_user)):
    """Purchase pay-as-you-go credit booster pack."""
    return billing_service.buy_credits(user, payload)


@router.post("/paystack/verify")
def verify_paystack_payment(payload: PaystackVerifyRequest, user: UserInDB = Depends(get_current_user)):
    """Verify Paystack transaction reference."""
    return billing_service.verify_paystack_payment(user, payload.reference)


@router.get("/invoices", response_model=List[Invoice])
def get_invoices(user: UserInDB = Depends(get_current_user)):
    """List billing history and downloadable receipt invoices."""
    return billing_service.list_invoices(user.id)

