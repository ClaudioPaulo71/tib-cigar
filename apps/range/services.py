from typing import List, Optional
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from fastapi import UploadFile
import shutil
import uuid
from pathlib import Path

from apps.range.models import Gun, Accessory, RangeSession
from apps.auth.models import User

class RangeService:
    def __init__(self, session: Session):
        self.session = session

    def list_guns(self, user: User, include_all: bool = False) -> List[Gun]:
        stmt = select(Gun).where(Gun.user_id == user.id)
        if not include_all:
            stmt = stmt.where(Gun.status == "active")
        stmt = stmt.options(selectinload(Gun.accessories))
        return self.session.exec(stmt).all()
        
    def dispose_gun(self, user: User, gun_id: int, status: str, date_obj, sale_price: float = None):
        gun = self.get_gun(user, gun_id)
        if not gun:
            return None
            
        gun.status = status
        gun.disposal_date = date_obj
        if sale_price:
            gun.sale_price = sale_price
            
        self.session.add(gun)
        self.session.commit()
        return gun

    def get_dashboard_stats(self, user: User) -> dict:
        guns = self.list_guns(user)
        total_rounds = sum(g.total_rounds for g in guns)
        
        # Calculate Total Valuation (Guns + Accessories)
        total_valuation = 0.0
        for gun in guns:
            total_valuation += gun.base_price
            if gun.accessories:
                total_valuation += sum(acc.cost for acc in gun.accessories)
    
        return {
            "total_valuation": total_valuation,
            "total_rounds": total_rounds,
            "gun_count": len(guns)
        }

    def get_gun(self, user: User, gun_id: int) -> Optional[Gun]:
        statement = select(Gun).where(Gun.id == gun_id).options(
            selectinload(Gun.accessories),
            selectinload(Gun.sessions)
        )
        gun = self.session.exec(statement).first()
        if gun and gun.user_id == user.id:
            return gun
        return None

    def create_gun(
        self,
        user: User,
        nickname: str, make: str, model: str, caliber: str,
        base_price: float, total_rounds: int,
        foto_arma: Optional[UploadFile],
        arquivo_nf: Optional[UploadFile]
    ) -> Gun:
        caminho_foto = self._handle_file_upload(foto_arma, "uploads/guns", "gun_")
        caminho_nf = self._handle_file_upload(arquivo_nf, "uploads/invoices", "nf_gun_")

        nova_arma = Gun(
            nickname=nickname, make=make, model=model,
            caliber=caliber, base_price=base_price,
            total_rounds=total_rounds, image=caminho_foto,
            invoice=caminho_nf, user_id=user.id
        )
        self.session.add(nova_arma)
        self.session.commit()
        return nova_arma

    def add_accessory(
        self,
        user: User,
        gun_id: int,
        type: str, brand: str, model: str, cost: float
    ) -> Optional[Accessory]:
        gun = self.get_gun(user, gun_id)
        if not gun:
            return None

        novo_acessorio = Accessory(
            gun_id=gun_id, type=type, brand=brand, model=model, cost=cost
        )
        self.session.add(novo_acessorio)
        self.session.commit()
        return novo_acessorio

    def add_session(
        self,
        user: User,
        gun_id: int,
        date_obj, # date object
        location: str,
        rounds_fired: int,
        ammo_brand: str,
        ammo_grain: int,
        failure_count: int,
        notes: Optional[str]
    ) -> Optional[RangeSession]:
        gun = self.session.get(Gun, gun_id) # Simple get for update
        if not gun or gun.user_id != user.id:
            return None

        nova_sessao = RangeSession(
            gun_id=gun_id, 
            date=date_obj, 
            location=location,
            rounds_fired=rounds_fired, 
            ammo_brand=ammo_brand,
            ammo_grain=ammo_grain, 
            failure_count=failure_count, 
            notes=notes
        )
        self.session.add(nova_sessao)

        # Update Odometer
        gun.total_rounds += rounds_fired
        self.session.add(gun)

        self.session.commit()
        return nova_sessao

    def _handle_file_upload(self, file: Optional[UploadFile], folder: str, prefix: str) -> Optional[str]:
        if not file or not file.filename:
            return None
            
        extensao = file.filename.split(".")[-1]
        nome_arquivo = f"{prefix}{uuid.uuid4()}.{extensao}"
        caminho_destino = Path(f"static/{folder}/{nome_arquivo}")
        caminho_destino.parent.mkdir(parents=True, exist_ok=True)
        
        with open(caminho_destino, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return str(caminho_destino)
