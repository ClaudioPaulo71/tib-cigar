import sqlite3

def migrate():
    conn = sqlite3.connect("tib_saas.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN stripe_customer_id VARCHAR")
        print("Adicionado stripe_customer_id em user")
    except sqlite3.OperationalError:
        print("Coluna stripe_customer_id ja existe")

    try:
        cursor.execute("ALTER TABLE user ADD COLUMN subscription_status VARCHAR DEFAULT 'free'")
        print("Adicionado subscription_status em user")
    except sqlite3.OperationalError:
        print("Coluna subscription_status ja existe")

    try:
        cursor.execute("ALTER TABLE user ADD COLUMN subscription_end_date DATE")
        print("Adicionado subscription_end_date em user")
    except sqlite3.OperationalError:
        print("Coluna subscription_end_date ja existe")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
