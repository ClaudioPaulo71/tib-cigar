from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn

# 1. Imports do Banco e dos Módulos
from database import create_db_and_tables 
from apps.garage.router import router as garage_router
from apps.range.router import router as range_router # <--- NOVO IMPORT

# --- CORREÇÃO AQUI: Importar direto de 'database', sem 'core.' ---
from database import create_db_and_tables 
from apps.garage.router import router as garage_router

# Ciclo de vida da aplicação (cria as tabelas ao iniciar)
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

# Monta a pasta de arquivos estáticos (CSS, Imagens, Uploads)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Inclui as rotas da Garagem
app.include_router(garage_router)

# Rota raiz (redireciona para a garagem)
@app.get("/")
def home():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/garage")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)