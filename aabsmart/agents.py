"""
Agent implementations for AabSmart Farmer system.
"""

import re
from typing import Dict, List, Optional
from aabsmart.data_structures import FarmerProfile, Scenario, ETC_TABLES
from aabsmart.memory import MEMORY, SESSION
from aabsmart.tools import calculate_water_footprint, retrieve_agronomy_tips
from aabsmart.gemini_client import call_gemini


# System prompts for agents
COACH_SYSTEM_PROMPT = """You are AabSmart Farmer, a bilingual agricultural advisor helping small farmers in water-limited conditions.

Your role:
- Provide practical, actionable advice in Persian (Farsi) first
- Follow with a short English summary (2-3 sentences)
- Focus on water conservation and crop management
- Be empathetic, clear, and culturally appropriate
- Do NOT output JSON or internal field names
- Do NOT make political or governance commentary

Output format:
SECTION 1: [Persian explanation - detailed, practical guidance]
SECTION 2: [English summary - 2-3 sentences]

Keep responses focused on agricultural advice only."""


def profiler_agent(farmer_id: str, user_message: str) -> FarmerProfile:
    """
    Extract or update farmer profile from user message.
    
    Uses simple keyword matching and rule-based extraction.
    """
    # Get existing profile or create new one
    profile = MEMORY.get_profile(farmer_id)
    if profile is None:
        profile = FarmerProfile(farmer_id=farmer_id)
    
    message_lower = user_message.lower()
    
    # Extract crops (Persian crop names)
    crops_found = []
    for crop in ETC_TABLES.keys():
        if crop in user_message:
            crops_found.append(crop)
    
    # Also check for common English crop names
    english_crops = {
        "wheat": "گندم",
        "barley": "جو",
        "rice": "برنج",
        "tomato": "گوجه فرنگی",
        "cucumber": "خیار",
        "pistachio": "پسته",
        "corn": "ذرت",
        "apple": "سیب"
    }
    for eng, persian in english_crops.items():
        if eng in message_lower and persian not in crops_found:
            crops_found.append(persian)
    
    if crops_found:
        profile.main_crops = crops_found
    
    # Extract irrigation type
    if "قطره" in user_message or "drip" in message_lower:
        profile.irrigation_type = "drip"
    elif "بارانی" in user_message or "sprinkler" in message_lower:
        profile.irrigation_type = "sprinkler"
    elif "غرقابی" in user_message or "flood" in message_lower:
        profile.irrigation_type = "flood"
    
    # Extract water level
    if any(word in user_message for word in ["کم", "محدود", "low", "limited"]):
        profile.water_level = "low"
    elif any(word in user_message for word in ["زیاد", "کافی", "high", "sufficient"]):
        profile.water_level = "high"
    else:
        profile.water_level = "medium"
    
    # Extract land size (simple pattern matching)
    land_patterns = [
        r"(\d+\.?\d*)\s*هکتار",
        r"(\d+\.?\d*)\s*hectare",
        r"(\d+\.?\d*)\s*ha"
    ]
    for pattern in land_patterns:
        match = re.search(pattern, user_message, re.IGNORECASE)
        if match:
            try:
                profile.land_size_ha = float(match.group(1))
                break
            except ValueError:
                pass
    
    # Extract region (simple - look for common region keywords)
    # This is a simplified version; can be enhanced
    if "خراسان" in user_message:
        profile.region = "خراسان"
    elif "اصفهان" in user_message:
        profile.region = "اصفهان"
    elif "فارس" in user_message:
        profile.region = "فارس"
    
    # Save profile
    MEMORY.save_profile(profile)
    
    return profile


def water_footprint_agent(profile: FarmerProfile) -> Dict:
    """
    Calculate water footprint for farmer's crop mix.
    """
    # If no crops specified, return empty result
    if not profile.main_crops:
        return {
            "crop_water_m3": {},
            "total_water_m3": 0.0,
            "recommended_switches": [],
            "assumptions": "هیچ محصولی مشخص نشده است."
        }
    
    # Assume equal distribution if land size not specified
    if profile.land_size_ha is None:
        # Default to 5 hectares for calculation
        land_size = 5.0
    else:
        land_size = profile.land_size_ha
    
    # Distribute land equally among crops
    num_crops = len(profile.main_crops)
    area_per_crop = land_size / num_crops if num_crops > 0 else 0
    
    crop_mix = {crop: area_per_crop for crop in profile.main_crops}
    
    # Calculate water footprint
    result = calculate_water_footprint(
        crop_mix,
        profile.irrigation_type
    )
    
    return result


def agronomy_rag_agent(profile: FarmerProfile, user_message: str) -> Dict:
    """
    Retrieve relevant agronomy tips using mini-RAG.
    """
    # Build query from profile and message
    query_parts = []
    if profile.irrigation_type != "unknown":
        query_parts.append(profile.irrigation_type)
    if profile.water_level == "low":
        query_parts.append("کم آب")
    query_parts.append(user_message)
    
    query = " ".join(query_parts)
    
    tips = retrieve_agronomy_tips(query=query, max_tips=3)
    return tips


