import sqlite3

def migrate():
    conn = sqlite3.connect("tib_saas.db")
    cursor = conn.cursor()
    
    # Garage Migration
    try:
        cursor.execute("ALTER TABLE veiculo ADD COLUMN status VARCHAR DEFAULT 'active'")
        print("Adicionado status em veiculo")
    except sqlite3.OperationalError:
        print("Coluna status ja existe em veiculo")

    try:
        cursor.execute("ALTER TABLE veiculo ADD COLUMN data_baixa DATE")
        print("Adicionado data_baixa em veiculo")
    except sqlite3.OperationalError:
        print("Coluna data_baixa ja existe em veiculo")

    try:
        cursor.execute("ALTER TABLE veiculo ADD COLUMN valor_venda FLOAT")
        print("Adicionado valor_venda em veiculo")
    except sqlite3.OperationalError:
        print("Coluna valor_venda ja existe em veiculo")

    # Range Migration
    try:
        cursor.execute("ALTER TABLE gun ADD COLUMN status VARCHAR DEFAULT 'active'")
        print("Adicionado status em gun")
    except sqlite3.OperationalError:
        print("Coluna status ja existe em gun")

    try:
        cursor.execute("ALTER TABLE gun ADD COLUMN disposal_date DATE")
        print("Adicionado disposal_date em gun")
    except sqlite3.OperationalError:
        print("Coluna disposal_date ja existe em gun")

    try:
        cursor.execute("ALTER TABLE gun ADD COLUMN sale_price FLOAT")
        print("Adicionado sale_price em gun")
    except sqlite3.OperationalError:
        print("Coluna sale_price ja existe em gun")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
