from sqlmodel import SQLModel, create_engine, Session

# Configuração do Banco de Dados
sqlite_file_name = "tib_saas.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# check_same_thread=False é necessário para SQLite com FastAPI
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

# Função para pegar a sessão (usada nas rotas)
def get_session():
    with Session(engine) as session:
        yield session

# --- A FUNÇÃO QUE FALTOU ---
# Essa função cria o arquivo .db e as tabelas se elas não existirem
def create_db_and_tables():
    # ATUALME ESTA LINHA:
    from apps.humidor.models import Cigar, SmokingSession, CigarImage, SessionImage
    from apps.auth.models import User
    
    SQLModel.metadata.create_all(engine)