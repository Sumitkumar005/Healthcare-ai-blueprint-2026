"""
Analytics engine for patient acquisition metrics
"""
import logging
from typing import List
from collections import defaultdict

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Calculates acquisition metrics and ROI"""
    
    def calculate_metrics(self, patients: List, spends: List) -> dict:
        """Calculate all acquisition metrics"""
        # Group by channel
        patients_by_channel = defaultdict(list)
        for patient in patients:
            patients_by_channel[patient.acquisition_source].append(patient)
        
        spend_by_channel = defaultdict(float)
        for spend in spends:
            spend_by_channel[spend.channel] += spend.amount
        
        # Calculate metrics
        metrics = {}
        for channel in set(list(patients_by_channel.keys()) + list(spend_by_channel.keys())):
            channel_patients = patients_by_channel.get(channel, [])
            channel_spend = spend_by_channel.get(channel, 0.0)
            
            patient_count = len(channel_patients)
            total_ltv = sum(p.lifetime_value for p in channel_patients)
            avg_ltv = total_ltv / patient_count if patient_count > 0 else 0
            
            cac = channel_spend / patient_count if patient_count > 0 else 0
            roi = ((total_ltv - channel_spend) / channel_spend * 100) if channel_spend > 0 else 0
            
            metrics[channel] = {
                "cac": round(cac, 2),
                "avg_ltv": round(avg_ltv, 2),
                "total_ltv": round(total_ltv, 2),
                "spend": round(channel_spend, 2),
                "patients": patient_count,
                "roi": round(roi, 2)
            }
        
        return {"channels": metrics}

