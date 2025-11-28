"""
Data structures for AabSmart Farmer system.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class FarmerProfile:
    """Farmer profile data structure."""
    farmer_id: str
    region: Optional[str] = None
    land_size_ha: Optional[float] = None
    main_crops: Optional[List[str]] = None
    irrigation_type: str = "unknown"  # "flood", "drip", "sprinkler", "unknown"
    water_level: str = "medium"  # "low", "medium", "high"
    risk_pref: str = "medium"  # "low", "medium", "high"
    last_updated: Optional[float] = None
    
    def __post_init__(self):
        """Set last_updated timestamp if not provided."""
        if self.last_updated is None:
            self.last_updated = datetime.now().timestamp()
        if self.main_crops is None:
            self.main_crops = []


@dataclass
class Scenario:
    """Crop scenario with water footprint calculations."""
    name: str  # e.g., "conservative", "water_saving"
    crop_mix: Dict[str, float]  # crop_name -> area_ha
    total_water_m3: float
    savings_pct: float = 0.0  # Percentage savings vs baseline
    assumptions: str = ""


# ETc (Crop Evapotranspiration) tables for common crops in Persian
# Values in m³/ha per season (approximate, for demonstration)
ETC_TABLES = {
    "گندم": {"et_c": 3500, "season": "winter"},  # Wheat
    "جو": {"et_c": 3200, "season": "winter"},  # Barley
    "پسته": {"et_c": 8500, "season": "perennial"},  # Pistachio
    "گوجه فرنگی": {"et_c": 6000, "season": "summer"},  # Tomato
    "خیار": {"et_c": 5500, "season": "summer"},  # Cucumber
    "برنج": {"et_c": 12000, "season": "summer"},  # Rice (high water use)
    "ذرت": {"et_c": 7000, "season": "summer"},  # Corn
    "سیب": {"et_c": 7500, "season": "perennial"},  # Apple
    "بادمجان": {"et_c": 5800, "season": "summer"},  # Eggplant
    "فلفل": {"et_c": 5200, "season": "summer"},  # Pepper
}

# Irrigation efficiency factors
IRRIGATION_EFFICIENCY = {
    "flood": 0.5,  # 50% efficiency (wasteful)
    "sprinkler": 0.75,  # 75% efficiency
    "drip": 0.90,  # 90% efficiency (most efficient)
    "unknown": 0.60,  # Default assumption
}

