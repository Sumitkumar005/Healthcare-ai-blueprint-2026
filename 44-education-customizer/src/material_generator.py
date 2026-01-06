"""
Education material generation
"""
import logging
import os
from typing import Optional
from dotenv import load_dotenv

try:
    from groq import Groq
except ImportError:
    Groq = None

load_dotenv()
logger = logging.getLogger(__name__)


class EducationMaterialGenerator:
    """Generates customized patient education materials"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        self.client = None
        if self.api_key and Groq:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Groq: {e}")
    
    def generate_material(
        self,
        topic: str,
        reading_level: str,
        language: str,
        specific_concerns: Optional[str] = None
    ) -> str:
        """Generate customized education material"""
        if self.client:
            try:
                prompt = f"""Create patient education material about {topic}.

Requirements:
- Reading level: {reading_level}
- Language: {language}
- Medically accurate
- Clear and accessible
- Answer specific concerns: {specific_concerns if specific_concerns else 'General information'}

Material:"""
                
                response = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "You are a patient education specialist. Create clear, accessible, medically accurate educational materials."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500
                )
                
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.warning(f"AI generation failed: {e}")
        
        # Fallback content
        return f"Patient Education: {topic}\n\nThis material provides information about {topic}. Please consult with your healthcare provider for personalized medical advice."


