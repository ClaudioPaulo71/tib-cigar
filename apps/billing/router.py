from fastapi import APIRouter, Request, Depends, HTTPException, Header
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from apps.auth.dependencies import get_current_user
from apps.auth.models import User
from database import get_session
import os
from .services import BillingService

router = APIRouter(prefix="/billing", tags=["Billing"])
templates = Jinja2Templates(directory="templates")

# Load Config
PREMIUM_PRICE_ID = os.getenv("STRIPE_PRICE_ID_PREMIUM") 
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

def get_service(session: Session = Depends(get_session)):
    return BillingService(session)

@router.get("/")
def pricing_page(request: Request, user: User = Depends(get_current_user)):
    """Show Pricing or Subscription Status"""
    if not user:
        return RedirectResponse("/auth/login")
        
    return templates.TemplateResponse("billing/pricing.html", {
        "request": request,
        "user": user,
        "is_premium": user.subscription_status == 'active'
    })

@router.post("/checkout")
def create_checkout(
    request: Request, 
    user: User = Depends(get_current_user), 
    service: BillingService = Depends(get_service)
):
    """Initiate Stripe Checkout"""
    if not PREMIUM_PRICE_ID:
        # Fallback for dev/demo if keys missing
        return templates.TemplateResponse("billing/error.html", {
            "request": request, 
            "error": "Billing not configured (Missing Price ID)"
        })

    checkout_url = service.create_checkout_session(
        user=user,
        price_id=PREMIUM_PRICE_ID,
        success_url=str(request.base_url) + "billing/success",
        cancel_url=str(request.base_url) + "billing?canceled=true"
    )
    
    if checkout_url:
        return RedirectResponse(checkout_url, status_code=303)
    else:
        return RedirectResponse("/billing?error=checkout_failed")

@router.get("/portal")
def customer_portal(
    request: Request, 
    user: User = Depends(get_current_user), 
    service: BillingService = Depends(get_service)
):
    """Redirect to Stripe Customer Portal"""
    portal_url = service.create_portal_session(
        user=user,
        return_url=str(request.base_url) + "billing"
    )
    if portal_url:
        return RedirectResponse(portal_url, status_code=303)
    
    return RedirectResponse("/billing")

@router.get("/success")
def billing_success(request: Request, user: User = Depends(get_current_user)):
    """Post-payment success page"""
    return templates.TemplateResponse("billing/success.html", {"request": request, "user": user})

@router.post("/webhook")
async def stripe_webhook(
    request: Request, 
    stripe_signature: str = Header(None),
    service: BillingService = Depends(get_service)
):
    """Handle Stripe Webhooks securely"""
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Webhook Secret not configured")
        
    payload = await request.body()
    try:
        service.handle_webhook_event(payload, stripe_signature, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    return {"status": "ok"}
