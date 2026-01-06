"""
Social media content generation
"""
import logging
import os
from typing import Dict, List
from dotenv import load_dotenv

try:
    from groq import Groq
except ImportError:
    Groq = None

load_dotenv()
logger = logging.getLogger(__name__)


class SocialMediaContentGenerator:
    """Generates healthcare social media content"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        self.client = None
        if self.api_key and Groq:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Groq: {e}")
    
    def generate_content(self, topic: str, platform: str) -> Dict:
        """Generate content for topic and platform"""
        if self.client:
            try:
                prompt = f"""Create a {platform} social media post about {topic} for a healthcare practice.

Requirements:
- Medically accurate information
- HIPAA-compliant (no patient information)
- Engaging and accessible language
- Platform-optimized format
- Include relevant hashtags

Post:"""
                
                response = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "You are a healthcare social media content creator. Create HIPAA-compliant, medically accurate, engaging content."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300
                )
                
                content = response.choices[0].message.content.strip()
                
                # Extract hashtags (simplified)
                hashtags = self._extract_hashtags(content, topic)
                
                return {
                    "content": content,
                    "hashtags": hashtags
                }
            except Exception as e:
                logger.warning(f"AI generation failed: {e}")
        
        # Fallback content
        return {
            "content": f"Learn about {topic}. Contact us for more information. #Healthcare #Wellness",
            "hashtags": ["Healthcare", "Wellness", topic.replace(" ", "")]
        }
    
    def _extract_hashtags(self, content: str, topic: str) -> List[str]:
        """Extract hashtags from content"""
        hashtags = []
        words = topic.split()
        hashtags.extend([w.capitalize() for w in words[:3]])
        hashtags.extend(["Healthcare", "Wellness"])
        return hashtags[:5]


