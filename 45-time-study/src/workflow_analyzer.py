"""
Workflow analysis logic
"""
import logging
from typing import List
from collections import defaultdict

logger = logging.getLogger(__name__)


class WorkflowAnalyzer:
    """Analyzes workflow patterns"""
    
    def analyze_workflow(self, task_logs: List) -> dict:
        """Analyze workflow patterns"""
        # Group by task category
        by_category = defaultdict(lambda: {"total_time": 0.0, "count": 0})
        
        for log in task_logs:
            if log.duration_minutes:
                by_category[log.task_category]["total_time"] += log.duration_minutes
                by_category[log.task_category]["count"] += 1
        
        # Calculate averages
        category_stats = {}
        for category, data in by_category.items():
            category_stats[category] = {
                "total_time": round(data["total_time"], 2),
                "count": data["count"],
                "average_time": round(data["total_time"] / data["count"], 2) if data["count"] > 0 else 0
            }
        
        # Identify bottlenecks (tasks taking longer than average)
        all_avg = sum(s["average_time"] for s in category_stats.values()) / len(category_stats) if category_stats else 0
        bottlenecks = [
            cat for cat, stats in category_stats.items()
            if stats["average_time"] > all_avg * 1.5
        ]
        
        return {
            "category_statistics": category_stats,
            "bottlenecks": bottlenecks,
            "total_tasks": len(task_logs)
        }


