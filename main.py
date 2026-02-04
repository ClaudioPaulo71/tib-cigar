from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn

# 1. Imports do Banco e dos Módulos
from database import create_db_and_tables 
from apps.garage.router import router as garage_router
from apps.range.router import router as range_router
from apps.auth.router import router as auth_router

# Ciclo de vida (Cria tabelas ao iniciar)
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

from fastapi import Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from apps.auth.deps import get_current_user
from apps.auth.models import User

templates = Jinja2Templates(directory="templates")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 302:
        return RedirectResponse(url=exc.headers["Location"])
    # Return standard JSON response for other errors
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# Monta a pasta de arquivos estáticos (Imagens/CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Inclui as Rotas (Os "Apps")
from apps.analytics.router import router as analytics_router
from apps.auth.webhook_router import router as webhook_router

app.include_router(auth_router)
app.include_router(garage_router)
app.include_router(range_router)
app.include_router(analytics_router)
app.include_router(webhook_router)

# Rota raiz (Landing Page)
@app.get("/")
def home(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("landing.html", {"request": request, "user": user})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)