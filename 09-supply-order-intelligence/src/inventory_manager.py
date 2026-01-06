"""
Inventory management and usage prediction.
"""

import logging
from typing import List, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class InventoryManager:
    """Manages inventory and predicts reorder timing."""
    
    def __init__(self):
        """Initialize with sample inventory."""
        self.inventory = {
            "Gloves": {"current": 500, "reorder_point": 200, "usage_rate": 50},
            "Syringes": {"current": 1000, "reorder_point": 300, "usage_rate": 100},
            "Bandages": {"current": 200, "reorder_point": 100, "usage_rate": 20},
        }
    
    def get_inventory_status(self) -> List[Dict]:
        """Get current inventory status."""
        status = []
        for name, data in self.inventory.items():
            status.append({
                "name": name,
                "current_stock": data["current"],
                "reorder_point": data["reorder_point"],
                "usage_rate": data["usage_rate"]
            })
        return status
    
    def record_usage(self, supply_name: str, quantity: int):
        """Record supply usage."""
        if supply_name in self.inventory:
            self.inventory[supply_name]["current"] -= quantity
            if self.inventory[supply_name]["current"] < 0:
                self.inventory[supply_name]["current"] = 0
    
    def get_reorder_suggestions(self) -> List[Dict]:
        """Get supplies that need reordering."""
        suggestions = []
        for name, data in self.inventory.items():
            if data["current"] < data["reorder_point"]:
                days_until_out = data["current"] / data["usage_rate"] if data["usage_rate"] > 0 else 0
                suggestions.append({
                    "supply_name": name,
                    "current_stock": data["current"],
                    "reorder_point": data["reorder_point"],
                    "suggested_quantity": data["reorder_point"] * 2,
                    "days_until_out": days_until_out,
                    "urgent": days_until_out < 7
                })
        return suggestions

