from fastapi import APIRouter, Depends, Form, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from datetime import timedelta
from database import get_session
from apps.auth.models import User
from apps.auth.utils import verify_password, get_password_hash, create_access_token
from config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="templates")

@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

@router.post("/register")
def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    session: Session = Depends(get_session)
):
    errors = []
    if password != confirm_password:
        errors.append("Passwords do not match")

    existing_user = session.query(User).filter(User.email == email).first()
    if existing_user:
        errors.append("Email already registered")

    if errors:
        return templates.TemplateResponse("auth/register.html", {"request": request, "errors": errors})

    hashed_pw = get_password_hash(password)
    new_user = User(email=email, hashed_password=hashed_pw)
    session.add(new_user)
    session.commit()
    
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/login")
def login(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    user = session.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("auth/login.html", {"request": request, "error": "Invalid credentials"})

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    resp = RedirectResponse(url="/garage", status_code=status.HTTP_303_SEE_OTHER)
    resp.set_cookie(
        key="access_token", 
        value=f"Bearer {access_token}", 
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return resp

@router.get("/logout")
def logout():
    resp = RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    resp.delete_cookie(key="access_token")
    return resp
