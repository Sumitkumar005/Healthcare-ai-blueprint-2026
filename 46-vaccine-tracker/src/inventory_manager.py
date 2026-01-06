"""
Vaccine inventory management
"""
import logging
from datetime import date, timedelta
from typing import List

logger = logging.getLogger(__name__)


class VaccineInventoryManager:
    """Manages vaccine inventory"""
    
    def check_expiration(self, expiration_date: date, days: int = 30) -> bool:
        """Check if vaccine expires within specified days"""
        if not expiration_date:
            return False
        days_until = (expiration_date - date.today()).days
        return 0 <= days_until <= days
    
    def get_expiring_soon(self, inventory: List, days: int = 30) -> List:
        """Get vaccines expiring soon"""
        today = date.today()
        expiring = []
        
        for inv in inventory:
            if inv.expiration_date:
                days_until = (inv.expiration_date - today).days
                if 0 <= days_until <= days:
                    expiring.append({
                        "vaccine_type": inv.vaccine_type,
                        "lot_number": inv.lot_number,
                        "expiration_date": inv.expiration_date.isoformat(),
                        "days_until": days_until,
                        "quantity": inv.quantity
                    })
        
        return sorted(expiring, key=lambda x: x["days_until"])
    
    def check_temperature_excursion(self, temperature: float, requirement: str) -> bool:
        """Check if temperature is within requirement"""
        if not requirement:
            return True
        
        # Parse requirement (simplified - e.g., "2-8C")
        try:
            if "2-8" in requirement or "36-46" in requirement:
                return 2.0 <= temperature <= 8.0
            elif "-20" in requirement or "-4" in requirement:
                return temperature <= -20.0
        except:
            pass
        
        return True


