"""
Appointment preparation coach.
"""

import logging
import sys
from pathlib import Path
from typing import Dict

sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))
from utils.api_client import get_free_llm_client

logger = logging.getLogger(__name__)


class AppointmentPrepCoach:
    """Generates appointment preparation guides."""
    
    def __init__(self):
        try:
            self.llm_client = get_free_llm_client()
        except Exception as e:
            logger.warning(f"Could not initialize LLM: {e}")
            self.llm_client = None
    
    def generate_prep_guide(self, request_data: Dict) -> str:
        """Generate appointment preparation guide."""
        prompt = f"""Create an appointment preparation guide for a {request_data.get('appointment_type', 'appointment')}.

Chief Complaint: {request_data.get('chief_complaint', 'General checkup')}

Generate a comprehensive preparation checklist including:
1. Medications to bring (current list)
2. Symptom timeline builder (when did symptoms start, frequency, severity)
3. Questions to ask the provider
4. Documents to bring (insurance card, ID, previous test results)
5. What to expect during the appointment

Format as a clear, printable checklist."""
        
        if self.llm_client:
            return self.llm_client.generate(prompt, max_tokens=1000, temperature=0.7)
        else:
            return self._fallback_guide()
    
    def _fallback_guide(self) -> str:
        """Fallback guide."""
        return """
APPOINTMENT PREPARATION CHECKLIST

□ Bring current medication list
□ Bring insurance card and ID
□ Write down symptoms with dates
□ Prepare questions for provider
□ Bring previous test results if available
□ Arrive 15 minutes early
"""

