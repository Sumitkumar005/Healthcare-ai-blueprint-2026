"""
CAC (Customer Acquisition Cost) Calculator
"""
import logging
from typing import List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CACCalculator:
    """Calculates Customer Acquisition Cost by channel"""
    
    def calculate_cac(self, total_spend: float, patients_acquired: int) -> float:
        """Calculate CAC for a channel"""
        if patients_acquired == 0:
            return 0.0
        return total_spend / patients_acquired
    
    def calculate_by_channel(self, spends: List, patients: List) -> dict:
        """Calculate CAC for each channel"""
        channel_cac = {}
        
        for channel in set(p.spend.channel for p in spends if hasattr(p, 'spend')):
            channel_spend = sum(s.amount for s in spends if s.channel == channel)
            channel_patients = len([p for p in patients if p.acquisition_source == channel])
            cac = self.calculate_cac(channel_spend, channel_patients)
            channel_cac[channel] = {
                "cac": cac,
                "spend": channel_spend,
                "patients": channel_patients
            }
        
        return channel_cac

