"""
Memory layer for AabSmart Farmer system.
Stores farmer profiles, scenarios, and conversation sessions.
"""

from typing import Dict, List, Optional
from datetime import datetime
from aabsmart.data_structures import FarmerProfile, Scenario


class MemoryBank:
    """Stores farmer profiles and their generated scenarios."""
    
    def __init__(self):
        self.profiles: Dict[str, FarmerProfile] = {}
        self.scenarios: Dict[str, List[Scenario]] = {}
    
    def get_profile(self, farmer_id: str) -> Optional[FarmerProfile]:
        """Retrieve a farmer profile by ID."""
        return self.profiles.get(farmer_id)
    
    def save_profile(self, profile: FarmerProfile):
        """Save or update a farmer profile."""
        profile.last_updated = datetime.now().timestamp()
        self.profiles[profile.farmer_id] = profile
    
    def get_scenarios(self, farmer_id: str) -> List[Scenario]:
        """Retrieve scenarios for a farmer."""
        return self.scenarios.get(farmer_id, [])
    
    def save_scenarios(self, farmer_id: str, scenarios: List[Scenario]):
        """Save scenarios for a farmer."""
        self.scenarios[farmer_id] = scenarios
    
    def clear(self):
        """Clear all stored data (for testing)."""
        self.profiles.clear()
        self.scenarios.clear()


class SessionStore:
    """Stores recent conversation turns per farmer."""
    
    def __init__(self, max_turns: int = 10):
        self.sessions: Dict[str, List[Dict]] = {}
        self.max_turns = max_turns
    
    def add_turn(self, farmer_id: str, role: str, content: str):
        """Add a conversation turn (user or assistant)."""
        if farmer_id not in self.sessions:
            self.sessions[farmer_id] = []
        
        turn = {
            "role": role,  # "user" or "assistant"
            "content": content,
            "timestamp": datetime.now().timestamp()
        }
        
        self.sessions[farmer_id].append(turn)
        
        # Keep only last max_turns
        if len(self.sessions[farmer_id]) > self.max_turns:
            self.sessions[farmer_id] = self.sessions[farmer_id][-self.max_turns:]
    
    def get_session(self, farmer_id: str) -> List[Dict]:
        """Get conversation history for a farmer."""
        return self.sessions.get(farmer_id, [])
    
    def clear_session(self, farmer_id: str):
        """Clear session for a specific farmer."""
        if farmer_id in self.sessions:
            del self.sessions[farmer_id]
    
    def clear_all(self):
        """Clear all sessions (for testing)."""
        self.sessions.clear()


# Global singletons
MEMORY = MemoryBank()
SESSION = SessionStore()

