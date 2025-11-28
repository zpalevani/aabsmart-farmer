"""
Observability and logging for AabSmart Farmer system.
"""

from typing import List, Dict, Optional
from datetime import datetime
from aabsmart.data_structures import Scenario


# Global log storage
LOGS: List[Dict] = []


def log_interaction(
    farmer_id: str,
    user_message: str,
    total_water_m3: float,
    scenarios: Dict,
    answer_preview: str,
    **kwargs
) -> None:
    """
    Log an interaction for observability.
    
    Args:
        farmer_id: Farmer identifier
        user_message: User's message
        total_water_m3: Total water footprint
        scenarios: Scenarios dictionary
        answer_preview: Preview of assistant answer
        **kwargs: Additional metadata
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "farmer_id": farmer_id,
        "user_message": user_message[:100],  # Truncate for storage
        "total_water_m3": total_water_m3,
        "num_scenarios": len(scenarios.get("scenarios", [])),
        "answer_preview": answer_preview,
        **kwargs
    }
    
    LOGS.append(log_entry)


def get_logs(
    farmer_id: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict]:
    """
    Retrieve logs, optionally filtered by farmer_id.
    
    Args:
        farmer_id: Optional filter by farmer ID
        limit: Optional limit on number of logs
    
    Returns:
        List of log entries
    """
    logs = LOGS
    if farmer_id:
        logs = [log for log in logs if log["farmer_id"] == farmer_id]
    
    if limit:
        logs = logs[-limit:]
    
    return logs


def clear_logs() -> None:
    """Clear all logs (for testing)."""
    LOGS.clear()

