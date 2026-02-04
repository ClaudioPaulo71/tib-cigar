from sqlmodel import Session, select
from apps.core.base_service import BaseService
from apps.garage.models import Veiculo, Manutencao
from apps.range.models import Gun, RangeSession
from apps.auth.models import User

class AnalyticsService(BaseService):
    def get_aggregated_stats(self, user: User) -> dict:
        # Garage Stats (Active Only)
        vehicles = self.session.exec(select(Veiculo).where(Veiculo.user_id == user.id, Veiculo.status == "active")).all()
        garage_value = sum(v.valor_estimado for v in vehicles)
        vehicle_count = len(vehicles)
        
        maintenances = self.session.exec(select(Manutencao).join(Veiculo).where(Veiculo.user_id == user.id)).all()
        garage_maint_cost = sum(m.valor for m in maintenances)

        # Range Stats (Active Only)
        guns = self.session.exec(select(Gun).where(Gun.user_id == user.id, Gun.status == "active")).all()
        armory_value = sum(gun.base_price for gun in guns) 
        gun_count = len(guns)
        
        # Calculate accessory value (if needed, but kept simple for now)
        # Assuming Base Price includes accessories for straightforward valuation or add loop
        
        sessions = self.session.exec(select(RangeSession).join(Gun).where(Gun.user_id == user.id)).all()
        total_rounds = sum(s.rounds_fired for s in sessions)

        # Aggregated
        total_assets_value = garage_value + armory_value

        return {
            "total_assets_value": total_assets_value,
            "garage": {
                "value": garage_value,
                "count": vehicle_count,
                "maintenance_cost": garage_maint_cost
            },
            "armory": {
                "value": armory_value,
                "count": gun_count,
                "rounds_fired": total_rounds
            }
        }
