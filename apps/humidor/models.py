from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import date

# --- Image Tables ---
class CigarImage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cigar_id: int = Field(foreign_key="cigar.id")
    url: str
    type: str = Field(default="generic") # type: box, single, band, etc
    
    cigar: Optional["Cigar"] = Relationship(back_populates="images")

class SessionImage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="smokingsession.id")
    url: str
    
    session: Optional["SmokingSession"] = Relationship(back_populates="images")
    
# --- Main Models ---
class Cigar(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    brand: str
    line: str
    vitola: str
    
    # Enhanced Properties
    format: Optional[str] = None # Parejo, Torpedo, Perfecto, etc
    wrapper: Optional[str] = None # Wrapper Name (e.g. Habano)
    wrapper_color: Optional[str] = None # Maduro, Oscuro, Connecticut...
    origin: Optional[str] = None
    
    length_in: Optional[float] = None
    ring_gauge: Optional[int] = None
    
    # Inventory
    quantity: int = Field(default=0)
    price_paid: Optional[float] = Field(default=0.0)
    purchase_date: Optional[date] = None
    aging_since: Optional[date] = None
    
    notes: Optional[str] = None
    # Removed single 'photo' field in favor of CigarImage relationship
    
    # Lifecycle
    status: str = Field(default="active")
    
    user_id: Optional[int] = Field(foreign_key="user.id", default=None)
    user: Optional["User"] = Relationship(back_populates="cigars")
    
    sessions: List["SmokingSession"] = Relationship(back_populates="cigar")
    images: List["CigarImage"] = Relationship(back_populates="cigar")

class SmokingSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: date
    duration_minutes: Optional[int] = None
    pairing: Optional[str] = None 
    
    # Enhanced Ratings (1-5 Scale usually, or 1-10)
    # Let's use 1-10 for granularity as implicit in "100 scale" requests often, or stick to 5.
    # User mentioned "Visual/Tactile", "Cold Draw", "Flavor", "Combustion", "Strength"
    
    rating_construction: Optional[int] = None # Visual, Tactile, Burn
    rating_draw: Optional[int] = None # Fluxo
    rating_flavor: Optional[int] = None # Aroma, Taste
    rating_overall: int = Field(default=0) # The final score (0-100)
    
    strength_profile: Optional[str] = None # Mild, Medium, Full
    
    # Qualitative Notes
    tasting_notes: Optional[str] = None # General notes or evolved notes
    
    cigar_id: int = Field(foreign_key="cigar.id")
    cigar: Optional[Cigar] = Relationship(back_populates="sessions")
    
    images: List["SessionImage"] = Relationship(back_populates="session")