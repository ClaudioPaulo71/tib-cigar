from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import date

# 1. Tabela de Veículos
class Veiculo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(index=True)
    marca: str
    modelo: str
    ano: int
    placa: str = Field(unique=True, index=True)
    km_atual: int
    media_km_mensal: int = Field(default=1000)
    
    # --- NOVOS CAMPOS ---
    valor_estimado: Optional[float] = Field(default=0.0) # Para o futuro gráfico financeiro
    foto: Optional[str] = None # Caminho da imagem da capa
    
    # --- LIFECYCLE ---
    status: str = Field(default="active") # active, sold, donated, discarded
    data_baixa: Optional[date] = None
    valor_venda: Optional[float] = None
    # -----------------

    user_id: Optional[int] = Field(foreign_key="user.id", default=None)
    user: Optional["User"] = Relationship(back_populates="veiculos")

    manutencoes: List["Manutencao"] = Relationship(back_populates="veiculo")
    alertas: List["Alerta"] = Relationship(back_populates="veiculo")
    
# 2. Tabela de Manutenções
class Manutencao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    data: date
    km_na_data: int
    descricao: str
    valor: float
    observacao: Optional[str] = None
    
    veiculo_id: int = Field(foreign_key="veiculo.id")
    veiculo: Optional[Veiculo] = Relationship(back_populates="manutencoes")

# 3. Tabela de Alertas
class Alerta(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tipo: str  # Ex: "Oil Change"
    km_limite: int 
    ativo: bool = True 
    
    veiculo_id: int = Field(foreign_key="veiculo.id")
    veiculo: Optional[Veiculo] = Relationship(back_populates="alertas")