"""Billing routes — Stripe Checkout, Portal, Sync, Webhooks."""

from __future__ import annotations

import logging

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from gtm.api.deps import get_current_user_or_dev, get_db
from gtm.config import Settings, get_settings
from gtm.models.user import User
from gtm.services.stripe_service import (
    create_checkout_session,
    create_portal_session,
    handle_checkout_completed,
    handle_payment_failed,
    handle_subscription_deleted,
    handle_subscription_updated,
    sync_subscription_from_stripe,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["billing"])


class CheckoutRequest(BaseModel):
    plan: str  # "pro" or "agency"


@router.post("/checkout")
async def checkout(
    body: CheckoutRequest,
    user: User = Depends(get_current_user_or_dev),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
):
    """Create a Stripe Checkout session and return the URL."""
    if body.plan not in ("pro", "agency"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plan must be 'pro' or 'agency'",
        )

    if user.plan == body.plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You're already on the {body.plan} plan",
        )

    if not settings.stripe_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Billing is not configured",
        )

    try:
        url = create_checkout_session(user, body.plan, settings, db)
        return {"checkout_url": url}
    except Exception as e:
        logger.exception("Failed to create checkout session")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/portal")
async def portal(
    user: User = Depends(get_current_user_or_dev),
    settings: Settings = Depends(get_settings),
):
    """Create a Stripe Customer Portal session and return the URL."""
    if not user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No billing account found. Subscribe to a plan first.",
        )

    try:
        url = create_portal_session(user, settings)
        return {"portal_url": url}
    except Exception as e:
        logger.exception("Failed to create portal session")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/sync")
async def sync_billing(
    user: User = Depends(get_current_user_or_dev),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Sync subscription status from Stripe.

    Called after checkout return since webhooks may not reach localhost in dev.
    Queries Stripe API directly for the user's active subscriptions.
    """
    if not user.stripe_customer_id:
        return {"plan": user.plan, "synced": False}

    new_plan = sync_subscription_from_stripe(user, db, settings)
    return {"plan": new_plan, "synced": True}


@router.get("/status")
async def billing_status(
    user: User = Depends(get_current_user_or_dev),
    db: Session = Depends(get_db),
):
    """Get current billing status."""
    from gtm.models.billing import Subscription

    sub = db.query(Subscription).filter_by(user_id=user.id).first()

    return {
        "plan": user.plan,
        "has_subscription": sub is not None,
        "subscription_status": sub.status if sub else None,
        "current_period_end": sub.current_period_end.isoformat() if sub else None,
        "cancel_at_period_end": sub.cancel_at_period_end if sub else False,
    }


@router.post("/webhooks")
async def webhooks(
    request: Request,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Handle Stripe webhook events.

    No user auth — verified by Stripe signature.
    """
    body = await request.body()
    sig = request.headers.get("stripe-signature", "")

    # In production, require webhook secret — reject unsigned payloads
    if settings.environment != "development" and not settings.stripe_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook secret not configured",
        )

    if settings.stripe_webhook_secret:
        try:
            event = stripe.Webhook.construct_event(
                body, sig, settings.stripe_webhook_secret
            )
        except stripe.SignatureVerificationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook signature",
            )
    elif settings.environment == "development":
        # Dev mode only — parse directly for local testing
        import json

        event = json.loads(body)
    else:
        raise HTTPException(status_code=400, detail="Webhook verification required")

    event_type = event.get("type", "")
    logger.info("Stripe webhook: %s", event_type)

    handlers = {
        "checkout.session.completed": handle_checkout_completed,
        "customer.subscription.updated": handle_subscription_updated,
        "customer.subscription.deleted": handle_subscription_deleted,
        "invoice.payment_failed": handle_payment_failed,
    }

    handler = handlers.get(event_type)
    if handler:
        try:
            handler(event, db, settings)
        except Exception:
            logger.exception("Webhook handler failed for %s", event_type)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Webhook processing failed",
            )

    return {"received": True}
