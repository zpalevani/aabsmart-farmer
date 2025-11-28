#!/usr/bin/env python3
"""
Demo script for AabSmart Farmer system.
Run this to see the system in action.
"""

from aabsmart import run_turn, run_golden
from aabsmart.gemini_client import initialize_gemini


def main():
    """Run demo examples."""
    print("="*80)
    print("AabSmart Farmer - Demo")
    print("="*80)
    
    # Initialize Gemini API
    try:
        initialize_gemini()
        print("✓ Gemini API initialized successfully\n")
    except Exception as e:
        print(f"✗ Error initializing Gemini API: {e}")
        print("\nPlease set your API key:")
        print("  export GEMINI_API_KEY='your-api-key'")
        return
    
    # Example 1: Persian query
    print("\n" + "="*80)
    print("Example 1: Persian Farmer Query")
    print("="*80)
    result1 = run_turn(
        farmer_id="farmer_001",
        user_message="سلام. من ۵ هکتار زمین دارم و گندم و جو می‌کارم. آب محدود است و از آبیاری غرقابی استفاده می‌کنم."
    )
    
    # Example 2: English query
    print("\n" + "="*80)
    print("Example 2: English Query with High-Water Crops")
    print("="*80)
    result2 = run_turn(
        farmer_id="farmer_002",
        user_message="I have 3 hectares with rice and tomato. Water is very limited. I'm using flood irrigation."
    )
    
    # Example 3: Drip irrigation
    print("\n" + "="*80)
    print("Example 3: Drip Irrigation Farmer")
    print("="*80)
    result3 = run_turn(
        farmer_id="farmer_003",
        user_message="من در اصفهان هستم. ۴ هکتار زمین دارم. پسته و گوجه فرنگی می‌کارم. آبیاری قطره‌ای استفاده می‌کنم."
    )
    
    print("\n" + "="*80)
    print("Demo completed!")
    print("="*80)


if __name__ == "__main__":
    main()

