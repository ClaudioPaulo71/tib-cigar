from sqlmodel import Session, select
from database import engine, create_db_and_tables
from apps.humidor.models import Cigar
from apps.auth.models import User
import random
from datetime import date, timedelta

def create_starter_pack():
    with Session(engine) as session:
        # Get the first user (assuming it's the one currently being used)
        user = session.exec(select(User)).first()
        if not user:
            print("Error: No user found. Please Register/Login first!")
            return

        print(f"Adding cigars to user: {user.email}")

        cigars_data = [
            {"brand": "Cohiba", "line": "Behike 52", "vitola": "Laguito No. 4", "origin": "Cuba", "wrapper": "Cuban", "wrapper_color": "Colorado", "format": "Parejo With Pigtail", "length_in": 4.7, "ring_gauge": 52},
            {"brand": "Montecristo", "line": "No. 2", "vitola": "Pirámides", "origin": "Cuba", "wrapper": "Cuban", "wrapper_color": "Colorado Claro", "format": "Torpedo", "length_in": 6.1, "ring_gauge": 52},
            {"brand": "Arturo Fuente", "line": "Opus X", "vitola": "Robusto", "origin": "Dominican Republic", "wrapper": "Dominican Sun Grown", "wrapper_color": "Colorado", "format": "Parejo", "length_in": 5.2, "ring_gauge": 50},
            {"brand": "Padron", "line": "1964 Anniversary", "vitola": "Exclusivo", "origin": "Nicaragua", "wrapper": "Nicaraguan", "wrapper_color": "Maduro", "format": "Box Pressed", "length_in": 5.5, "ring_gauge": 50},
            {"brand": "Davidoff", "line": "Winston Churchill", "vitola": "The Late Hour", "origin": "Dominican Republic", "wrapper": "Ecuadorian Habano", "wrapper_color": "Oscuro", "format": "Churchill", "length_in": 7.0, "ring_gauge": 48},
            {"brand": "Partagas", "line": "Serie D No. 4", "vitola": "Robusto", "origin": "Cuba", "wrapper": "Cuban", "wrapper_color": "Colorado Red", "format": "Parejo", "length_in": 4.9, "ring_gauge": 50},
            {"brand": "Romeo y Julieta", "line": "Churchill", "vitola": "Julieta No. 2", "origin": "Cuba", "wrapper": "Cuban", "wrapper_color": "Claro", "format": "Churchill", "length_in": 7.0, "ring_gauge": 47},
            {"brand": "Hoyo de Monterrey", "line": "Epicure No. 2", "vitola": "Robusto", "origin": "Cuba", "wrapper": "Cuban", "wrapper_color": "Claro", "format": "Parejo", "length_in": 4.9, "ring_gauge": 50},
            {"brand": "Oliva", "line": "Serie V Melanio", "vitola": "Figurado", "origin": "Nicaragua", "wrapper": "Ecuadorian Sumatra", "wrapper_color": "Colorado", "format": "Figurado", "length_in": 6.5, "ring_gauge": 52},
            {"brand": "Liga Privada", "line": "No. 9", "vitola": "Toro", "origin": "Nicaragua", "wrapper": "Connecticut Broadleaf", "wrapper_color": "Oscuro", "format": "Parejo", "length_in": 6.0, "ring_gauge": 52},
            {"brand": "My Father", "line": "Le Bijou 1922", "vitola": "Torpedo", "origin": "Nicaragua", "wrapper": "Nicaraguan Habano", "wrapper_color": "Oscuro", "format": "Torpedo", "length_in": 6.1, "ring_gauge": 52},
            {"brand": "Trinidad", "line": "Fundadores", "vitola": "Laguito Especial", "origin": "Cuba", "wrapper": "Cuban", "wrapper_color": "Colorado Claro", "format": "Parejo With Pigtail", "length_in": 7.5, "ring_gauge": 40},
            {"brand": "Bolivar", "line": "Belicosos Finos", "vitola": "Campana", "origin": "Cuba", "wrapper": "Cuban", "wrapper_color": "Colorado", "format": "Belicoso", "length_in": 5.5, "ring_gauge": 52},
            {"brand": "H. Upmann", "line": "Magnum 54", "vitola": "Magnum 54", "origin": "Cuba", "wrapper": "Cuban", "wrapper_color": "Colorado Claro", "format": "Parejo", "length_in": 4.7, "ring_gauge": 54},
            {"brand": "Alec Bradley", "line": "Prensado", "vitola": "Churchill", "origin": "Honduras", "wrapper": "Trojes", "wrapper_color": "Colorado Maduro", "format": "Box Pressed", "length_in": 7.0, "ring_gauge": 48},
            {"brand": "Rocky Patel", "line": "Decade", "vitola": "Robusto", "origin": "Honduras", "wrapper": "Ecuadorian Sumatra", "wrapper_color": "Colorado", "format": "Box Pressed", "length_in": 5.0, "ring_gauge": 50},
            {"brand": "Perdomo", "line": "Reserve 10th Anniversary", "vitola": "Epicure", "origin": "Nicaragua", "wrapper": "Champagne (Connecticut)", "wrapper_color": "Claro", "format": "Parejo", "length_in": 6.0, "ring_gauge": 54},
            {"brand": "Tatuaje", "line": "Brown Label", "vitola": "Noella", "origin": "USA", "wrapper": "Ecuadorian Habano", "wrapper_color": "Colorado", "format": "Parejo", "length_in": 5.1, "ring_gauge": 42},
            {"brand": "Plasencia", "line": "Alma Fuerte", "vitola": "Nestor IV", "origin": "Nicaragua", "wrapper": "Nicaraguan Jalapa", "wrapper_color": "Oscuro", "format": "Box Pressed", "length_in": 6.2, "ring_gauge": 54},
            {"brand": "Ashton", "line": "VSG", "vitola": "Sorcerer", "origin": "Dominican Republic", "wrapper": "Ecuadorian Sumatra", "wrapper_color": "Colorado", "format": "Parejo", "length_in": 7.0, "ring_gauge": 49},
        ]

        count = 0
        for data in cigars_data:
            # Check if exists
            exists = session.exec(select(Cigar).where(Cigar.brand == data["brand"], Cigar.line == data["line"], Cigar.user_id == user.id)).first()
            if not exists:
                cigar = Cigar(
                    user_id=user.id,
                    brand=data["brand"],
                    line=data["line"],
                    vitola=data["vitola"],
                    origin=data["origin"],
                    wrapper=data["wrapper"],
                    wrapper_color=data["wrapper_color"],
                    format=data["format"],
                    length_in=data["length_in"],
                    ring_gauge=data["ring_gauge"],
                    quantity=random.randint(1, 5),
                    price_paid=round(random.uniform(15.0, 50.0), 2),
                    purchase_date=date.today() - timedelta(days=random.randint(0, 365)),
                    aging_since=date.today() - timedelta(days=random.randint(0, 365))
                )
                session.add(cigar)
                count += 1
        
        session.commit()
        print(f"Successfully added {count} cigars to your Humidor!")

if __name__ == "__main__":
    create_starter_pack()
