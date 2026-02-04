from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from database import get_session
from apps.auth.deps import get_current_user
from apps.auth.models import User
from apps.analytics.services import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])
templates = Jinja2Templates(directory="templates")

def get_service(session: Session = Depends(get_session)) -> AnalyticsService:
    return AnalyticsService(session)

@router.get("/")
def dashboard(
    request: Request,
    service: AnalyticsService = Depends(get_service),
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login")

    stats = service.get_aggregated_stats(user)
    charts = service.get_charts_data(user)
    
    return templates.TemplateResponse("analytics/dashboard.html", {
        "request": request,
        "stats": stats,
        "charts": charts,
        "user": user
    })
