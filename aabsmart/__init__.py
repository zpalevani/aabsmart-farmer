"""
AabSmart Farmer - A bilingual agricultural advisory system for water-limited farming.
"""

__version__ = "1.0.0"

from aabsmart.data_structures import FarmerProfile, Scenario
from aabsmart.memory import MemoryBank, SessionStore, MEMORY, SESSION
from aabsmart.runner import run_turn, planner_agent
from aabsmart.observability import log_interaction, LOGS
from aabsmart.evaluation import run_golden

__all__ = [
    "FarmerProfile",
    "Scenario",
    "MemoryBank",
    "SessionStore",
    "MEMORY",
    "SESSION",
    "run_turn",
    "planner_agent",
    "log_interaction",
    "LOGS",
    "run_golden",
]

