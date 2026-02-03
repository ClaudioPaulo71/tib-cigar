from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import date

# 1. A Arma (Gun) - AGORA COM INVOICE
class Gun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nickname: str = Field(index=True)
    make: str     
    model: str    
    caliber: str  
    
    total_rounds: int = Field(default=0)
    base_price: float = Field(default=0.0)
    image: Optional[str] = None
    invoice: Optional[str] = None # <--- NOVO CAMPO: Caminho da Nota Fiscal
    
    user_id: Optional[int] = Field(foreign_key="user.id", default=None)
    user: Optional["User"] = Relationship(back_populates="guns")

    # Relacionamentos
    sessions: List["RangeSession"] = Relationship(back_populates="gun")
    maintenances: List["GunMaintenance"] = Relationship(back_populates="gun")
    accessories: List["Accessory"] = Relationship(back_populates="gun") 

# 2. Acessórios
class Accessory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: str     
    brand: str    
    model: str    
    cost: float = Field(default=0.0)
    
    gun_id: Optional[int] = Field(default=None, foreign_key="gun.id")
    gun: Optional[Gun] = Relationship(back_populates="accessories")

# 3. Sessão de Tiro
class RangeSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: date
    location: str
    rounds_fired: int
    
    ammo_brand: str
    ammo_grain: int
    
    failure_count: int = Field(default=0)
    notes: Optional[str] = None
    target_photo: Optional[str] = None
    
    gun_id: int = Field(foreign_key="gun.id")
    gun: Optional[Gun] = Relationship(back_populates="sessions")

# 4. Manutenção
class GunMaintenance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: date
    type: str
    notes: Optional[str] = None
    
    gun_id: int = Field(foreign_key="gun.id")
    gun: Optional[Gun] = Relationship(back_populates="maintenances")