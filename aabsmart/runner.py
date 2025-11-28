"""
Runner and orchestrator for AabSmart Farmer system.
"""

from typing import Dict
from aabsmart.agents import planner_agent
from aabsmart.observability import log_interaction


def run_turn(farmer_id: str, user_message: str) -> Dict:
    """
    Run a single conversation turn with AabSmart Farmer.
    
    Args:
        farmer_id: Unique identifier for the farmer
        user_message: User's message in English
    
    Returns:
        Dictionary containing all agent outputs and final answer
    """
    print(f"\n{'='*60}")
    print(f"Farmer ID: {farmer_id}")
    print(f"User Message: {user_message}")
    print(f"{'='*60}\n")
    
    # Run planner agent
    result = planner_agent(farmer_id, user_message)
    
    # Print response
    print("AabSmart Farmer Response:")
    print("-" * 60)
    print(result["answer"])
    print("-" * 60)
    
    # Log interaction
    log_interaction(
        farmer_id=farmer_id,
        user_message=user_message,
        total_water_m3=result["water_footprint"].get("total_water_m3", 0),
        scenarios=result["scenarios"],
        answer_preview=result["answer"][:200]  # First 200 chars
    )
    
    return result


def run_turn(farmer_id: str, user_message: str) -> Dict:
    """
    Run a single conversation turn with AabSmart Farmer.
    
    Args:
        farmer_id: Unique identifier for the farmer
        user_message: User's message in English
    
    Returns:
        Dictionary containing all agent outputs and final answer
    """
    print(f"\n{'='*60}")
    print(f"Farmer ID: {farmer_id}")
    print(f"User Message: {format_text_for_display(user_message)}")
    print(f"{'='*60}\n")
    
    # Run planner agent
    result = planner_agent(farmer_id, user_message)
    
    # Print response
    print("AabSmart Farmer Response:")
    print("-" * 60)
    print(format_text_for_display(result["answer"]))
    print("-" * 60)
    
    # Log interaction
    log_interaction(
        farmer_id=farmer_id,
        user_message=user_message,
        total_water_m3=result["water_footprint"].get("total_water_m3", 0),
        scenarios=result["scenarios"],
        answer_preview=result["answer"][:200]  # First 200 chars
    )
    
    return result

