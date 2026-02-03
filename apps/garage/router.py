from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from database import get_session
from datetime import date

from apps.garage.services import GarageService
from apps.auth.deps import get_current_user, require_user
from apps.auth.models import User

router = APIRouter(prefix="/garage", tags=["garage"])
templates = Jinja2Templates(directory="templates")

def get_service(session: Session = Depends(get_session)) -> GarageService:
    return GarageService(session)

# 1. Rota para LISTAR Veículos (Home)
@router.get("/")
def listar_veiculos(
    request: Request, 
    service: GarageService = Depends(get_service),
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login")
        
    veiculos = service.list_vehicles(user)
    stats = service.get_dashboard_stats(user)
    
    return templates.TemplateResponse("garage/index.html", {
        "request": request,
        "veiculos": veiculos,
        "stats": stats,
        "user": user
    })

# 2. Rota para SALVAR NOVO Veículo (Create)
@router.post("/novo")
def criar_veiculo(
    nome: str = Form(...),
    marca: str = Form(...),
    modelo: str = Form(...),
    ano: int = Form(...),
    placa: str = Form(...),
    km_atual: int = Form(...),
    valor_estimado: float = Form(default=0.0),
    foto_carro: UploadFile = File(default=None),
    service: GarageService = Depends(get_service),
    user: User = Depends(require_user)
):
    service.create_vehicle(
        user=user, nome=nome, marca=marca, modelo=modelo, ano=ano,
        placa=placa, km_atual=km_atual, valor_estimado=valor_estimado, foto=foto_carro
    )
    return RedirectResponse(url="/garage", status_code=303)

# 3. Rota para ATUALIZAR Veículo
@router.post("/{veiculo_id}/update")
def atualizar_veiculo(
    veiculo_id: int,
    nome: str = Form(...),
    marca: str = Form(...),
    modelo: str = Form(...),
    ano: int = Form(...),
    placa: str = Form(...),
    km_atual: int = Form(...),
    valor_estimado: float = Form(default=0.0),
    foto_carro: UploadFile = File(default=None),
    service: GarageService = Depends(get_service),
    user: User = Depends(require_user)
):
    service.update_vehicle(
        user=user, vehicle_id=veiculo_id,
        nome=nome, marca=marca, modelo=modelo, ano=ano,
        placa=placa, km_atual=km_atual, valor_estimado=valor_estimado, foto=foto_carro
    )
    return RedirectResponse(url="/garage", status_code=303)

# 4. Rota para ATUALIZAR ODÔMETRO
@router.post("/{veiculo_id}/update_odometer")
def atualizar_odometro(
    veiculo_id: int,
    nova_km: int = Form(...),
    service: GarageService = Depends(get_service),
    user: User = Depends(require_user)
):
    service.update_odometer(user, vehicle_id, nova_km)
    return RedirectResponse(url="/garage", status_code=303)

# 5. Rota de DETALHES
@router.get("/{veiculo_id}")
def detalhe_veiculo(
    veiculo_id: int, 
    request: Request, 
    service: GarageService = Depends(get_service),
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login")

    veiculo = service.get_vehicle(user, veiculo_id)
    if not veiculo:
        return "Vehicle not found"
        
    return templates.TemplateResponse("garage/detail.html", {
        "request": request, 
        "veiculo": veiculo, 
        "user": user
    })

# 6. Rota para ADICIONAR SERVIÇO
@router.post("/{veiculo_id}/service")
def adicionar_servico(
    veiculo_id: int,
    descricao: str = Form(...),
    data: str = Form(...),
    km_na_data: int = Form(...),
    valor: float = Form(...),
    intervalo_miles: int = Form(default=None),
    arquivo_nf: UploadFile = File(default=None),
    service: GarageService = Depends(get_service),
    user: User = Depends(require_user)
):
    data_formatada = date.fromisoformat(data)
    result = service.add_service_log(
        user=user, vehicle_id=veiculo_id,
        descricao=descricao, data_obj=data_formatada,
        km_na_data=km_na_data, valor=valor,
        intervalo_miles=intervalo_miles, arquivo_nf=arquivo_nf
    )
    
    if not result:
         return "Unauthorized"

    return RedirectResponse(url=f"/garage/{veiculo_id}", status_code=303)