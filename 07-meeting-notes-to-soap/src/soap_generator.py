"""
SOAP note generator from meeting notes.
"""

import logging
import sys
from pathlib import Path
from typing import List, Dict

sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))
from utils.api_client import get_free_llm_client

logger = logging.getLogger(__name__)


class SOAPGenerator:
    """Generates discipline-specific SOAP notes from meeting notes."""
    
    def __init__(self):
        try:
            self.llm_client = get_free_llm_client()
        except Exception as e:
            logger.warning(f"Could not initialize LLM: {e}")
            self.llm_client = None
    
    def generate_soap_notes(self, meeting_notes: str, disciplines: List[str]) -> Dict[str, str]:
        """
        Generate SOAP notes for specified disciplines.
        
        Args:
            meeting_notes: Meeting notes or transcript
            disciplines: List of disciplines (nursing, pt, ot, social_work, etc.)
            
        Returns:
            Dictionary mapping discipline to SOAP note
        """
        soap_notes = {}
        
        for discipline in disciplines:
            try:
                soap_note = self._generate_discipline_soap(meeting_notes, discipline)
                soap_notes[discipline] = soap_note
            except Exception as e:
                logger.error(f"Error generating {discipline} SOAP: {e}")
                soap_notes[discipline] = f"Error generating SOAP note: {str(e)}"
        
        return soap_notes
    
    def _generate_discipline_soap(self, meeting_notes: str, discipline: str) -> str:
        """Generate SOAP note for a specific discipline."""
        discipline_focus = {
            "nursing": "nursing care, vital signs, medications, wound care, patient response",
            "pt": "physical therapy, mobility, strength, gait, functional movement",
            "ot": "occupational therapy, activities of daily living, fine motor skills, adaptive equipment",
            "social_work": "psychosocial factors, family dynamics, discharge planning, resources",
        }
        
        focus = discipline_focus.get(discipline.lower(), "general clinical information")
        
        prompt = f"""Convert the following meeting notes into a professional SOAP note for {discipline.upper()}.

Meeting Notes:
{meeting_notes}

Focus on: {focus}

Generate a SOAP note with:
S (Subjective): Patient statements, complaints, history relevant to {discipline}
O (Objective): Observable findings, measurements, assessments relevant to {discipline}
A (Assessment): Clinical judgment, diagnosis, progress relevant to {discipline}
P (Plan): Treatment plan, goals, next steps for {discipline}

Format the SOAP note clearly with sections labeled S, O, A, P."""
        
        if self.llm_client:
            return self.llm_client.generate(prompt, max_tokens=1000, temperature=0.7)
        else:
            return self._fallback_soap(meeting_notes, discipline)
    
    def _fallback_soap(self, meeting_notes: str, discipline: str) -> str:
        """Fallback SOAP generation without AI."""
        return f"""SOAP NOTE - {discipline.upper()}

S (Subjective):
Based on meeting notes: {meeting_notes[:200]}...

O (Objective):
[Extract objective findings from meeting notes]

A (Assessment):
[Clinical assessment based on meeting discussion]

P (Plan):
[Treatment plan and next steps]

Note: This is a template. For full AI-powered generation, configure API keys."""


