"""
Unified API client for various LLM providers (all free tiers).
"""

import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()


class LLMClient:
    """
    Unified client for various free LLM APIs.
    Supports Groq, OpenRouter, and Together AI.
    """
    
    def __init__(self, provider: str = "groq", api_key: Optional[str] = None):
        """
        Initialize LLM client.
        
        Args:
            provider: Provider name ("groq", "openrouter", "together")
            api_key: API key (if None, reads from environment)
        """
        self.provider = provider.lower()
        self.api_key = api_key or self._get_api_key()
        
        if not self.api_key:
            raise ValueError(f"API key not found for {provider}. Set {provider.upper()}_API_KEY in .env")
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment."""
        key_map = {
            "groq": "GROQ_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
            "together": "TOGETHER_API_KEY",
        }
        
        env_key = key_map.get(self.provider)
        if env_key:
            return os.getenv(env_key)
        return None
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate text using LLM.
        
        Args:
            prompt: Input prompt
            model: Model name (uses default if None)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        try:
            if self.provider == "groq":
                return self._groq_generate(prompt, model, max_tokens, temperature)
            elif self.provider == "openrouter":
                return self._openrouter_generate(prompt, model, max_tokens, temperature)
            elif self.provider == "together":
                return self._together_generate(prompt, model, max_tokens, temperature)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise
    
    def _groq_generate(
        self, prompt: str, model: Optional[str], max_tokens: int, temperature: float
    ) -> str:
        """Generate using Groq API."""
        try:
            from groq import Groq
            
            client = Groq(api_key=self.api_key)
            model = model or "llama-3.1-8b-instant"  # Fast free model
            
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            return response.choices[0].message.content
        except ImportError:
            raise ImportError("Install groq: pip install groq")
    
    def _openrouter_generate(
        self, prompt: str, model: Optional[str], max_tokens: int, temperature: float
    ) -> str:
        """Generate using OpenRouter API."""
        try:
            import requests
            
            model = model or "meta-llama/llama-3.1-8b-instant:free"
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
                timeout=30,
            )
            
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except ImportError:
            raise ImportError("Install requests: pip install requests")
    
    def _together_generate(
        self, prompt: str, model: Optional[str], max_tokens: int, temperature: float
    ) -> str:
        """Generate using Together AI API."""
        try:
            import requests
            
            model = model or "meta-llama/Llama-3-8b-chat-hf"
            
            response = requests.post(
                "https://api.together.xyz/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
                timeout=30,
            )
            
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except ImportError:
            raise ImportError("Install requests: pip install requests")


def get_free_llm_client(provider: Optional[str] = None) -> LLMClient:
    """
    Get a free LLM client, trying providers in order.
    
    Args:
        provider: Preferred provider (None = auto-detect)
        
    Returns:
        LLMClient instance
    """
    if provider:
        return LLMClient(provider=provider)
    
    # Try providers in order of preference
    for prov in ["groq", "openrouter", "together"]:
        try:
            return LLMClient(provider=prov)
        except ValueError:
            continue
    
    raise ValueError("No free LLM API keys found. Set GROQ_API_KEY, OPENROUTER_API_KEY, or TOGETHER_API_KEY")


