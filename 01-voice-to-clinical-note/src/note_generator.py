"""
Clinical note generator - structures transcribed text into clinical note format.
"""

import logging
import sys
from pathlib import Path
from typing import Dict

sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))
from utils.api_client import get_free_llm_client

logger = logging.getLogger(__name__)


class ClinicalNoteGenerator:
    """Generates structured clinical notes from transcribed text."""
    
    def __init__(self):
        """Initialize note generator."""
        try:
            self.llm_client = get_free_llm_client()
            logger.info("LLM client initialized")
        except Exception as e:
            logger.warning(f"Could not initialize LLM: {e}")
            self.llm_client = None
    
    def generate(self, transcription: str, note_type: str = "visit_note") -> str:
        """
        Generate structured clinical note from transcription.
        
        Args:
            transcription: Transcribed text from audio
            note_type: Type of note (visit_note, wound_care, medication)
            
        Returns:
            Structured clinical note
        """
        try:
            prompt = self._build_prompt(transcription, note_type)
            
            if self.llm_client:
                structured_note = self.llm_client.generate(
                    prompt,
                    max_tokens=1500,
                    temperature=0.7,
                )
            else:
                structured_note = self._fallback_structure(transcription, note_type)
            
            return structured_note
            
        except Exception as e:
            logger.error(f"Error generating note: {str(e)}")
            return self._fallback_structure(transcription, note_type)
    
    def _build_prompt(self, transcription: str, note_type: str) -> str:
        """Build prompt for LLM."""
        templates = {
            "visit_note": """
Convert the following voice transcription into a professional nursing transmission note.

Transcription: {transcription}

Format the note with these sections:
- PATIENT NAME: [extract from transcription]
- VISIT DATE/TIME: [extract or use current date/time]
- VITAL SIGNS: [extract any vital signs mentioned]
- ASSESSMENT: [patient condition, observations]
- CARE PROVIDED: [treatments, procedures performed]
- PATIENT RESPONSE: [how patient responded to care]
- PLAN: [next steps, follow-up]

Use professional medical language. If information is missing, note it as "Not specified".
""",
            "wound_care": """
Convert the following voice transcription into a professional wound care note.

Transcription: {transcription}

Format with sections:
- PATIENT NAME
- VISIT DATE/TIME
- WOUND LOCATION
- WOUND DESCRIPTION: Size, appearance, drainage, odor
- WOUND CARE PROVIDED: Cleaning, dressing changes
- ASSESSMENT: Healing progress
- PLAN: Next steps
""",
            "medication": """
Convert the following voice transcription into a medication administration note.

Transcription: {transcription}

Format with sections:
- PATIENT NAME
- DATE/TIME
- MEDICATIONS ADMINISTERED: Name, dose, route, time
- PATIENT RESPONSE: Any reactions or concerns
- ASSESSMENT: Medication effectiveness
- PLAN: Continue, adjust, or discontinue
""",
        }
        
        template = templates.get(note_type, templates["visit_note"])
        return template.format(transcription=transcription)
    
    def _fallback_structure(self, transcription: str, note_type: str) -> str:
        """Fallback structure without AI."""
        return f"""
CLINICAL NOTE - {note_type.upper().replace('_', ' ')}

TRANSCRIPTION:
{transcription}

NOTE: This is a basic structure. For full AI-powered formatting, configure API keys.

PATIENT NAME: [Extract from transcription]
VISIT DATE/TIME: [Current date/time]
ASSESSMENT: [Review transcription for assessment details]
CARE PROVIDED: [Review transcription for care details]
PLAN: [Review transcription for plan details]
"""

