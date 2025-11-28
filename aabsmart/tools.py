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
        crop_mix: Dictionary mapping crop names (Persian) to area in hectares
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
    high_water_crops = ["برنج"]  # Rice
    for crop in high_water_crops:
        if crop in crop_mix and crop_mix[crop] > 0:
            recommended_switches.append(
                f"کاهش سطح زیر کشت {crop} می‌تواند مصرف آب را کاهش دهد"
            )
    
    # Check irrigation efficiency
    if irrigation_type == "flood":
        recommended_switches.append(
            "استفاده از سیستم آبیاری قطره‌ای می‌تواند مصرف آب را تا 40% کاهش دهد"
        )
    elif irrigation_type == "unknown":
        recommended_switches.append(
            "بهبود سیستم آبیاری می‌تواند مصرف آب را کاهش دهد"
        )
    
    assumptions = (
        f"فرض بر این است که راندمان آبیاری {irrigation_type} برابر {efficiency*100:.0f}% است. "
        f"مقادیر ETc بر اساس داده‌های منطقه‌ای متوسط محاسبه شده است."
    )
    
    return {
        "crop_water_m3": crop_water_m3,
        "total_water_m3": total_water_m3,
        "recommended_switches": recommended_switches,
        "assumptions": assumptions
    }


# Mini-RAG corpus: Persian agricultural tips for water conservation
AGRONOMY_TIPS = [
    {
        "id": 1,
        "title": "آبیاری در زمان مناسب",
        "summary": "آبیاری در ساعات اولیه صبح یا عصر باعث کاهش تبخیر آب می‌شود. از آبیاری در ساعات گرم روز خودداری کنید.",
        "keywords": ["آبیاری", "زمان", "تبخیر", "صبح", "عصر"]
    },
    {
        "id": 2,
        "title": "مالچ‌پاشی",
        "summary": "استفاده از مالچ (کاه، برگ خشک) در اطراف گیاهان باعث حفظ رطوبت خاک و کاهش نیاز به آبیاری می‌شود.",
        "keywords": ["مالچ", "رطوبت", "خاک", "کاهش آبیاری"]
    },
    {
        "id": 3,
        "title": "کاشت گیاهان مقاوم به خشکی",
        "summary": "انتخاب ارقام مقاوم به خشکی و کم‌آب می‌تواند نیاز آبیاری را تا 30% کاهش دهد.",
        "keywords": ["مقاوم", "خشکی", "ارقام", "کاهش آب"]
    },
    {
        "id": 4,
        "title": "آبیاری قطره‌ای",
        "summary": "سیستم آبیاری قطره‌ای آب را مستقیماً به ریشه گیاه می‌رساند و از هدررفت آب جلوگیری می‌کند.",
        "keywords": ["قطره‌ای", "ریشه", "هدررفت", "کارایی"]
    },
    {
        "id": 5,
        "title": "مدیریت خاک",
        "summary": "افزودن مواد آلی به خاک باعث بهبود ظرفیت نگهداری آب و کاهش نیاز به آبیاری می‌شود.",
        "keywords": ["خاک", "مواد آلی", "نگهداری آب", "کود"]
    },
    {
        "id": 6,
        "title": "چرخش محصولات",
        "summary": "چرخش محصولات با گیاهان کم‌آب می‌تواند فشار بر منابع آبی را کاهش دهد.",
        "keywords": ["چرخش", "محصولات", "کم‌آب", "منابع"]
    },
    {
        "id": 7,
        "title": "نظارت بر رطوبت خاک",
        "summary": "استفاده از رطوبت‌سنج یا روش‌های ساده برای بررسی رطوبت خاک قبل از آبیاری از آبیاری غیرضروری جلوگیری می‌کند.",
        "keywords": ["رطوبت", "خاک", "نظارت", "آبیاری"]
    },
    {
        "id": 8,
        "title": "کاشت در تراکم مناسب",
        "summary": "کاشت با تراکم مناسب باعث استفاده بهینه از آب و کاهش رقابت بین گیاهان می‌شود.",
        "keywords": ["تراکم", "کاشت", "بهینه", "رقابت"]
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
        "sources": ["AabSmart Farmer Knowledge Base"]
    }

