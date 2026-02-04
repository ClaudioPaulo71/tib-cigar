from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, date

if TYPE_CHECKING:
    from apps.garage.models import Veiculo
    from apps.range.models import Gun

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Monetization
    stripe_customer_id: Optional[str] = None
    subscription_status: str = Field(default="free") # free, active, past_due, canceled
    subscription_end_date: Optional[date] = None

    veiculos: List["Veiculo"] = Relationship(back_populates="user")
    guns: List["Gun"] = Relationship(back_populates="user")
