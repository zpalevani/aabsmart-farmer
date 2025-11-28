"""
Tools for AabSmart Farmer system.
Includes water footprint calculator and mini-RAG retrieval.
"""

from typing import Dict, List, Optional
from aabsmart.data_structures import ETC_TABLES, IRRIGATION_EFFICIENCY


def calculate_water_footprint(
    crop_mix: Dict[str, float],
    irrigation_type: str = "unknown"
) -> Dict:
    """
    Calculate water footprint for a crop mix.
    
    Args:
        crop_mix: Dictionary mapping crop names (English) to area in hectares
        irrigation_type: Type of irrigation ("flood", "drip", "sprinkler", "unknown")
    
    Returns:
        Dictionary with:
        - crop_water_m3: Dict mapping crop names to water use in m³
        - total_water_m3: Total water use in m³
        - recommended_switches: List of recommendations
        - assumptions: String describing assumptions
    """
    crop_water_m3 = {}
    total_water_m3 = 0.0
    
    efficiency = IRRIGATION_EFFICIENCY.get(irrigation_type, 0.60)
    
    for crop_name, area_ha in crop_mix.items():
        if crop_name in ETC_TABLES:
            et_c = ETC_TABLES[crop_name]["et_c"]
            # Water needed = ETc / efficiency (to account for losses)
            water_m3 = (et_c * area_ha) / efficiency
            crop_water_m3[crop_name] = water_m3
            total_water_m3 += water_m3
        else:
            # Unknown crop - use average
            avg_et_c = 6000
            water_m3 = (avg_et_c * area_ha) / efficiency
            crop_water_m3[crop_name] = water_m3
            total_water_m3 += water_m3
    
    # Generate recommendations
    recommended_switches = []
    
    # Check for high-water crops
    high_water_crops = ["rice"]  # Rice
    for crop in high_water_crops:
        if crop in crop_mix and crop_mix[crop] > 0:
            recommended_switches.append(
                f"Reducing {crop} cultivation area can significantly reduce water consumption"
            )
    
    # Check irrigation efficiency
    if irrigation_type == "flood":
        recommended_switches.append(
            "Switching to drip irrigation can reduce water use by up to 40%"
        )
    elif irrigation_type == "unknown":
        recommended_switches.append(
            "Improving irrigation system can reduce water consumption"
        )
    
    assumptions = (
        f"Assumed irrigation efficiency for {irrigation_type} is {efficiency*100:.0f}%. "
        f"ETc values are based on average regional data."
    )
    
    return {
        "crop_water_m3": crop_water_m3,
        "total_water_m3": total_water_m3,
        "recommended_switches": recommended_switches,
        "assumptions": assumptions
    }


# Mini-RAG corpus: Agricultural tips for water conservation
AGRONOMY_TIPS = [
    {
        "id": 1,
        "title": "Irrigate at Optimal Times",
        "summary": "Irrigating in early morning or evening reduces water evaporation. Avoid irrigation during hot midday hours.",
        "keywords": ["irrigation", "time", "evaporation", "morning", "evening"]
    },
    {
        "id": 2,
        "title": "Use Mulching",
        "summary": "Using mulch (straw, dry leaves) around plants helps retain soil moisture and reduces irrigation needs.",
        "keywords": ["mulch", "moisture", "soil", "reduce irrigation"]
    },
    {
        "id": 3,
        "title": "Plant Drought-Resistant Varieties",
        "summary": "Choosing drought-resistant and low-water crop varieties can reduce irrigation needs by up to 30%.",
        "keywords": ["resistant", "drought", "varieties", "reduce water"]
    },
    {
        "id": 4,
        "title": "Drip Irrigation",
        "summary": "Drip irrigation systems deliver water directly to plant roots and prevent water waste.",
        "keywords": ["drip", "roots", "waste", "efficiency"]
    },
    {
        "id": 5,
        "title": "Soil Management",
        "summary": "Adding organic matter to soil improves water retention capacity and reduces irrigation needs.",
        "keywords": ["soil", "organic matter", "water retention", "compost"]
    },
    {
        "id": 6,
        "title": "Crop Rotation",
        "summary": "Rotating crops with low-water plants can reduce pressure on water resources.",
        "keywords": ["rotation", "crops", "low-water", "resources"]
    },
    {
        "id": 7,
        "title": "Monitor Soil Moisture",
        "summary": "Using a moisture meter or simple methods to check soil moisture before irrigation prevents unnecessary watering.",
        "keywords": ["moisture", "soil", "monitoring", "irrigation"]
    },
    {
        "id": 8,
        "title": "Optimal Planting Density",
        "summary": "Planting at appropriate density optimizes water use and reduces competition between plants.",
        "keywords": ["density", "planting", "optimal", "competition"]
    }
]


def retrieve_agronomy_tips(
    query: Optional[str] = None,
    max_tips: int = 3
) -> Dict:
    """
    Retrieve relevant agronomy tips from mini-RAG corpus.
    
    Args:
        query: Optional query string (for future keyword matching)
        max_tips: Maximum number of tips to return
    
    Returns:
        Dictionary with:
        - tips: List of tip dictionaries
        - sources: List of source identifiers
    """
    # Simple keyword matching (can be enhanced with embeddings)
    selected_tips = AGRONOMY_TIPS[:max_tips]  # For MVP, return top tips
    
    if query:
        # Simple keyword matching
        query_lower = query.lower()
        scored_tips = []
        for tip in AGRONOMY_TIPS:
            score = 0
            for keyword in tip.get("keywords", []):
                if keyword in query_lower:
                    score += 1
            scored_tips.append((score, tip))
        
        # Sort by score and take top max_tips
        scored_tips.sort(reverse=True, key=lambda x: x[0])
        selected_tips = [tip for _, tip in scored_tips[:max_tips]]
    
    return {
        "tips": selected_tips,
        "sources": ["AabSmart Farmer Knowledge Base - Water Conservation Tips"]
    }

