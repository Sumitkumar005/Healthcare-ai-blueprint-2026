"""
Program matching logic
"""
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class ProgramMatcher:
    """Matches patients to assistance programs"""
    
    def rank_programs(self, matches: List[Dict]) -> List[Dict]:
        """Rank programs by match score"""
        return sorted(matches, key=lambda x: x.get("match_score", 0), reverse=True)
    
    def get_best_match(self, matches: List[Dict]) -> Dict:
        """Get best matching program"""
        if not matches:
            return {}
        
        ranked = self.rank_programs(matches)
        return ranked[0] if ranked else {}

