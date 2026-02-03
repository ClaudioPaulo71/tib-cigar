import os
from pathlib import Path

# Definição das pastas
folders = [
    "core",
    "apps/garage",
    "apps/range",
    "templates/shared",
    "templates/garage",
    "templates/range",
    "static/css",
    "static/img",
    "static/js"
]

# Definição dos arquivos
files = [
    "core/__init__.py", "core/database.py", "core/security.py", "core/models.py", "config.py",
    "apps/__init__.py",
    "apps/garage/__init__.py", "apps/garage/router.py", "apps/garage/models.py", "apps/garage/views.py",
    "apps/range/__init__.py", "apps/range/router.py", "apps/range/models.py",
    "main.py", "requirements.txt", ".env", ".gitignore"
]

print("--- Iniciando Configuração TIB-SaaS ---")

# Criar Pastas
for folder in folders:
    Path(folder).mkdir(parents=True, exist_ok=True)
    print(f"Pasta criada: {folder}")

# Criar Arquivos
for file in files:
    filepath = Path(file)
    if not filepath.exists():
        filepath.touch()
        print(f"Arquivo criado: {file}")
    else:
        print(f"Arquivo já existe: {file}")

print("\n--- Estrutura criada com sucesso! ---")