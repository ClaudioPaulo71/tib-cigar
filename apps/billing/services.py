import stripe
import os
from fastapi import Request
from sqlmodel import Session, select
from apps.auth.models import User

# Initialize Stripe with API Key from Environment
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class BillingService:
    def __init__(self, session: Session):
        self.session = session

    def create_customer(self, user: User) -> User:
        """Create a Stripe Customer for the user if not exists"""
        if user.stripe_customer_id:
            return user
        
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.full_name,
                metadata={"user_id": user.id}
            )
            user.stripe_customer_id = customer.id
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return user
        except Exception as e:
            print(f"Stripe Error: {e}")
            return user

    def create_checkout_session(self, user: User, price_id: str, success_url: str, cancel_url: str) -> str:
        """Generate a Stripe Checkout URL for subscription"""
        if not user.stripe_customer_id:
            self.create_customer(user)
        
        try:
            checkout_session = stripe.checkout.Session.create(
                customer=user.stripe_customer_id,
                payment_method_types=["card"],
                line_items=[
                    {"price": price_id, "quantity": 1},
                ],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={"user_id": user.id}
            )
            return checkout_session.url
        except Exception as e:
            print(f"Checkout Error: {e}")
            return None

    def create_portal_session(self, user: User, return_url: str) -> str:
        """Generate a Customer Portal URL for managing subscription"""
        if not user.stripe_customer_id:
            return None
            
        try:
            portal_session = stripe.billing_portal.Session.create(
                customer=user.stripe_customer_id,
                return_url=return_url
            )
            return portal_session.url
        except Exception as e:
            print(f"Portal Error: {e}")
            return None
            
    def handle_webhook_event(self, payload: bytes, sig_header: str, webhook_secret: str):
        """Process Stripe Webhook Events"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            raise Exception("Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            raise Exception("Invalid signature")

        event_type = event["type"]
        data = event["data"]["object"]

        if event_type == "checkout.session.completed":
            self._fulfill_checkout(data)
        elif event_type == "invoice.payment_succeeded":
            self._update_subscription_status(data, "active")
        elif event_type == "customer.subscription.deleted":
            self._update_subscription_status(data, "canceled")
        elif event_type == "customer.subscription.updated":
            self._update_subscription_status(data, data.get("status"))

        return {"status": "success"}

    def _fulfill_checkout(self, session_data):
        # User paid successfully via Checkout
        user_id = session_data.get("metadata", {}).get("user_id")
        if user_id:
            user = self.session.get(User, user_id)
            if user:
                user.subscription_status = "active"
                user.is_premium = True # Legacy field support if needed
                self.session.add(user)
                self.session.commit()

    def _update_subscription_status(self, invoice_or_sub_data, status):
        # Look up user by Stripe Customer ID
        customer_id = invoice_or_sub_data.get("customer")
        if customer_id:
            statement = select(User).where(User.stripe_customer_id == customer_id)
            results = self.session.exec(statement)
            user = results.first()
            if user:
                user.subscription_status = status
                # If active, is_premium = True. Else False.
                user.is_premium = (status == "active")
                self.session.add(user)
                self.session.commit()
