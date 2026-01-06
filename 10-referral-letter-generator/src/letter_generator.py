"""
Referral letter generator.
"""

import logging
import sys
from pathlib import Path
from typing import Dict

sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))
from utils.api_client import get_free_llm_client

logger = logging.getLogger(__name__)


class ReferralLetterGenerator:
    """Generates professional referral letters."""
    
    def __init__(self):
        try:
            self.llm_client = get_free_llm_client()
        except Exception as e:
            logger.warning(f"Could not initialize LLM: {e}")
            self.llm_client = None
    
    def generate(self, request_data: Dict) -> str:
        """Generate referral letter."""
        prompt = f"""Write a professional referral letter for a {request_data.get('specialist_type', 'specialist')} consultation.

Patient Information:
- Name: {request_data.get('patient_name', 'N/A')}
- Date of Birth: {request_data.get('patient_dob', 'N/A')}

Referral Reason: {request_data.get('referral_reason', 'N/A')}

Patient History: {request_data.get('patient_history', 'N/A')}

Examination Findings: {request_data.get('examination_findings', 'Not provided')}

Test Results: {request_data.get('test_results', 'Not provided')}

Generate a formal referral letter with:
1. Professional letterhead format
2. Patient demographics
3. Chief complaint
4. Relevant history
5. Examination findings
6. Reason for referral
7. Clinical question for specialist
8. Professional closing

Use formal medical language and professional tone."""
        
        if self.llm_client:
            return self.llm_client.generate(prompt, max_tokens=1500, temperature=0.7)
        else:
            return self._fallback_letter(request_data)
    
    def _fallback_letter(self, data: Dict) -> str:
        """Fallback letter generation."""
        return f"""
REFERRAL LETTER

Date: [Current Date]

Dear Dr. [Specialist Name],

I am referring {data.get('patient_name', 'patient')} (DOB: {data.get('patient_dob', 'N/A')}) for {data.get('specialist_type', 'specialist')} consultation.

Reason for Referral: {data.get('referral_reason', 'N/A')}

Relevant History: {data.get('patient_history', 'N/A')}

Please evaluate and provide recommendations.

Sincerely,
[Provider Name]
"""


