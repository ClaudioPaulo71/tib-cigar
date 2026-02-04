from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from database import get_session
from datetime import date

from apps.range.services import RangeService
from apps.auth.models import User
from apps.auth.deps import get_current_user, require_user

router = APIRouter(prefix="/range", tags=["range"])
templates = Jinja2Templates(directory="templates")

def get_service(session: Session = Depends(get_session)) -> RangeService:
    return RangeService(session)

# 1. Dashboard da Armaria
@router.get("/")
def listar_armas(
    request: Request, 
    service: RangeService = Depends(get_service),
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login")

    guns = service.list_guns(user)
    stats = service.get_dashboard_stats(user)
    
    return templates.TemplateResponse("range/index.html", {
        "request": request,
        "guns": guns,
        "stats": stats,
        "user": user
    })

# 2. Cadastrar Nova Arma
@router.post("/novo")
def criar_arma(
    nickname: str = Form(...),
    make: str = Form(...),
    model: str = Form(...),
    caliber: str = Form(...),
    base_price: float = Form(default=0.0),
    total_rounds: int = Form(default=0),
    foto_arma: UploadFile = File(default=None),
    arquivo_nf: UploadFile = File(default=None),
    service: RangeService = Depends(get_service),
    user: User = Depends(require_user)
):
    service.create_gun(
        user=user, nickname=nickname, make=make, model=model, caliber=caliber,
        base_price=base_price, total_rounds=total_rounds,
        foto_arma=foto_arma, arquivo_nf=arquivo_nf
    )
    return RedirectResponse(url="/range", status_code=303)

# 3. Rota de DETALHE da Arma
@router.get("/{gun_id}")
def detalhe_arma(
    gun_id: int, 
    request: Request, 
    service: RangeService = Depends(get_service),
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login")

    gun = service.get_gun(user, gun_id)
    if not gun:
        return "Gun not found"
    
    return templates.TemplateResponse("range/detail.html", {
        "request": request,
        "gun": gun,
        "user": user
    })

# 4. Rota para ADICIONAR ACESSÓRIO
@router.post("/{gun_id}/accessory")
def adicionar_acessorio(
    gun_id: int,
    type: str = Form(...),
    brand: str = Form(...),
    model: str = Form(...),
    cost: float = Form(...),
    service: RangeService = Depends(get_service),
    user: User = Depends(require_user)
):
    result = service.add_accessory(
        user=user, gun_id=gun_id, type=type, brand=brand, model=model, cost=cost
    )
    if not result:
        return "Unauthorized"

    return RedirectResponse(url=f"/range/{gun_id}", status_code=303)

# 5. Rota para REGISTRAR SESSÃO DE TIRO (Logbook)
@router.post("/{gun_id}/session")
def registrar_sessao(
    gun_id: int,
    date_str: str = Form(..., alias="date"), 
    location: str = Form(...),
    rounds_fired: int = Form(...),
    ammo_brand: str = Form(...),
    ammo_grain: int = Form(...),
    failure_count: int = Form(default=0),
    notes: str = Form(default=None),
    service: RangeService = Depends(get_service),
    user: User = Depends(require_user)
):
    data_formatada = date.fromisoformat(date_str)
    
    result = service.add_session(
        user=user, gun_id=gun_id, date_obj=data_formatada,
        location=location, rounds_fired=rounds_fired,
        ammo_brand=ammo_brand, ammo_grain=ammo_grain,
        failure_count=failure_count, notes=notes
    )
    
    if not result:
        return "Unauthorized"

    return RedirectResponse(url=f"/range/{gun_id}", status_code=303)

# 6. Rota para DAR BAIXA (Dispose)
@router.post("/{gun_id}/dispose")
def baixar_arma(
    gun_id: int,
    status: str = Form(...), # sold, donated, discarded
    date_str: str = Form(..., alias="date"),
    sale_price: float = Form(default=None),
    service: RangeService = Depends(get_service),
    user: User = Depends(require_user)
):
    data_formatada = date.fromisoformat(date_str)
    service.dispose_gun(
        user=user, gun_id=gun_id, status=status,
        date_obj=data_formatada, sale_price=sale_price
    )
    return RedirectResponse(url="/range", status_code=303)