from typing import List
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from database import get_session
from datetime import date

from apps.humidor.services import HumidorService
from apps.auth.deps import get_current_user, require_user
from apps.auth.models import User

router = APIRouter(prefix="/cigar", tags=["cigar"])
templates = Jinja2Templates(directory="templates")

def get_service(session: Session = Depends(get_session)) -> HumidorService:
    return HumidorService(session)

MAX_FILE_SIZE = 5 * 1024 * 1024 # 5 MB

async def validate_image_size(files: List[UploadFile]):
    for file in files:
        if file.filename:
            # Check Content-Length header first if available
            # Note: This can be spoofed, but it's a first line of defense
            # A more robust way requires reading the file which consumes the stream
            # For now, we trust standard browser behavior or catch it during read
            file.file.seek(0, 2)
            size = file.file.tell()
            file.file.seek(0)
            if size > MAX_FILE_SIZE:
                from fastapi import HTTPException
                raise HTTPException(status_code=413, detail=f"File {file.filename} exceeds maximum size of 5MB")

# --- COMMUNITY ---
@router.get("/community")
def community_library(
    request: Request,
    service: HumidorService = Depends(get_service),
    user: User = Depends(get_current_user)
):
    if not user: return RedirectResponse("/auth/login")
    
    unique_cigars = service.get_community_cigars()
    
    return templates.TemplateResponse("humidor/community.html", {
        "request": request,
        "cigars": unique_cigars,
        "user": user
    })

@router.post("/community/add")
def add_from_community(
    brand: str = Form(...),
    line: str = Form(...),
    vitola: str = Form(...),
    format: str = Form(default=None),
    wrapper: str = Form(default=None),
    wrapper_color: str = Form(default=None),
    origin: str = Form(default=None),
    length_in: float = Form(default=None),
    ring_gauge: int = Form(default=None),
    service: HumidorService = Depends(get_service),
    user: User = Depends(require_user)
):
    # Create with 0 quantity initially, user must update stock
    service.create_cigar(
        user=user, brand=brand, line=line, vitola=vitola,
        quantity=0, price_paid=0.0,
        format=format, wrapper=wrapper, wrapper_color=wrapper_color, origin=origin,
        length_in=length_in, ring_gauge=ring_gauge,
        purchase_date=date.today()
    )
    # Redirect to the main list or the new cigar detail (we'd need ID but create_cigar returns it)
    # Ideally should redirect to edit page to set quantity.
    # For now, redirect to humidor list.
    return RedirectResponse(url="/cigar", status_code=303)

# 1. List Cigars
@router.get("/")
def list_cigars(
    request: Request, 
    service: HumidorService = Depends(get_service),
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login")
        
    cigars = service.list_cigars(user)
    stats = service.get_dashboard_stats(user)
    catalog_options = service.get_catalog_options()
    
    return templates.TemplateResponse("humidor/index.html", {
        "request": request,
        "cigars": cigars,
        "stats": stats,
        "options": catalog_options,
        "user": user
    })

# 2. Add New Cigar
@router.post("/new")
async def create_cigar(
    brand: str = Form(...),
    line: str = Form(...),
    vitola: str = Form(None), # Made optional
    quantity: int = Form(...),
    price_paid: float = Form(default=0.0),
    format: str = Form(default=None),
    wrapper: str = Form(default=None),
    wrapper_color: str = Form(default=None),
    binder: str = Form(default=None),
    filler: str = Form(default=None),
    strength: str = Form(default=None),
    origin: str = Form(default=None),
    length_in: float = Form(default=None),
    ring_gauge: int = Form(default=None),
    purchase_date: str = Form(default=None),
    photos: List[UploadFile] = File(default=[]),
    service: HumidorService = Depends(get_service),
    user: User = Depends(require_user)
):
    await validate_image_size(photos)

    p_date = date.fromisoformat(purchase_date) if purchase_date else None
    
    # Filter empty files
    valid_photos = [p for p in photos if p.filename]
    
    service.create_cigar(
        user=user, brand=brand, line=line, vitola=vitola,
        quantity=quantity, price_paid=price_paid,
        format=format, wrapper=wrapper, wrapper_color=wrapper_color, 
        binder=binder, filler=filler, strength=strength,
        origin=origin,
        length_in=length_in, ring_gauge=ring_gauge,
        purchase_date=p_date, photos=valid_photos
    )
    return RedirectResponse(url="/cigar", status_code=303)

# 3. Update Cigar
@router.post("/{cigar_id}/update")
async def update_cigar(
    cigar_id: int,
    brand: str = Form(...),
    line: str = Form(...),
    vitola: str = Form(None),
    quantity: int = Form(...),
    price_paid: float = Form(default=0.0),
    format: str = Form(default=None),
    wrapper: str = Form(default=None),
    wrapper_color: str = Form(default=None),
    binder: str = Form(default=None),
    filler: str = Form(default=None),
    strength: str = Form(default=None),
    origin: str = Form(default=None),
    length_in: float = Form(default=None),
    ring_gauge: int = Form(default=None),
    photos: List[UploadFile] = File(default=[]),
    service: HumidorService = Depends(get_service),
    user: User = Depends(require_user)
):
    await validate_image_size(photos)
    
    valid_photos = [p for p in photos if p.filename]
    
    service.update_cigar(
        user=user, cigar_id=cigar_id,
        brand=brand, line=line, vitola=vitola,
        quantity=quantity, price_paid=price_paid,
        format=format, wrapper=wrapper, wrapper_color=wrapper_color, 
        binder=binder, filler=filler, strength=strength,
        origin=origin,
        length_in=length_in, ring_gauge=ring_gauge,
        photos=valid_photos
    )
    return RedirectResponse(url=f"/humidor/{cigar_id}", status_code=303)

# 4. Cigar Details
@router.get("/{cigar_id}")
def cigar_details(
    cigar_id: int, 
    request: Request, 
    service: HumidorService = Depends(get_service),
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login")

    cigar = service.get_cigar(user, cigar_id)
    if not cigar:
        return "Cigar not found"
        
    return templates.TemplateResponse("humidor/detail.html", {
        "request": request, 
        "cigar": cigar, 
        "user": user
    })

# 5. Add Smoking Session
@router.post("/{cigar_id}/session")
def add_session(
    cigar_id: int,
    date_str: str = Form(..., alias="date"),
    rating_overall: int = Form(...),
    rating_construction: int = Form(default=None),
    rating_draw: int = Form(default=None),
    rating_flavor: int = Form(default=None),
    strength_profile: str = Form(default=None),
    duration: int = Form(default=None),
    pairing: str = Form(default=None),
    notes: str = Form(default=None),
    photos: List[UploadFile] = File(default=[]),
    service: HumidorService = Depends(get_service),
    user: User = Depends(require_user)
):
    d_obj = date.fromisoformat(date_str)
    
    valid_photos = [p for p in photos if p.filename]
    
    service.add_smoking_session(
        user=user, cigar_id=cigar_id, date_obj=d_obj,
        rating_overall=rating_overall,
        rating_construction=rating_construction,
        rating_draw=rating_draw,
        rating_flavor=rating_flavor,
        strength_profile=strength_profile,
        duration_minutes=duration,
        pairing=pairing, tasting_notes=notes,
        photos=valid_photos
    )
    
    return RedirectResponse(url=f"/humidor/{cigar_id}", status_code=303)