from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt
from sqlmodel import Session
from database import get_session
from config import settings
from apps.auth.models import User

def get_current_user(request: Request, session: Session = Depends(get_session)):
    token = request.cookies.get("access_token")
    if not token:
        return None # Return None if no user, let the route decide if it redirects or just shows "guest"

    # Remove "Bearer " prefix if present (common in APIs, but cookies might just have the token)
    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None

    user = session.query(User).filter(User.email == email).first()
    return user

def require_user(user: User = Depends(get_current_user)):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            detail="Not authenticated",
            headers={"Location": "/auth/login"}, 
        ) 
    return user
