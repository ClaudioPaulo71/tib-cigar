from typing import Optional, List
from sqlmodel import Session, select
from datetime import timedelta
from fastapi import Response, status, UploadFile
from fastapi.responses import RedirectResponse
import shutil
import uuid
from pathlib import Path

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
        
        resp = RedirectResponse(url="/humidor", status_code=status.HTTP_303_SEE_OTHER)
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
    # --- PROFILE MANAGEMENT ---

    def update_profile(
        self, 
        user: User, 
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        profile_image: Optional[UploadFile] = None
    ) -> User:
        if full_name: user.full_name = full_name
        if phone: user.phone = phone
        if city: user.city = city
        if state: user.state = state
        
        if profile_image and profile_image.filename:
            # Reusing the logic from HumidorService - ideally this should be a shared utility
            extensao = profile_image.filename.split(".")[-1]
            nome_arquivo = f"user_{user.id}_{uuid.uuid4()}.{extensao}"
            caminho_destino = Path(f"static/uploads/profiles/{nome_arquivo}")
            caminho_destino.parent.mkdir(parents=True, exist_ok=True)
            
            with open(caminho_destino, "wb") as buffer:
                shutil.copyfileobj(profile_image.file, buffer)
            
            user.profile_image = str(caminho_destino)
            
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
