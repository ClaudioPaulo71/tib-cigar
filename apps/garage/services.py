from typing import List, Optional
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from fastapi import UploadFile
import shutil
import uuid
from pathlib import Path

from apps.garage.models import Veiculo, Manutencao, Alerta
from apps.auth.models import User

class GarageService:
    def __init__(self, session: Session):
        self.session = session

    def list_vehicles(self, user: User, include_all: bool = False) -> List[Veiculo]:
        stmt = select(Veiculo).where(Veiculo.user_id == user.id).options(selectinload(Veiculo.alertas))
        if not include_all:
             stmt = stmt.where(Veiculo.status == "active")
        return self.session.exec(stmt).all()

    def dispose_vehicle(self, user: User, vehicle_id: int, status: str, date_obj, sale_value: float = None):
        vehicle = self.get_vehicle(user, vehicle_id)
        if not vehicle:
            return None
        
        vehicle.status = status
        vehicle.data_baixa = date_obj
        if sale_value:
            vehicle.valor_venda = sale_value
            
        self.session.add(vehicle)
        self.session.commit()
        return vehicle

    def get_dashboard_stats(self, user: User) -> dict:
        vehicles = self.list_vehicles(user)
        total_value = sum(v.valor_estimado for v in vehicles)
        total_mileage = sum(v.km_atual for v in vehicles)
        
        # Calculate maintenance cost (This is a bit heavier, might want to optimize later)
        maintenance_cost = 0
        for v in vehicles:
            # We need to load maintenances if not loaded.
            # Ideally list_vehicles should selectinload maintenances too if we use them often.
            # For now, let's do a separate efficient query for total cost
            pass 
        
        # Optimized query for maintenance cost
        stmt = select(Manutencao).join(Veiculo).where(Veiculo.user_id == user.id)
        maintenances = self.session.exec(stmt).all()
        maintenance_cost = sum(m.valor for m in maintenances)

        return {
            "fleet_value": total_value,
            "total_mileage": total_mileage,
            "maintenance_cost": maintenance_cost,
            "vehicle_count": len(vehicles)
        }

    def get_vehicle(self, user: User, vehicle_id: int) -> Optional[Veiculo]:
        vehicle = self.session.get(Veiculo, vehicle_id)
        if vehicle and vehicle.user_id == user.id:
            return vehicle
        return None

    def create_vehicle(
        self, 
        user: User, 
        nome: str, marca: str, modelo: str, ano: int, 
        placa: str, km_atual: int, valor_estimado: float, 
        foto: Optional[UploadFile]
    ) -> Veiculo:
        caminho_foto = self._handle_photo_upload(foto)
        
        novo_veiculo = Veiculo(
            user_id=user.id,
            nome=nome, marca=marca, modelo=modelo, ano=ano, placa=placa,
            km_atual=km_atual, valor_estimado=valor_estimado, foto=caminho_foto
        )
        self.session.add(novo_veiculo)
        self.session.commit()
        return novo_veiculo

    def update_vehicle(
        self,
        user: User,
        vehicle_id: int,
        nome: str, marca: str, modelo: str, ano: int,
        placa: str, km_atual: int, valor_estimado: float,
        foto: Optional[UploadFile]
    ) -> Optional[Veiculo]:
        vehicle = self.get_vehicle(user, vehicle_id)
        if not vehicle:
            return None

        vehicle.nome = nome
        vehicle.marca = marca
        vehicle.modelo = modelo
        vehicle.ano = ano
        vehicle.placa = placa
        vehicle.km_atual = km_atual
        vehicle.valor_estimado = valor_estimado

        if foto and foto.filename:
            caminho_foto = self._handle_photo_upload(foto)
            vehicle.foto = caminho_foto

        self.session.add(vehicle)
        self.session.commit()
        return vehicle

    def update_odometer(self, user: User, vehicle_id: int, new_km: int) -> Optional[Veiculo]:
        vehicle = self.get_vehicle(user, vehicle_id)
        if vehicle and new_km > vehicle.km_atual:
            vehicle.km_atual = new_km
            self.session.add(vehicle)
            self.session.commit()
            return vehicle
        return None

    def add_service_log(
        self,
        user: User,
        vehicle_id: int,
        descricao: str,
        data_obj, # date object
        km_na_data: int,
        valor: float,
        intervalo_miles: Optional[int],
        arquivo_nf: Optional[UploadFile]
    ) -> Optional[Manutencao]:
        vehicle = self.get_vehicle(user, vehicle_id)
        if not vehicle:
            return None

        caminho_final = self._handle_file_upload(arquivo_nf, "uploads", "nf_")

        novo_servico = Manutencao(
            veiculo_id=vehicle.id, descricao=descricao, data=data_obj,
            km_na_data=km_na_data, valor=valor, comprovante=caminho_final
        )
        self.session.add(novo_servico)

        # Update Odometer if service km is higher
        if km_na_data > vehicle.km_atual:
            vehicle.km_atual = km_na_data
            self.session.add(vehicle)

        # Handle Alerts
        if intervalo_miles and intervalo_miles > 0:
            self._handle_alerts(vehicle.id, descricao, km_na_data, intervalo_miles)

        self.session.commit()
        return novo_servico

    def _handle_alerts(self, vehicle_id: int, tipo: str, current_km: int, interval: int):
        # Disable old alerts of same type
        alertas_antigos = self.session.exec(
            select(Alerta).where(
                Alerta.veiculo_id == vehicle_id, 
                Alerta.tipo == tipo, 
                Alerta.ativo == True
            )
        ).all()
        for alerta in alertas_antigos:
            alerta.ativo = False
            self.session.add(alerta)
        
        # Create new alert
        novo_alerta = Alerta(
            veiculo_id=vehicle_id, 
            tipo=tipo, 
            km_limite=current_km + interval, 
            ativo=True
        )
        self.session.add(novo_alerta)

    def _handle_photo_upload(self, file: Optional[UploadFile]) -> Optional[str]:
        if not file or not file.filename:
            return None
        return self._handle_file_upload(file, "uploads/cars", "car_")

    def _handle_file_upload(self, file: UploadFile, folder: str, prefix: str) -> str:
        extensao = file.filename.split(".")[-1]
        nome_arquivo = f"{prefix}{uuid.uuid4()}.{extensao}"
        caminho_destino = Path(f"static/{folder}/{nome_arquivo}")
        caminho_destino.parent.mkdir(parents=True, exist_ok=True)
        
        with open(caminho_destino, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return str(caminho_destino)
