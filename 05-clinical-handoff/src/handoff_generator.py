"""
Handoff report generator.
"""

import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))
from utils.api_client import get_free_llm_client

logger = logging.getLogger(__name__)


class HandoffGenerator:
    """Generates structured handoff reports."""
    
    def __init__(self):
        try:
            self.llm_client = get_free_llm_client()
        except:
            self.llm_client = None
    
    def generate(self, voice_notes: str) -> str:
        """
        Generate structured handoff report.
        
        Args:
            voice_notes: Transcribed voice notes or text
            
        Returns:
            Structured handoff report
        """
        prompt = f"""Convert the following shift handoff notes into a structured clinical handoff report.

Voice Notes:
{voice_notes}

Organize into sections:
1. PATIENT ID/NAME
2. CURRENT STATUS
3. EVENTS THIS SHIFT
4. PENDING TASKS
5. CRITICAL ALERTS

Highlight critical information. Use professional medical language."""
        
        if self.llm_client:
            try:
                return self.llm_client.generate(prompt, max_tokens=1500, temperature=0.7)
            except Exception as e:
                logger.warning(f"AI generation failed: {e}")
        
        # Fallback
        return f"""
CLINICAL HANDOFF REPORT

{voice_notes}

NOTE: This is a basic structure. For full AI-powered formatting, configure API keys.
"""
