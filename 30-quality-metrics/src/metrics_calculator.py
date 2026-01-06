"""
Quality metrics calculator
"""
import logging
from typing import List
from collections import defaultdict

logger = logging.getLogger(__name__)


class QualityMetricsCalculator:
    """Calculates quality metrics and performance"""
    
    def check_target(self, metric_type: str, value: float) -> int:
        """Check if metric meets target"""
        targets = {
            "HbA1c": 8.0,  # <8% is target
            "Systolic_BP": 140,  # <140 is target
            "Diastolic_BP": 90  # <90 is target
        }
        
        target = targets.get(metric_type)
        if target is None:
            return 1  # Assume meets if no target defined
        
        if metric_type == "HbA1c":
            return 1 if value < target else 0
        elif "BP" in metric_type:
            return 1 if value < target else 0
        
        return 1
    
    def calculate_dashboard(self, metrics: List) -> dict:
        """Calculate dashboard metrics"""
        by_type = defaultdict(list)
        for metric in metrics:
            by_type[metric.metric_type].append(metric)
        
        results = {}
        for metric_type, metric_list in by_type.items():
            total = len(metric_list)
            meets = sum(1 for m in metric_list if m.meets_target == 1)
            rate = (meets / total * 100) if total > 0 else 0
            
            results[metric_type] = {
                "total_patients": total,
                "meets_target": meets,
                "performance_rate": round(rate, 2)
            }
        
        return {"metrics": results}

