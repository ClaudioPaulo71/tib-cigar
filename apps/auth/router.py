from fastapi import APIRouter, Depends, Form, Request, Response, status, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from database import get_session
from apps.auth.services import AuthService
from apps.auth.models import User

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="templates")

def get_service(session: Session = Depends(get_session)) -> AuthService:
    return AuthService(session)

@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

@router.post("/register")
def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    service: AuthService = Depends(get_service)
):
    errors = []
    if password != confirm_password:
        errors.append("Passwords do not match")

    if service.get_user_by_email(email):
        errors.append("Email already registered")

    if errors:
        return templates.TemplateResponse("auth/register.html", {"request": request, "errors": errors})

    service.register_user(email, password)
    
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    service: AuthService = Depends(get_service)
):
    user = service.authenticate_user(email, password)
    if not user:
        return templates.TemplateResponse("auth/login.html", {"request": request, "error": "Invalid credentials"})

    return service.login_user(user)

@router.get("/logout")
def logout(
    service: AuthService = Depends(get_service)
):
    return service.logout_user()

    return service.logout_user()

from apps.auth.subscription_service import SubscriptionService
from apps.auth.deps import get_current_user, require_user

# --- PROFILE ROUTES ---

@router.get("/profile")
def profile_page(request: Request, user: User = Depends(require_user)):
    return templates.TemplateResponse("auth/profile.html", {"request": request, "user": user})

@router.post("/profile")
def update_profile(
    request: Request,
    full_name: str = Form(default=None),
    phone: str = Form(default=None),
    city: str = Form(default=None),
    state: str = Form(default=None),
    profile_image: UploadFile = File(default=None),
    service: AuthService = Depends(get_service),
    user: User = Depends(require_user)
):
    service.update_profile(user, full_name, phone, city, state, profile_image)
    return RedirectResponse(url="/auth/profile", status_code=303)

@router.get("/subscribe")
def subscribe_premium(
    request: Request,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    sub_service = SubscriptionService(session)
    success_url = str(request.url_for('dashboard')) # Redirect to analytics after success
    cancel_url = str(request.url_for('dashboard'))
    
    checkout_url = sub_service.create_checkout_session(user, success_url, cancel_url)
    
    if checkout_url:
        return RedirectResponse(checkout_url, status_code=303)
    
    return RedirectResponse("/analytics?error=payment_config_missing", status_code=303) 

