"""
Price comparison across vendors.
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class PriceComparator:
    """Compares prices across multiple vendors."""
    
    def __init__(self):
        """Initialize with mock vendor data."""
        self.vendors = {
            "Vendor A": {"Gloves": 0.15, "Syringes": 0.25, "Bandages": 0.50},
            "Vendor B": {"Gloves": 0.12, "Syringes": 0.28, "Bandages": 0.45},
            "Vendor C": {"Gloves": 0.14, "Syringes": 0.24, "Bandages": 0.52},
        }
    
    def compare_prices(self, supply_name: str) -> List[Dict]:
        """
        Compare prices for a supply across vendors.
        
        Args:
            supply_name: Name of supply
            
        Returns:
            List of vendor prices sorted by price
        """
        prices = []
        for vendor, catalog in self.vendors.items():
            if supply_name in catalog:
                prices.append({
                    "vendor": vendor,
                    "price": catalog[supply_name],
                    "supply": supply_name
                })
        
        # Sort by price
        prices.sort(key=lambda x: x["price"])
        return prices

