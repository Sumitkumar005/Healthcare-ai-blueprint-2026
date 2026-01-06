"""
Audio transcription using Groq Whisper API.
"""

import logging
import base64
import os
from typing import Optional

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

logger = logging.getLogger(__name__)


class AudioTranscriber:
    """Transcribes audio to text using Groq Whisper API."""
    
    def __init__(self):
        """Initialize transcriber."""
        self.api_key = os.getenv("GROQ_API_KEY")
        if self.api_key and GROQ_AVAILABLE:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info("Groq client initialized")
            except Exception as e:
                logger.warning(f"Could not initialize Groq: {e}")
                self.client = None
        else:
            self.client = None
    
    async def transcribe(self, audio_data: bytes, filename: str) -> Optional[str]:
        """
        Transcribe audio to text.
        
        Args:
            audio_data: Audio file bytes
            filename: Original filename
            
        Returns:
            Transcribed text or None if failed
        """
        if not self.client:
            logger.warning("Groq client not available. Returning mock transcription.")
            return "Mock transcription: Patient visited today. Vital signs stable. Wound healing well."
        
        try:
            # Save audio to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name
            
            try:
                # Transcribe using Groq Whisper
                with open(tmp_path, "rb") as audio_file:
                    transcription = self.client.audio.transcriptions.create(
                        file=audio_file,
                        model="whisper-large-v3",
                    )
                
                result = transcription.text
                logger.info(f"Transcription successful: {len(result)} characters")
                return result
                
            finally:
                # Clean up temp file
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return None