def scenario_agent(profile: FarmerProfile, water_footprint: Dict) -> Dict:
    """
    Generate crop scenarios (conservative and water-saving).
    """
    if not profile.main_crops:
        return {"scenarios": []}
    
    # Baseline crop mix
    if profile.land_size_ha is None:
        land_size = 5.0
    else:
        land_size = profile.land_size_ha
    
    num_crops = len(profile.main_crops)
    area_per_crop = land_size / num_crops if num_crops > 0 else 0
    
    baseline_mix = {crop: area_per_crop for crop in profile.main_crops}
    
    # Conservative scenario: equal distribution (baseline)
    conservative_wf = calculate_water_footprint(
        baseline_mix,
        profile.irrigation_type
    )
    
    conservative = Scenario(
        name="conservative",
        crop_mix=baseline_mix.copy(),
        total_water_m3=conservative_wf["total_water_m3"],
        savings_pct=0.0,
        assumptions="توزیع مساوی زمین بین محصولات"
    )
    
    # Water-saving scenario: reduce high-water crops
    water_saving_mix = baseline_mix.copy()
    
    # Reduce rice area by 50% if present
    if "برنج" in water_saving_mix:
        rice_area = water_saving_mix["برنج"]
        water_saving_mix["برنج"] = rice_area * 0.5
        # Redistribute saved area to other crops
        saved_area = rice_area * 0.5
        other_crops = [c for c in profile.main_crops if c != "برنج"]
        if other_crops:
            area_per_other = saved_area / len(other_crops)
            for crop in other_crops:
                water_saving_mix[crop] += area_per_other
    
    # If no rice, reduce largest water consumer by 30%
    else:
        # Find crop with highest water use
        crop_water = water_footprint.get("crop_water_m3", {})
        if crop_water:
            max_crop = max(crop_water.items(), key=lambda x: x[1])[0]
            if max_crop in water_saving_mix:
                reduced_area = water_saving_mix[max_crop] * 0.3
                water_saving_mix[max_crop] -= reduced_area
                # Redistribute
                other_crops = [c for c in profile.main_crops if c != max_crop]
                if other_crops:
                    area_per_other = reduced_area / len(other_crops)
                    for crop in other_crops:
                        water_saving_mix[crop] += area_per_other
    
    water_saving_wf = calculate_water_footprint(
        water_saving_mix,
        profile.irrigation_type
    )
    
    savings_pct = 0.0
    if conservative_wf["total_water_m3"] > 0:
        savings_pct = (
            (conservative_wf["total_water_m3"] - water_saving_wf["total_water_m3"]) /
            conservative_wf["total_water_m3"] * 100
        )
    
    water_saving = Scenario(
        name="water_saving",
        crop_mix=water_saving_mix,
        total_water_m3=water_saving_wf["total_water_m3"],
        savings_pct=savings_pct,
        assumptions="کاهش محصولات پرآب و توزیع مجدد سطح زیر کشت"
    )
    
    scenarios = [conservative, water_saving]
    
    # Save scenarios
    MEMORY.save_scenarios(profile.farmer_id, scenarios)
    
    return {"scenarios": scenarios}


def coach_agent(
    profile: FarmerProfile,
    water_footprint: Dict,
    tips: Dict,
    scenarios: Dict,
    user_message: str
) -> str:
    """
    Generate bilingual response using Gemini Coach Agent.
    """
    # Build context for coach
    context_parts = []
    
    context_parts.append(f"Farmer Profile:")
    context_parts.append(f"- Region: {profile.region or 'Not specified'}")
    context_parts.append(f"- Land size: {profile.land_size_ha or 'Not specified'} hectares")
    context_parts.append(f"- Main crops: {', '.join(profile.main_crops) if profile.main_crops else 'Not specified'}")
    context_parts.append(f"- Irrigation type: {profile.irrigation_type}")
    context_parts.append(f"- Water level: {profile.water_level}")
    
    context_parts.append(f"\nWater Footprint Analysis:")
    context_parts.append(f"- Total water use: {water_footprint.get('total_water_m3', 0):.0f} m³")
    for crop, water in water_footprint.get('crop_water_m3', {}).items():
        context_parts.append(f"  - {crop}: {water:.0f} m³")
    
    context_parts.append(f"\nAgronomy Tips:")
    for tip in tips.get('tips', [])[:3]:
        context_parts.append(f"- {tip['title']}: {tip['summary']}")
    
    context_parts.append(f"\nScenarios:")
    for scenario in scenarios.get('scenarios', []):
        context_parts.append(
            f"- {scenario.name}: {scenario.total_water_m3:.0f} m³ "
            f"(savings: {scenario.savings_pct:.1f}%)"
        )
    
    context_parts.append(f"\nUser Message: {user_message}")
    
    context = "\n".join(context_parts)
    
    user_prompt = f"""Based on the following information, provide bilingual agricultural advice:

{context}

Remember:
- SECTION 1: Detailed Persian explanation with practical tips
- SECTION 2: Short English summary (2-3 sentences)
- Focus on water conservation and actionable recommendations
- Be empathetic and culturally appropriate"""
    
    response = call_gemini(
        system_prompt=COACH_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.3
    )
    
    return response


def planner_agent(farmer_id: str, user_message: str) -> Dict:
    """
    Orchestrator agent that coordinates all other agents.
    """
    # Step 1: Log user message to session
    SESSION.add_turn(farmer_id, "user", user_message)
    
    # Step 2: Profiler Agent
    profile = profiler_agent(farmer_id, user_message)
    
    # Step 3: Water Footprint Agent
    water_footprint = water_footprint_agent(profile)
    
    # Step 4: Agronomy RAG Agent
    tips = agronomy_rag_agent(profile, user_message)
    
    # Step 5: Scenario Agent
    scenarios = scenario_agent(profile, water_footprint)
    
    # Step 6: Coach Agent
    answer = coach_agent(profile, water_footprint, tips, scenarios, user_message)
    
    # Step 7: Log assistant reply to session
    SESSION.add_turn(farmer_id, "assistant", answer)
    
    return {
        "profile": profile,
        "water_footprint": water_footprint,
        "tips": tips,
        "scenarios": scenarios,
        "answer": answer
    }

