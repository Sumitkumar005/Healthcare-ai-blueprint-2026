"""
Text processing utilities for healthcare AI projects.
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """
    Clean and normalize text input.
    
    Args:
        text: Raw text input
        
    Returns:
        Cleaned text string
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def normalize_medical_text(text: str) -> str:
    """
    Normalize medical text for processing.
    
    Args:
        text: Medical text input
        
    Returns:
        Normalized text string
    """
    if not text:
        return ""
    
    # Clean text
    text = clean_text(text)
    
    # Normalize common medical abbreviations
    abbreviations = {
        'pt': 'patient',
        'pt.': 'patient',
        'dr': 'doctor',
        'dr.': 'doctor',
        'rx': 'prescription',
        'dx': 'diagnosis',
    }
    
    # Simple normalization (case-insensitive)
    words = text.split()
    normalized_words = []
    
    for word in words:
        word_lower = word.lower().rstrip('.,!?;:')
        if word_lower in abbreviations:
            normalized_words.append(abbreviations[word_lower])
        else:
            normalized_words.append(word)
    
    return ' '.join(normalized_words)


def extract_sections(text: str, section_markers: list[str]) -> dict[str, Optional[str]]:
    """
    Extract sections from structured text.
    
    Args:
        text: Text to parse
        section_markers: List of section markers (e.g., ['Patient:', 'Date:', 'Assessment:'])
        
    Returns:
        Dictionary mapping section names to content
    """
    sections = {marker: None for marker in section_markers}
    
    for i, marker in enumerate(section_markers):
        # Find marker in text
        pattern = re.compile(rf'{re.escape(marker)}\s*(.+?)(?=\n\s*{"|".join(section_markers[i+1:])}|$)', 
                           re.IGNORECASE | re.DOTALL)
        match = pattern.search(text)
        
        if match:
            sections[marker] = match.group(1).strip()
    
    return sections


