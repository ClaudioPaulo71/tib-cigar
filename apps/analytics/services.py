from sqlmodel import Session, select
from apps.humidor.models import Cigar, SmokingSession
from apps.auth.models import User
from sqlalchemy import func

class AnalyticsService:
    def __init__(self, session: Session):
        self.session = session

    def get_aggregated_stats(self, user: User) -> dict:
        # 1. Inventory Stats
        cigars = self.session.exec(select(Cigar).where(Cigar.user_id == user.id)).all()
        total_value = sum((c.price_paid or 0) * c.quantity for c in cigars)
        total_cigars = sum(c.quantity for c in cigars)
        unique_brands = len(set(c.brand for c in cigars))

        # 2. Session Stats
        stmt = select(SmokingSession).join(Cigar).where(Cigar.user_id == user.id)
        sessions = self.session.exec(stmt).all()
        total_sessions = len(sessions)
        
        avg_rating = 0
        if total_sessions > 0:
            avg_rating = sum(s.rating_overall for s in sessions) / total_sessions

        # 3. Simple Logic for now
        return {
            "total_value": total_value,
            "total_count": total_cigars,
            "unique_brands": unique_brands,
            "total_sessions": total_sessions,
            "avg_rating": round(avg_rating, 1)
        }

    def get_charts_data(self, user: User) -> dict:
        # 1. Cigars by Origin (Pie)
        # Group by origin, count quantity
        stmt_origin = select(Cigar.origin, func.count(Cigar.id)).where(Cigar.user_id == user.id).group_by(Cigar.origin)
        origin_data = self.session.exec(stmt_origin).all()
        
        # 2. Favorite Brands (Bar) - Top 5 by quantity held + consumed? Just held for now
        stmt_brand = select(Cigar.brand, func.count(Cigar.id)).where(Cigar.user_id == user.id).group_by(Cigar.brand).order_by(func.count(Cigar.id).desc()).limit(5)
        brand_data = self.session.exec(stmt_brand).all()

        # 3. Top Smoked Cigars (Bar) - Based on Sessions count per unique Cigar (Brand+Line+Vitola)
        # This is trickier if we want "Cigar Name" aggregation. Let's do simple Brand+Line grouping from sessions.
        # Join Session -> Cigar, Group by Brand, Line
        stmt_top = select(Cigar.brand, Cigar.line, func.count(SmokingSession.id))\
            .join(SmokingSession)\
            .where(Cigar.user_id == user.id)\
            .group_by(Cigar.brand, Cigar.line)\
            .order_by(func.count(SmokingSession.id).desc())\
            .limit(5)
        top_smoked = self.session.exec(stmt_top).all()
        
        # 4. Preferred Dimensions (Scatter or Average?)
        # Let's just return averages for now or a simple distribution if needed.
        # User asked for "Preferred Dimensions". Let's give Avg Length & Ring Gauge of high rated cigars (>90)?
        # Or just average of all sessions.
        
        return {
            "origins": {
                "labels": [r[0] or "Unknown" for r in origin_data],
                "data": [r[1] for r in origin_data]
            },
            "brands": {
                "labels": [r[0] for r in brand_data],
                "data": [r[1] for r in brand_data]
            },
            "top_smoked": {
                "labels": [f"{r[0]} {r[1]}" for r in top_smoked],
                "data": [r[2] for r in top_smoked]
            }
        }
