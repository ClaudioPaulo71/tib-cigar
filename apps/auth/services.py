from typing import Optional, List
from sqlmodel import Session, select
from datetime import timedelta
from fastapi import Response, status
from fastapi.responses import RedirectResponse

from apps.auth.models import User
from apps.auth.utils import verify_password, get_password_hash, create_access_token
from config import settings

from apps.core.base_service import BaseService

class AuthService(BaseService):

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.session.exec(select(User).where(User.email == email)).first()

    def register_user(self, email: str, password: str) -> User:
        hashed_pw = get_password_hash(password)
        new_user = User(email=email, hashed_password=hashed_pw)
        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)
        return new_user

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def login_user(self, user: User) -> Response:
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

    def logout_user(self) -> Response:
        resp = RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
        resp.delete_cookie(key="access_token")
        return resp
