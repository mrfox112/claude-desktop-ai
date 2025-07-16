#!/usr/bin/env python3
"""
Debug version of the enhanced Claude Desktop application
Tests various features without GUI
"""

import os
import sys
import tempfile
from datetime import datetime
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from claude_desktop_enhanced_v2 import (
    ConversationDatabase,
    ConversationAnalyzer,
    ConfigurationManager
)

def test_database_functionality():
    """Test database creation and operations"""
    print("🔍 Testing Database Functionality")
    print("-" * 40)
    
    # Create temporary database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        db = ConversationDatabase(temp_db.name)
        print("✅ Database created successfully")
        
        # Test saving conversation
        session_id = "test_session_123"
        messages = [
            {"role": "user", "content": "Hello, Claude!", "tokens": 3, "response_time": 0.1},
            {"role": "assistant", "content": "Hello! How can I help you today?", "tokens": 8, "response_time": 1.2, "quality_score": 0.85}
        ]
        
        conversation_id = db.save_conversation(session_id, messages, "Test conversation")
        print(f"✅ Conversation saved with ID: {conversation_id}")
        
        # Test analytics
        analytics = db.get_conversation_analytics(30)
        print(f"✅ Analytics retrieved: {analytics}")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists(temp_db.name):
            os.unlink(temp_db.name)
    
    return True

def test_analyzer_functionality():
    """Test conversation analyzer"""
    print("\n🔍 Testing Analyzer Functionality")
    print("-" * 40)
    
    try:
        analyzer = ConversationAnalyzer()
        print("✅ Analyzer created successfully")
        
        # Test topic identification
        test_messages = [
            "Let's write some Python code for data analysis",
            "Can you help me write a creative story?",
            "Please analyze this research data",
            "I need help with a technical system design"
        ]
        
        for msg in test_messages:
            topic = analyzer.identify_topic(msg)
            print(f"✅ Topic identified: '{msg[:30]}...' -> {topic}")
        
        # Test conversation quality analysis
        conversation = [
            {"role": "user", "content": "Hello! Can you help me write a Python function?"},
            {"role": "assistant", "content": "Of course! I'd be happy to help you write a Python function. What would you like the function to do?"},
            {"role": "user", "content": "I need a function that calculates fibonacci numbers"},
            {"role": "assistant", "content": "Here's a Python function to calculate fibonacci numbers: def fibonacci(n): if n <= 1: return n else: return fibonacci(n-1) + fibonacci(n-2)"}
        ]
        
        quality_score = analyzer.analyze_conversation_quality(conversation)
        print(f"✅ Quality score calculated: {quality_score:.2f}")
        
        # Test summary generation
        summary = analyzer.generate_conversation_summary(conversation)
        print(f"✅ Summary generated: {summary}")
        
    except Exception as e:
        print(f"❌ Analyzer test failed: {e}")
        return False
    
    return True

def test_configuration_functionality():
    """Test configuration manager"""
    print("\n🔍 Testing Configuration Functionality")
    print("-" * 40)
    
    # Create temporary database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        db = ConversationDatabase(temp_db.name)
        config = ConfigurationManager(db)
        print("✅ Configuration manager created successfully")
        
        # Test default values
        print(f"✅ Default model: {config.get('model')}")
        print(f"✅ Default temperature: {config.get('temperature')}")
        print(f"✅ Default max_tokens: {config.get('max_tokens')}")
        
        # Test setting and getting values
        config.set('model', 'claude-3-haiku-20240307')
        config.set('temperature', 0.8)
        config.set('max_tokens', 1500)
        
        print(f"✅ Updated model: {config.get('model')}")
        print(f"✅ Updated temperature: {config.get('temperature')}")
        print(f"✅ Updated max_tokens: {config.get('max_tokens')}")
        
        # Test persistence
        new_config = ConfigurationManager(db)
        print(f"✅ Persisted model: {new_config.get('model')}")
        print(f"✅ Persisted temperature: {new_config.get('temperature')}")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists(temp_db.name):
            os.unlink(temp_db.name)
    
    return True

