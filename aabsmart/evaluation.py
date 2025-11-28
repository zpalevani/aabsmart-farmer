"""
Evaluation components for AabSmart Farmer system.
Includes golden test cases and optional LLM-as-judge critic.
"""

import json
from typing import Dict, List, Optional
from aabsmart.runner import run_turn
from aabsmart.memory import MEMORY, SESSION
from aabsmart.gemini_client import call_gemini


# Golden test cases
GOLDEN_TEST_CASES = [
    {
        "id": "test_1",
        "farmer_id": "farmer_001",
        "user_message": "سلام. من ۵ هکتار زمین دارم و گندم و جو می‌کارم. آب محدود است.",
        "expected_keywords": ["گندم", "جو", "آب"],
        "description": "Basic wheat and barley farmer with limited water"
    },
    {
        "id": "test_2",
        "farmer_id": "farmer_002",
        "user_message": "I have 3 hectares with rice and tomato. Water is low. Using flood irrigation.",
        "expected_keywords": ["rice", "tomato", "water"],
        "description": "High-water crops with flood irrigation"
    },
    {
        "id": "test_3",
        "farmer_id": "farmer_003",
        "user_message": "من در اصفهان هستم. پسته و گوجه فرنگی دارم. آبیاری قطره‌ای استفاده می‌کنم.",
        "expected_keywords": ["پسته", "گوجه فرنگی", "قطره"],
        "description": "Pistachio and tomato with drip irrigation"
    }
]


def run_golden() -> List[Dict]:
    """
    Run golden test cases and return results for inspection.
    
    Returns:
        List of test results
    """
    results = []
    
    print("\n" + "="*80)
    print("RUNNING GOLDEN TEST CASES")
    print("="*80 + "\n")
    
    for test_case in GOLDEN_TEST_CASES:
        print(f"\n{'='*80}")
        print(f"Test Case: {test_case['id']}")
        print(f"Description: {test_case['description']}")
        print(f"{'='*80}\n")
        
        # Clear memory for clean test
        if test_case['farmer_id'] in MEMORY.profiles:
            del MEMORY.profiles[test_case['farmer_id']]
        SESSION.clear_session(test_case['farmer_id'])
        
        # Run turn
        try:
            result = run_turn(
                farmer_id=test_case['farmer_id'],
                user_message=test_case['user_message']
            )
            
            # Check if expected keywords appear
            answer_lower = result['answer'].lower()
            keywords_found = []
            for keyword in test_case['expected_keywords']:
                if keyword.lower() in answer_lower or keyword in result['answer']:
                    keywords_found.append(keyword)
            
            test_result = {
                "test_id": test_case['id'],
                "passed": len(keywords_found) > 0,
                "keywords_found": keywords_found,
                "expected_keywords": test_case['expected_keywords'],
                "profile_extracted": result['profile'].main_crops is not None,
                "water_footprint_calculated": result['water_footprint']['total_water_m3'] > 0,
                "scenarios_generated": len(result['scenarios']['scenarios']) > 0,
                "answer_length": len(result['answer'])
            }
            
            results.append(test_result)
            
            print(f"\nTest Result: {'PASSED' if test_result['passed'] else 'FAILED'}")
            print(f"Keywords found: {keywords_found}")
            
        except Exception as e:
            print(f"ERROR in test case {test_case['id']}: {str(e)}")
            results.append({
                "test_id": test_case['id'],
                "passed": False,
                "error": str(e)
            })
    
    print("\n" + "="*80)
    print("GOLDEN TEST SUMMARY")
    print("="*80)
    for result in results:
        status = "✓" if result.get('passed', False) else "✗"
        print(f"{status} {result['test_id']}: {result.get('keywords_found', [])}")
    
    return results


def critic_agent(answer_a: str, answer_b: str, criteria: str = "water conservation advice quality") -> Dict:
    """
    LLM-as-judge critic comparing two answers.
    
    Args:
        answer_a: First answer to compare
        answer_b: Second answer to compare
        criteria: Evaluation criteria
    
    Returns:
        Dictionary with winner and reason
    """
    system_prompt = """You are an expert agricultural advisor evaluator. Compare two answers and determine which is better based on the given criteria.

Output ONLY valid JSON in this format:
{"winner": "A"|"B"|"tie", "reason": "brief explanation"}

Be objective and focus on practical agricultural advice quality."""
    
    user_prompt = f"""Compare these two agricultural advisory answers:

Answer A:
{answer_a}

Answer B:
{answer_b}

Criteria: {criteria}

Which answer is better? Output JSON only."""
    
    response = call_gemini(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.1
    )
    
    # Try to parse JSON from response
    try:
        # Extract JSON if wrapped in markdown
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0].strip()
        else:
            json_str = response.strip()
        
        result = json.loads(json_str)
        return result
    except:
        # Fallback if JSON parsing fails
        return {
            "winner": "tie",
            "reason": f"Could not parse response: {response[:100]}"
        }

