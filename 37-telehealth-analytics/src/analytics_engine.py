"""
Telehealth analytics engine
"""
import logging
from typing import List
from collections import defaultdict

logger = logging.getLogger(__name__)


class TelehealthAnalytics:
    """Calculates telehealth utilization metrics"""
    
    def calculate_metrics(self, visits: List) -> dict:
        """Calculate comprehensive analytics"""
        telehealth_visits = [v for v in visits if v.modality == "telehealth"]
        in_person_visits = [v for v in visits if v.modality == "in_person"]
        
        # No-show rates
        telehealth_no_shows = sum(1 for v in telehealth_visits if v.no_show)
        in_person_no_shows = sum(1 for v in in_person_visits if v.no_show)
        
        telehealth_no_show_rate = (telehealth_no_shows / len(telehealth_visits) * 100) if telehealth_visits else 0
        in_person_no_show_rate = (in_person_no_shows / len(in_person_visits) * 100) if in_person_visits else 0
        
        # Revenue
        telehealth_revenue = sum(v.revenue for v in telehealth_visits if not v.no_show)
        in_person_revenue = sum(v.revenue for v in in_person_visits if not v.no_show)
        
        telehealth_avg_revenue = telehealth_revenue / len(telehealth_visits) if telehealth_visits else 0
        in_person_avg_revenue = in_person_revenue / len(in_person_visits) if in_person_visits else 0
        
        # Satisfaction
        telehealth_satisfaction = [v.patient_satisfaction for v in telehealth_visits if v.patient_satisfaction]
        in_person_satisfaction = [v.patient_satisfaction for v in in_person_visits if v.patient_satisfaction]
        
        telehealth_avg_satisfaction = sum(telehealth_satisfaction) / len(telehealth_satisfaction) if telehealth_satisfaction else None
        in_person_avg_satisfaction = sum(in_person_satisfaction) / len(in_person_satisfaction) if in_person_satisfaction else None
        
        return {
            "telehealth": {
                "total_visits": len(telehealth_visits),
                "no_show_rate": round(telehealth_no_show_rate, 2),
                "avg_revenue": round(telehealth_avg_revenue, 2),
                "avg_satisfaction": round(telehealth_avg_satisfaction, 2) if telehealth_avg_satisfaction else None
            },
            "in_person": {
                "total_visits": len(in_person_visits),
                "no_show_rate": round(in_person_no_show_rate, 2),
                "avg_revenue": round(in_person_avg_revenue, 2),
                "avg_satisfaction": round(in_person_avg_satisfaction, 2) if in_person_avg_satisfaction else None
            }
        }


