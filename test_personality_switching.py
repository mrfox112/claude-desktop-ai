#!/usr/bin/env python3
"""
Test script for automatic personality switching functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from claude_desktop import PersonalitySystem, ConversationDatabase
from datetime import datetime
import random

def test_personality_switching():
    """Test the automatic personality switching with various scenarios"""
    
    # Initialize systems
    personality_system = PersonalitySystem()
    db = ConversationDatabase()
    
    print("🔬 Testing Automatic Personality Switching System")
    print("=" * 60)
    
    # Test cases with expected outcomes
    test_cases = [
        # Test case: Short message (should trigger Loyal Ether)
        {
            "message": "hi",
            "description": "Short message (< 10 chars)",
            "expected": "loyal_ether"
        },
        
        # Test case: Complex message with special characters (should trigger Rogue Ether)
        {
            "message": "What the hell is going on?!@#$%",
            "description": "High complexity with special characters",
            "expected": "rogue_ether"
        },
        
        # Test case: Multiple keywords (should trigger Rogue Ether)
        {
            "message": "I need help with an error, please help me protect my system from errors",
            "description": "Multiple trigger keywords (error, help, protect)",
            "expected": "rogue_ether"
        },
        
        # Test case: Aggressive tone (should trigger Rogue Ether)
        {
            "message": "I'm really frustrated and angry with this system",
            "description": "Aggressive tone detection",
            "expected": "rogue_ether"
        },
        
        # Test case: Polite tone (neutral)
        {
            "message": "Thank you for your help, I really appreciate it",
            "description": "Polite tone (neutral case)",
            "expected": "random"  # Could be either
        },
        
        # Test case: Normal message (neutral)
        {
            "message": "Can you explain how machine learning works?",
            "description": "Normal neutral message",
            "expected": "random"  # Could be either
        },
        
        # Test case: Time-based switching (simulate evening)
        {
            "message": "Good evening, how are you?",
            "description": "Evening time check (if after 6 PM)",
            "expected": "depends_on_time"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_case['description']}")
        print(f"   Input: '{test_case['message']}'")
        
        # Record initial personality
        initial_personality = personality_system.current_personality
        
        # Run the switching logic
        try:
            switch_result = personality_system.switch_personality_based_on_factors(
                test_case['message'], db
            )
            
            final_personality = personality_system.current_personality
            
            # Analyze the result
            if test_case['expected'] == "random":
                result = "✅ PASS" if final_personality in ['loyal_ether', 'rogue_ether'] else "❌ FAIL"
            elif test_case['expected'] == "depends_on_time":
                current_hour = datetime.now().hour
                if current_hour >= 18:
                    result = "✅ PASS" if final_personality == 'rogue_ether' else "❌ FAIL"
                else:
                    result = "✅ PASS" if final_personality in ['loyal_ether', 'rogue_ether'] else "❌ FAIL"
            else:
                result = "✅ PASS" if final_personality == test_case['expected'] else "❌ FAIL"
            
            print(f"   Result: {initial_personality} → {final_personality}")
            print(f"   Status: {result}")
            
            results.append({
                "test": test_case['description'],
                "passed": "✅" in result,
                "personality": final_personality
            })
            
        except Exception as e:
            print(f"   Status: ❌ ERROR - {str(e)}")
            results.append({
                "test": test_case['description'],
                "passed": False,
                "personality": "ERROR"
            })
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed! Automatic personality switching is working correctly.")
    else:
        print("⚠️  Some tests failed. Review the implementation.")
    
    return results

def test_factor_analysis():
    """Test individual factor analysis components"""
    
    print("\n🔍 Testing Individual Factor Analysis")
    print("=" * 60)
    
    personality_system = PersonalitySystem()
    db = ConversationDatabase()
    
    # Test different message types
    test_messages = [
        "hello",
        "What the hell?!@#$%",
        "I need help with an error",
        "Thank you so much",
        "I'm frustrated and angry",
        "Can you explain quantum physics in detail?"
    ]
    
    for msg in test_messages:
        print(f"\n📝 Analyzing: '{msg}'")
        
        # Extract factors manually to show analysis
        factors = {
            "length": len(msg),
            "complexity": sum(1 for c in msg if c in "?!@#$%"),
            "keywords": sum(map(msg.lower().count, ["error", "help", "protect"])),
            "time_of_day": datetime.now().hour,
            "user_tone": personality_system._detect_tone(msg),
            "random": random.randint(0, 1),
            "network_status": personality_system._check_network(),
            "session_length": len(db.get_hourly_trends()) if db else 0,
            "recent_conversations": db.get_conversation_analytics()['total_conversations'] if db else 0,
            "user_activity": personality_system._detect_user_activity(),
        }
        
        print(f"   Length: {factors['length']}")
        print(f"   Complexity: {factors['complexity']}")
        print(f"   Keywords: {factors['keywords']}")
        print(f"   Time: {factors['time_of_day']}:00")
        print(f"   Tone: {factors['user_tone']}")
        print(f"   Network: {factors['network_status']}")
        
        # Run switching logic
        personality_system.switch_personality_based_on_factors(msg, db)
        print(f"   → Selected: {personality_system.current_personality}")

if __name__ == "__main__":
    try:
        # Run comprehensive tests
        results = test_personality_switching()
        
        # Run factor analysis
        test_factor_analysis()
        
        print("\n✅ Testing completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Testing failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
