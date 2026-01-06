"""
Performance analysis for multi-location practices
"""
import logging
from typing import List
from collections import defaultdict

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """Analyzes performance across locations"""
    
    def calculate_comparative_metrics(self, locations: List, metrics: List) -> dict:
        """Calculate comparative performance metrics"""
        # Group metrics by location
        by_location = defaultdict(list)
        for metric in metrics:
            by_location[metric.location_id].append(metric)
        
        location_performance = {}
        for location in locations:
            loc_metrics = by_location.get(location.location_id, [])
            if loc_metrics:
                # Calculate averages
                location_performance[location.location_id] = {
                    "location_name": location.location_name,
                    "avg_patient_volume": sum(m.patient_volume for m in loc_metrics) / len(loc_metrics),
                    "avg_revenue_per_visit": sum(m.revenue_per_visit for m in loc_metrics) / len(loc_metrics),
                    "avg_no_show_rate": sum(m.no_show_rate for m in loc_metrics) / len(loc_metrics),
                    "avg_satisfaction": sum(m.patient_satisfaction for m in loc_metrics if m.patient_satisfaction) / len([m for m in loc_metrics if m.patient_satisfaction]) if any(m.patient_satisfaction for m in loc_metrics) else None,
                    "avg_productivity": sum(m.provider_productivity for m in loc_metrics) / len(loc_metrics),
                    "avg_operating_costs": sum(m.operating_costs for m in loc_metrics) / len(loc_metrics)
                }
        
        # Rank locations
        if location_performance:
            ranked_by_revenue = sorted(
                location_performance.items(),
                key=lambda x: x[1]["avg_revenue_per_visit"],
                reverse=True
            )
            
            return {
                "total_locations": len(locations),
                "location_performance": location_performance,
                "rankings": {
                    "by_revenue": [loc[0] for loc in ranked_by_revenue],
                    "by_satisfaction": sorted(
                        location_performance.items(),
                        key=lambda x: x[1]["avg_satisfaction"] or 0,
                        reverse=True
                    )[:3]
                }
            }
        
        return {"total_locations": len(locations), "location_performance": {}}


