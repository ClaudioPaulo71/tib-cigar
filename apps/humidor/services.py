from typing import List, Optional
from sqlmodel import Session, select, text
from fastapi import UploadFile
import shutil
import uuid
from pathlib import Path
from datetime import date

from apps.humidor.models import Cigar, SmokingSession, CigarImage, SessionImage
from apps.auth.models import User

class HumidorService:
    def __init__(self, session: Session):
        self.session = session

    # --- CIGAR OPERATIONS ---

    def list_cigars(self, user: User, include_all: bool = False) -> List[Cigar]:
        stmt = select(Cigar).where(Cigar.user_id == user.id)
        if not include_all:
             stmt = stmt.where(Cigar.status == "active")
        return self.session.exec(stmt).all()

    def get_cigar(self, user: User, cigar_id: int) -> Optional[Cigar]:
        cigar = self.session.get(Cigar, cigar_id)
        if cigar and cigar.user_id == user.id:
            return cigar
        return None

    def get_community_cigars(self) -> List[dict]:
        """
        Returns a list of unique cigars (Brand/Line/Vitola) from the entire database.
        Using a raw SQL approach for distinct grouping to avoid duplicates.
        """
        stmt = "SELECT brand, line, vitola, format, wrapper, wrapper_color, origin, avg(length_in) as length_in, avg(ring_gauge) as ring_gauge, count(*) as popularity FROM cigar GROUP BY brand, line, vitola ORDER BY popularity DESC"
        results = self.session.exec(text(stmt)).all()
        
        # Convert to dictionary-like objects for the template
        unique_cigars = []
        for r in results:
            unique_cigars.append({
                "brand": r[0],
                "line": r[1],
                "vitola": r[2],
                "format": r[3],
                "wrapper": r[4],
                "wrapper_color": r[5],
                "origin": r[6],
                "length_in": round(r[7], 1) if r[7] else None,
                "ring_gauge": int(r[8]) if r[8] else None,
                "popularity": r[9]
            })
        return unique_cigars

    def get_catalog_options(self) -> dict:
        """
        Returns unique sets of brands, lines, vitolas, origins, etc. for autocomplete.
        """
        # We can optimize this with distinct queries, but for now reusing community logic is fine
        # or just quick distinct selects.
        # Let's do distinct selects for cleaner lists.
        # Use scalar() or simple iteration to ensure we get values not rows
        brands = self.session.exec(select(Cigar.brand).distinct()).all()
        lines = self.session.exec(select(Cigar.line).distinct()).all()
        vitolas = self.session.exec(select(Cigar.vitola).distinct()).all()
        origins = self.session.exec(select(Cigar.origin).distinct()).all()
        wrappers = self.session.exec(select(Cigar.wrapper).distinct()).all()
        
        # Verify if elements are Row/Tuple objects or primitives.
        # Use simple list comprehension with check.
        # Note: SQLModel exec(select(col)) returns a ScalarResult which yields the value directly.
        # But let's be safe.
        return {
            "brands": sorted([b for b in brands if b]),
            "lines": sorted([l for l in lines if l]),
            "vitolas": sorted([v for v in vitolas if v]),
            "origins": sorted([o for o in origins if o]),
            "wrappers": sorted([w for w in wrappers if w])
        }
        
        return {
            "brands": sorted([b for b in brands if b]),
            "lines": sorted([l for l in lines if l]),
            "vitolas": sorted([v for v in vitolas if v]),
            "origins": sorted([o for o in origins if o]),
            "wrappers": sorted([w for w in wrappers if w])
        }

    def create_cigar(
        self, 
        user: User, 
        brand: str, line: str, vitola: str, 
        quantity: int, price_paid: float, 
        format: Optional[str] = None,
        wrapper: Optional[str] = None,
        wrapper_color: Optional[str] = None,
        origin: Optional[str] = None,
        length_in: Optional[float] = None,
        ring_gauge: Optional[int] = None,
        purchase_date: Optional[date] = None,
        photos: List[UploadFile] = []
    ) -> Cigar:
        
        new_cigar = Cigar(
            user_id=user.id,
            brand=brand, line=line, vitola=vitola,
            quantity=quantity, price_paid=price_paid,
            format=format,
            wrapper=wrapper, wrapper_color=wrapper_color, origin=origin,
            length_in=length_in, ring_gauge=ring_gauge,
            purchase_date=purchase_date,
            aging_since=purchase_date
        )
        self.session.add(new_cigar)
        self.session.commit()
        self.session.refresh(new_cigar)
        
        # Handle Photos
        if photos:
            for i, photo in enumerate(photos):
                if photo.filename:
                    url = self._handle_file_upload(photo, "uploads/cigars", f"cigar_{new_cigar.id}_")
                    # First photo is 'box' or 'default', others 'single' etc. logic can be added later
                    img_type = "main" if i == 0 else "gallery" 
                    self.add_cigar_image(new_cigar.id, url, img_type)
        
        self.session.refresh(new_cigar)
        return new_cigar

    def update_cigar(
        self,
        user: User,
        cigar_id: int,
        brand: str, line: str, vitola: str,
        quantity: int, price_paid: float,
        format: Optional[str] = None,
        wrapper: Optional[str] = None,
        wrapper_color: Optional[str] = None,
        origin: Optional[str] = None,
        length_in: Optional[float] = None,
        ring_gauge: Optional[int] = None,
        photos: List[UploadFile] = []
    ) -> Optional[Cigar]:
        cigar = self.get_cigar(user, cigar_id)
        if not cigar:
            return None

        cigar.brand = brand
        cigar.line = line
        cigar.vitola = vitola
        cigar.quantity = quantity
        cigar.price_paid = price_paid
        cigar.format = format
        cigar.wrapper = wrapper
        cigar.wrapper_color = wrapper_color
        cigar.origin = origin
        cigar.length_in = length_in
        cigar.ring_gauge = ring_gauge

        self.session.add(cigar)
        self.session.commit()
        
        if photos:
             for photo in photos:
                if photo.filename:
                    url = self._handle_file_upload(photo, "uploads/cigars", f"cigar_{cigar.id}_")
                    self.add_cigar_image(cigar.id, url, "gallery")

        self.session.refresh(cigar)
        return cigar

    def add_cigar_image(self, cigar_id: int, url: str, type: str = "generic"):
        img = CigarImage(cigar_id=cigar_id, url=url, type=type)
        self.session.add(img)
        self.session.commit()

    # --- SESSION OPERATIONS ---

    def add_smoking_session(
        self,
        user: User,
        cigar_id: int,
        date_obj: date,
        rating_overall: int,
        rating_construction: Optional[int] = None,
        rating_draw: Optional[int] = None,
        rating_flavor: Optional[int] = None,
        strength_profile: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        pairing: Optional[str] = None,
        tasting_notes: Optional[str] = None,
        photos: List[UploadFile] = []
    ) -> Optional[SmokingSession]:
        cigar = self.get_cigar(user, cigar_id)
        if not cigar:
            return None

        # Create Session
        session = SmokingSession(
            cigar_id=cigar.id,
            date=date_obj,
            rating_overall=rating_overall,
            rating_construction=rating_construction,
            rating_draw=rating_draw,
            rating_flavor=rating_flavor,
            strength_profile=strength_profile,
            duration_minutes=duration_minutes,
            pairing=pairing,
            tasting_notes=tasting_notes
        )
        self.session.add(session)
        self.session.commit()
        self.session.refresh(session)
        
        # Handle Photos
        if photos:
            for photo in photos:
                if photo.filename:
                    url = self._handle_file_upload(photo, "uploads/sessions", f"session_{session.id}_")
                    self.add_session_image(session.id, url)
        
        # Decrement Quantity
        if cigar.quantity > 0:
            cigar.quantity -= 1
            if cigar.quantity == 0:
                cigar.status = "empty"
            self.session.add(cigar)
            self.session.commit()

        return session

    def add_session_image(self, session_id: int, url: str):
        img = SessionImage(session_id=session_id, url=url)
        self.session.add(img)
        self.session.commit()
        
    # --- STATISTICS ---

    def get_dashboard_stats(self, user: User) -> dict:
        cigars = self.list_cigars(user)
        total_value = sum((c.price_paid or 0) * c.quantity for c in cigars)
        total_cigars = sum(c.quantity for c in cigars)
        
        stmt = select(SmokingSession).join(Cigar).where(Cigar.user_id == user.id)
        sessions = self.session.exec(stmt).all()
        total_sessions = len(sessions)

        return {
            "total_value": total_value,
            "total_cigars": total_cigars,
            "total_sessions": total_sessions,
            "cigar_count": len(cigars)
        }

    # --- HELPERS ---

    def _handle_file_upload(self, file: UploadFile, folder: str, prefix: str) -> str:
        extensao = file.filename.split(".")[-1]
        nome_arquivo = f"{prefix}{uuid.uuid4()}.{extensao}"
        caminho_destino = Path(f"static/{folder}/{nome_arquivo}")
        caminho_destino.parent.mkdir(parents=True, exist_ok=True)
        
        with open(caminho_destino, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return str(caminho_destino)
