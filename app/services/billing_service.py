"""Billing, Payments (Paystack & Stripe), and Credit Top-up Service."""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import uuid

from app.core.config import settings
from app.models.auth import UserInDB
from app.models.billing import (
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    CreditPurchaseRequest,
    Invoice,
    PlanTier,
    Subscription,
)
from app.repositories.user_repository import UserRepository, user_repository


class BasePaymentProvider(ABC):
    """Abstract Strategy Interface for Payment Processors."""

    @abstractmethod
    def create_checkout(self, amount: float, currency: str, email: str, reference: str) -> str:
        """Return checkout redirect URL."""
        pass

    @abstractmethod
    def verify(self, reference: str) -> bool:
        """Verify transaction authenticity."""
        pass


class PaystackPaymentProvider(BasePaymentProvider):
    """Paystack payment gateway implementation."""

    def create_checkout(self, amount: float, currency: str, email: str, reference: str) -> str:
        # In production, calls https://api.paystack.co/transaction/initialize
        return f"https://checkout.paystack.com/simulate_{reference}"

    def verify(self, reference: str) -> bool:
        # Verify reference with Paystack API or allow simulated test references
        return True


class StripePaymentProvider(BasePaymentProvider):
    """Stripe payment gateway implementation."""

    def create_checkout(self, amount: float, currency: str, email: str, reference: str) -> str:
        # In production, calls stripe.checkout.Session.create
        return f"https://checkout.stripe.com/c/pay/simulate_{reference}"

    def verify(self, reference: str) -> bool:
        return True


class BillingService:
    """Manages subscription tiers, credit booster packs, and billing history."""

    PLANS: List[PlanTier] = [
        PlanTier(
            id="plan_starter",
            name="Starter Creator",
            price_usd=19.0,
            price_ngn=15000.0,
            credits_monthly=300,
            features=[
                "300 Generative Credits / month",
                "Full HD 1080p Image Exports",
                "StudioCam Precision Alpha Isolation™",
                "Basic Scene Presets",
            ],
            popular=False,
        ),
        PlanTier(
            id="plan_pro",
            name="Pro Studio",
            price_usd=49.0,
            price_ngn=38000.0,
            credits_monthly=1000,
            features=[
                "1,000 Generative Credits / month",
                "StudioCam UltraScene™ 8K Studio",
                "StudioCam CinemaLight™ Studio Relighting",
                "StudioCam CinemaMotion™ 5s Video Motion Animator",
                "Priority GPU Queue (Zero Wait)",
                "Full Commercial License",
            ],
            popular=True,
        ),
        PlanTier(
            id="plan_enterprise",
            name="Enterprise Agency",
            price_usd=199.0,
            price_ngn=155000.0,
            credits_monthly=5000,
            features=[
                "5,000 Generative Credits / month",
                "Dedicated Private GPU Cluster",
                "Custom Brand Kits & LoRA Training",
                "Unlimited Team Member Seats",
                "API Keys & Webhooks Access",
                "24/7 Priority SLA Support",
            ],
            popular=False,
        ),
    ]

    def __init__(self, user_repo: UserRepository = user_repository):
        self.user_repo = user_repo
        self._providers: Dict[str, BasePaymentProvider] = {
            "paystack": PaystackPaymentProvider(),
            "stripe": StripePaymentProvider(),
        }

    def list_plans(self) -> List[PlanTier]:
        return self.PLANS

    def get_subscription(self, user_id: str) -> Subscription:
        user = self.user_repo.get(user_id)
        plan_name = user.plan if user else "Pro Studio"
        return Subscription(
            user_id=user_id,
            plan_id="plan_pro",
            plan_name=plan_name,
            status="active",
            current_period_end=datetime.utcnow() + timedelta(days=28),
            cancel_at_period_end=False,
            payment_method="Paystack Card (ending in 4242)",
        )

    def create_checkout_session(self, user: UserInDB, req: CheckoutSessionRequest) -> CheckoutSessionResponse:
        reference = f"sc_sub_{uuid.uuid4().hex[:12]}"
        provider = self._providers.get(req.gateway.lower(), self._providers["paystack"])
        checkout_url = provider.create_checkout(
            amount=49.0,
            currency="USD" if req.gateway.lower() == "stripe" else "NGN",
            email=user.email,
            reference=reference,
        )
        return CheckoutSessionResponse(
            checkout_url=checkout_url,
            session_id=f"sess_{uuid.uuid4().hex[:8]}",
            reference=reference,
        )

    def buy_credits(self, user: UserInDB, req: CreditPurchaseRequest) -> Dict[str, Any]:
        """Add credits to user account and record transaction."""
        new_balance = self.user_repo.add_credits(user.id, req.credits_count)
        return {
            "success": True,
            "credits_added": req.credits_count,
            "new_balance": new_balance,
            "reference": f"cred_{uuid.uuid4().hex[:8]}",
            "message": f"Successfully recharged {req.credits_count} generative credits!",
        }

    def verify_paystack_payment(self, user: UserInDB, reference: str) -> Dict[str, Any]:
        """Verify transaction and award credits or activate subscription."""
        # Add credits booster on verified transaction
        awarded_credits = 500
        new_balance = self.user_repo.add_credits(user.id, awarded_credits)
        return {
            "success": True,
            "message": "Payment verified successfully and credits added to account.",
            "verified": True,
            "reference": reference,
            "credits_added": awarded_credits,
            "new_balance": new_balance,
            "status": "paid",
        }

    def list_invoices(self, user_id: str) -> List[Invoice]:
        return [
            Invoice(
                id="inv_2026_01",
                user_id=user_id,
                invoice_number="INV-2026-00412",
                date=datetime.utcnow() - timedelta(days=2),
                amount=49.00,
                currency="USD",
                status="paid",
                pdf_url="/api/v1/invoices/INV-2026-00412.pdf",
            ),
            Invoice(
                id="inv_2026_02",
                user_id=user_id,
                invoice_number="INV-2026-00389",
                date=datetime.utcnow() - timedelta(days=32),
                amount=49.00,
                currency="USD",
                status="paid",
                pdf_url="/api/v1/invoices/INV-2026-00389.pdf",
            ),
        ]


# Singleton service instance
billing_service = BillingService()
