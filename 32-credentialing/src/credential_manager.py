"""
Credential management logic
"""
import logging
from datetime import datetime, timedelta
from typing import List

logger = logging.getLogger(__name__)


class CredentialManager:
    """Manages provider credentials"""
    
    def check_expiring_soon(self, expiration_date, days=90) -> bool:
        """Check if credential expires within specified days"""
        if not expiration_date:
            return False
        days_until = (expiration_date - datetime.now().date()).days
        return 0 <= days_until <= days
    
    def get_renewal_alerts(self, credentials: List) -> List[dict]:
        """Get credentials that need renewal alerts"""
        alerts = []
        for cred in credentials:
            if cred.expiration_date:
                days_until = (cred.expiration_date - datetime.now().date()).days
                if 0 <= days_until <= 90:
                    alerts.append({
                        "credential_type": cred.credential_type,
                        "expiration_date": cred.expiration_date.isoformat(),
                        "days_until": days_until,
                        "alert_level": "High" if days_until <= 30 else "Medium" if days_until <= 60 else "Low"
                    })
        return alerts