def test_mode_parameters():
    """Test mode parameter functionality"""
    print("\n🔍 Testing Mode Parameters")
    print("-" * 40)
    
    try:
        # Simulate mode parameter generation
        modes = ["balanced", "creative", "analytical", "coding", "writing"]
        
        for mode in modes:
            # Simulate get_mode_parameters logic
            base_params = {
                'model': 'claude-3-5-sonnet-20241022',
                'max_tokens': 1000,
            }
            
            if mode == "creative":
                base_params['temperature'] = 0.9
            elif mode == "analytical":
                base_params['temperature'] = 0.3
            elif mode == "coding":
                base_params['temperature'] = 0.1
                base_params['max_tokens'] = 2000
            elif mode == "writing":
                base_params['temperature'] = 0.8
                base_params['max_tokens'] = 3000
            else:  # balanced
                base_params['temperature'] = 0.7
            
            print(f"✅ Mode '{mode}': temp={base_params['temperature']}, tokens={base_params['max_tokens']}")
        
    except Exception as e:
        print(f"❌ Mode parameter test failed: {e}")
        return False
    
    return True

def test_export_functionality():
    """Test conversation export functionality"""
    print("\n🔍 Testing Export Functionality")
    print("-" * 40)
    
    try:
        import json
        
        # Create mock conversation data
        session_id = "export_test_session"
        conversation = [
            {"role": "user", "content": "Test export functionality", "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": "This is a test response", "timestamp": datetime.now().isoformat(), "quality_score": 0.8}
        ]
        
        analyzer = ConversationAnalyzer()
        
        export_data = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'conversation': conversation,
            'analytics': {
                'total_messages': len(conversation),
                'quality_score': analyzer.analyze_conversation_quality(conversation),
                'summary': analyzer.generate_conversation_summary(conversation)
            }
        }
        
        # Test JSON serialization
        json_str = json.dumps(export_data, indent=2)
        print(f"✅ JSON export successful: {len(json_str)} characters")
        
        # Test deserialization
        imported_data = json.loads(json_str)
        print(f"✅ JSON import successful: {len(imported_data['conversation'])} messages")
        
    except Exception as e:
        print(f"❌ Export test failed: {e}")
        return False
    
    return True

def test_performance():
    """Test performance with larger datasets"""
    print("\n🔍 Testing Performance")
    print("-" * 40)
    
    try:
        analyzer = ConversationAnalyzer()
        
        # Create large conversation
        large_conversation = []
        for i in range(100):
            large_conversation.append({
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"This is message number {i} in a large conversation for performance testing."
            })
        
        start_time = datetime.now()
        quality_score = analyzer.analyze_conversation_quality(large_conversation)
        end_time = datetime.now()
        
        analysis_time = (end_time - start_time).total_seconds()
        print(f"✅ Large conversation analysis: {analysis_time:.3f}s, quality: {quality_score:.3f}")
        
        # Test database performance
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        db = ConversationDatabase(temp_db.name)
        
        start_time = datetime.now()
        for i in range(10):
            session_id = f"perf_test_{i}"
            messages = [
                {"role": "user", "content": f"Test message {i}"},
                {"role": "assistant", "content": f"Test response {i}"}
            ]
            db.save_conversation(session_id, messages, f"Test conversation {i}")
        
        end_time = datetime.now()
        save_time = (end_time - start_time).total_seconds()
        print(f"✅ Database performance: {save_time:.3f}s for 10 conversations")
        
        # Clean up
        if os.path.exists(temp_db.name):
            os.unlink(temp_db.name)
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Enhanced Claude Desktop - Debug Test Suite")
    print("=" * 50)
    
    load_dotenv()
    
    tests = [
        test_database_functionality,
        test_analyzer_functionality,
        test_configuration_functionality,
        test_mode_parameters,
        test_export_functionality,
        test_performance
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print(f"🎯 Success rate: {(passed / (passed + failed) * 100):.1f}%")
    
    if failed == 0:
        print("✅ All tests passed! The enhanced application is ready.")
    else:
        print("❌ Some tests failed. Please check the output above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
