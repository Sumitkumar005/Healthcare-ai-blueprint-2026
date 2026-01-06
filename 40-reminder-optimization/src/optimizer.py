"""
Reminder optimization logic
"""
import logging
from typing import List, Dict
from collections import defaultdict

logger = logging.getLogger(__name__)


class ReminderOptimizer:
    """Optimizes reminder strategies"""
    
    def calculate_optimal_strategy(self, reminders: List) -> Dict:
        """Calculate optimal reminder strategy for patient"""
        if not reminders:
            return {
                "recommended_channel": "sms",
                "recommended_timing": 24,
                "confidence": "low"
            }
        
        # Analyze response patterns
        by_channel = defaultdict(lambda: {"sent": 0, "confirmed": 0})
        by_timing = defaultdict(lambda: {"sent": 0, "confirmed": 0})
        
        for reminder in reminders:
            by_channel[reminder.channel]["sent"] += 1
            if reminder.confirmed:
                by_channel[reminder.channel]["confirmed"] += 1
            
            by_timing[reminder.timing_hours]["sent"] += 1
            if reminder.confirmed:
                by_timing[reminder.timing_hours]["confirmed"] += 1
        
        # Find best channel
        best_channel = max(by_channel.items(), key=lambda x: (x[1]["confirmed"] / x[1]["sent"]) if x[1]["sent"] > 0 else 0)
        
        # Find best timing
        best_timing = max(by_timing.items(), key=lambda x: (x[1]["confirmed"] / x[1]["sent"]) if x[1]["sent"] > 0 else 0)
        
        return {
            "recommended_channel": best_channel[0],
            "recommended_timing": best_timing[0],
            "confidence": "high" if len(reminders) > 5 else "medium" if len(reminders) > 2 else "low"
        }
    
    def calculate_analytics(self, reminders: List) -> Dict:
        """Calculate reminder analytics"""
        total = len(reminders)
        confirmed = sum(1 for r in reminders if r.confirmed)
        opened = sum(1 for r in reminders if r.opened)
        
        return {
            "total_reminders": total,
            "confirmed": confirmed,
            "opened": opened,
            "confirmation_rate": round((confirmed / total * 100) if total > 0 else 0, 2),
            "open_rate": round((opened / total * 100) if total > 0 else 0, 2)
        }


