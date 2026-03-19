"""Stripe integration for subscriptions and billing."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

import stripe
from sqlalchemy.orm import Session

from gtm.config import Settings
from gtm.models.billing import Subscription
from gtm.models.user import User

logger = logging.getLogger(__name__)


def init_stripe(settings: Settings) -> None:
    """Configure the Stripe API key."""
    if settings.stripe_api_key:
        stripe.api_key = settings.stripe_api_key
        logger.info("Stripe initialized")
    else:
        logger.warning("Stripe API key not configured — billing disabled")


def create_checkout_session(
    user: User,
    plan: str,
    settings: Settings,
    db: Session,
) -> str:
    """Create a Stripe Checkout Session. Returns the checkout URL."""
    if not settings.stripe_api_key:
        raise RuntimeError("Stripe is not configured")

    price_id = (
        settings.stripe_pro_price_id
        if plan == "pro"
        else settings.stripe_agency_price_id
    )
    if not price_id:
        raise ValueError(f"No Stripe price ID configured for plan: {plan}")

    # Get or create Stripe customer
    customer_id = user.stripe_customer_id
    if not customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            name=user.name,
            metadata={"user_id": user.id},
        )
        customer_id = customer.id
        # Persist the customer ID immediately
        user.stripe_customer_id = customer_id
        db.commit()

    session = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{settings.app_url}/dashboard?checkout=success",
        cancel_url=f"{settings.app_url}/pricing?checkout=cancel",
        metadata={"user_id": user.id, "plan": plan},
    )
    return session.url


def create_portal_session(user: User, settings: Settings) -> str:
    """Create a Stripe Customer Portal session. Returns the portal URL."""
    if not user.stripe_customer_id:
        raise ValueError("User has no Stripe customer ID")

    session = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url=f"{settings.app_url}/",
    )
    return session.url


def price_to_plan(price_id: str, settings: Settings) -> str:
    """Map a Stripe price ID to a plan name."""
    if price_id == settings.stripe_pro_price_id:
        return "pro"
    if price_id == settings.stripe_agency_price_id:
        return "agency"
    return "free"


# ── Sync from Stripe (used after checkout return) ────────────


def sync_subscription_from_stripe(user: User, db: Session, settings: Settings) -> str:
    """Query Stripe for user's active subscriptions and sync to local DB.

    Called when user returns from checkout (webhooks may not reach localhost).
    Returns the updated plan name.
    """
    if not user.stripe_customer_id:
        return user.plan

    try:
        subs = stripe.Subscription.list(
            customer=user.stripe_customer_id,
            status="active",
            limit=1,
        )

        if not subs.data:
            # Check for trialing too
            subs = stripe.Subscription.list(
                customer=user.stripe_customer_id,
                status="trialing",
                limit=1,
            )

        if not subs.data:
            return user.plan

        sub_obj = subs.data[0]
        item = sub_obj["items"]["data"][0]
        price_id = item["price"]["id"]
        new_plan = price_to_plan(price_id, settings)

        # In newer Stripe API, period is on the item, not the subscription
        period_start = datetime.fromtimestamp(
            item.get("current_period_start", sub_obj.get("start_date", 0)), tz=timezone.utc
        )
        period_end = datetime.fromtimestamp(
            item.get("current_period_end", sub_obj.get("start_date", 0)), tz=timezone.utc
        )

        # Update user plan — re-query within this session to ensure it's attached
        db_user = db.query(User).filter_by(id=user.id).first()
        if db_user:
            db_user.plan = new_plan

        # Commit user plan first (critical)
        db.commit()

        # Upsert subscription record (non-critical)
        try:
            existing = db.query(Subscription).filter_by(user_id=user.id).first()
            if existing:
                existing.stripe_subscription_id = sub_obj["id"]
                existing.stripe_price_id = price_id
                existing.plan = new_plan
                existing.status = sub_obj["status"]
                existing.current_period_start = period_start
                existing.current_period_end = period_end
                existing.cancel_at_period_end = sub_obj.get("cancel_at_period_end", False)
            else:
                db.add(
                    Subscription(
                        id=str(uuid.uuid4()),
                        user_id=user.id,
                        stripe_subscription_id=sub_obj["id"],
                        stripe_price_id=price_id,
                        plan=new_plan,
                        status=sub_obj["status"],
                        current_period_start=period_start,
                        current_period_end=period_end,
                    )
                )
            db.commit()
        except Exception:
            logger.warning("Failed to upsert subscription record, but user plan was updated")

        logger.info("Synced subscription from Stripe: user=%s plan=%s", user.id, new_plan)
        return new_plan

    except Exception:
        logger.exception("Failed to sync subscription from Stripe for user %s", user.id)
        return user.plan


# ── Webhook event handlers ──────────────────────────────────


def _extract_period(sub_data: dict) -> tuple[datetime, datetime]:
    """Extract period start/end from subscription, handling API version differences."""
    item = sub_data.get("items", {}).get("data", [{}])[0] if "items" in sub_data else {}
    start_ts = item.get("current_period_start") or sub_data.get("start_date", 0)
    end_ts = item.get("current_period_end") or sub_data.get("start_date", 0)
    return (
        datetime.fromtimestamp(start_ts, tz=timezone.utc),
        datetime.fromtimestamp(end_ts, tz=timezone.utc),
    )


def handle_checkout_completed(event: dict, db: Session, settings: Settings) -> None:
    """Handle checkout.session.completed — create subscription, update user."""
    session_data = event["data"]["object"]
    user_id = session_data.get("metadata", {}).get("user_id")
    plan = session_data.get("metadata", {}).get("plan", "pro")
    customer_id = session_data.get("customer")
    subscription_id = session_data.get("subscription")

    if not user_id or not subscription_id:
        logger.warning("Checkout completed but missing user_id or subscription_id")
        return

    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        logger.error("Checkout completed for unknown user %s", user_id)
        return

    # Update user
    user.stripe_customer_id = customer_id
    user.plan = plan

    # Fetch subscription details from Stripe
    sub = stripe.Subscription.retrieve(subscription_id)
    price_id = sub["items"]["data"][0]["price"]["id"]
    period_start, period_end = _extract_period(sub)

    # Upsert subscription record
    existing = db.query(Subscription).filter_by(user_id=user_id).first()
    if existing:
        existing.stripe_subscription_id = subscription_id
        existing.stripe_price_id = price_id
        existing.plan = plan
        existing.status = sub["status"]
        existing.current_period_start = period_start
        existing.current_period_end = period_end
    else:
        db.add(
            Subscription(
                id=str(uuid.uuid4()),
                user_id=user_id,
                stripe_subscription_id=subscription_id,
                stripe_price_id=price_id,
                plan=plan,
                status=sub["status"],
                current_period_start=period_start,
                current_period_end=period_end,
            )
        )

    db.commit()
    logger.info("Checkout completed: user=%s plan=%s", user_id, plan)


def handle_subscription_updated(event: dict, db: Session, settings: Settings) -> None:
    """Handle customer.subscription.updated — sync plan/status changes."""
    sub_data = event["data"]["object"]
    sub_id = sub_data["id"]

    sub = db.query(Subscription).filter_by(stripe_subscription_id=sub_id).first()
    if not sub:
        logger.warning("Subscription updated for unknown sub %s", sub_id)
        return

    price_id = sub_data["items"]["data"][0]["price"]["id"]
    new_plan = price_to_plan(price_id, settings)
    period_start, period_end = _extract_period(sub_data)

    sub.status = sub_data["status"]
    sub.plan = new_plan
    sub.stripe_price_id = price_id
    sub.current_period_start = period_start
    sub.current_period_end = period_end
    sub.cancel_at_period_end = sub_data.get("cancel_at_period_end", False)

    # Sync user plan
    user = db.query(User).filter_by(id=sub.user_id).first()
    if user:
        if sub_data["status"] == "active":
            user.plan = new_plan
        elif sub_data["status"] in ("canceled", "unpaid"):
            user.plan = "free"

    db.commit()
    logger.info("Subscription updated: sub=%s plan=%s status=%s", sub_id, new_plan, sub_data["status"])


def handle_subscription_deleted(event: dict, db: Session, settings: Settings) -> None:
    """Handle customer.subscription.deleted — revert to free plan."""
    sub_data = event["data"]["object"]
    sub_id = sub_data["id"]

    sub = db.query(Subscription).filter_by(stripe_subscription_id=sub_id).first()
    if not sub:
        return

    user = db.query(User).filter_by(id=sub.user_id).first()
    if user:
        user.plan = "free"

    sub.status = "canceled"
    db.commit()
    logger.info("Subscription deleted: user=%s reverted to free", sub.user_id)


def handle_payment_failed(event: dict, db: Session, settings: Settings) -> None:
    """Handle invoice.payment_failed — mark subscription past_due."""
    invoice = event["data"]["object"]
    sub_id = invoice.get("subscription")
    if not sub_id:
        return

    sub = db.query(Subscription).filter_by(stripe_subscription_id=sub_id).first()
    if sub:
        sub.status = "past_due"
        db.commit()
        logger.warning("Payment failed for subscription %s", sub_id)
