"""
Handoff transcription (reuses transcriber from project 01).
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class HandoffTranscriber:
    """Transcribes voice notes for handoff."""
    
    def transcribe(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio (can reuse from project 01)."""
        # For now, return mock transcription
        # In production, use Groq Whisper API
        return "Mock transcription: Patient John Doe, stable condition, no new orders, continue current plan."
