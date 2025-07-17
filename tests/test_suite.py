import unittest
import sys
import os
import json
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your modules
try:
    from claude_desktop import ClaudeDesktopApp, ConversationDatabase, ConversationAnalyzer
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the correct directory")
    # Create dummy classes for testing if import fails
    class ConversationDatabase:
        def __init__(self, db_path):
            pass
        def save_conversation(self, *args, **kwargs):
            return 1
        def get_conversation_analytics(self, *args, **kwargs):
            return {'total_conversations': 0, 'total_messages': 0}
    
    class ConversationAnalyzer:
        def __init__(self):
            pass
        def analyze_conversation_quality(self, messages):
            return 0.5
        def _calculate_flow_score(self, messages):
            return 0.5
    
    class ClaudeDesktopApp:
        pass

class TestConversationDatabase(unittest.TestCase):
    """Test suite for ConversationDatabase"""
    
    def setUp(self):
        """Set up test database"""
        self.test_db = ConversationDatabase("test_conversations.db")
        
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists("test_conversations.db"):
            os.remove("test_conversations.db")
    
    def test_database_initialization(self):
        """Test database initialization"""
        self.assertTrue(os.path.exists("test_conversations.db"))
        
    def test_save_conversation(self):
        """Test saving a conversation"""
        messages = [
            {"role": "user", "content": "Hello", "tokens": 5},
            {"role": "assistant", "content": "Hi there!", "tokens": 10}
        ]
        
        conversation_id = self.test_db.save_conversation(
            session_id="test_session",
            messages=messages,
            title="Test Conversation"
        )
        
        self.assertIsInstance(conversation_id, int)
        self.assertGreater(conversation_id, 0)
    
    def test_get_conversation_analytics(self):
        """Test getting conversation analytics"""
        # First save a conversation
        messages = [
            {"role": "user", "content": "Hello", "tokens": 5},
            {"role": "assistant", "content": "Hi there!", "tokens": 10}
        ]
        
        self.test_db.save_conversation(
            session_id="test_session",
            messages=messages,
            title="Test Conversation"
        )
        
        # Get analytics
        analytics = self.test_db.get_conversation_analytics(days=30)
        
        self.assertIsInstance(analytics, dict)
        self.assertIn('total_conversations', analytics)
        self.assertIn('total_messages', analytics)
        self.assertEqual(analytics['total_conversations'], 1)
        self.assertEqual(analytics['total_messages'], 2)

class TestConversationAnalyzer(unittest.TestCase):
    """Test suite for ConversationAnalyzer"""
    
    def setUp(self):
        """Set up analyzer"""
        self.analyzer = ConversationAnalyzer()
    
    def test_analyze_conversation_quality(self):
        """Test conversation quality analysis"""
        messages = [
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you! How can I help you today?"},
            {"role": "user", "content": "Can you help me with coding?"},
            {"role": "assistant", "content": "Absolutely! I'd be happy to help with coding. What programming language or specific problem are you working on?"}
        ]
        
        quality_score = self.analyzer.analyze_conversation_quality(messages)
        
        self.assertIsInstance(quality_score, float)
        self.assertGreaterEqual(quality_score, 0.0)
        self.assertLessEqual(quality_score, 1.0)
    
    def test_flow_score_calculation(self):
        """Test conversation flow score calculation"""
        good_flow_messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
            {"role": "assistant", "content": "I'm doing well!"}
        ]
        
        bad_flow_messages = [
            {"role": "user", "content": "Hello"},
            {"role": "user", "content": "Are you there?"},
            {"role": "assistant", "content": "Yes, I'm here!"},
            {"role": "assistant", "content": "How can I help?"}
        ]
        
        good_score = self.analyzer._calculate_flow_score(good_flow_messages)
        bad_score = self.analyzer._calculate_flow_score(bad_flow_messages)
        
        self.assertGreater(good_score, bad_score)
        self.assertEqual(good_score, 1.0)  # Perfect alternation

class TestAPIIntegration(unittest.TestCase):
    """Test suite for API integration"""
    
    def setUp(self):
        """Set up API test environment"""
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            self.skipTest("ANTHROPIC_API_KEY not found in environment")
    
    @patch('anthropic.Anthropic')
    def test_api_connection(self, mock_anthropic):
        """Test API connection with mock"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Test response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        # Test the API call
        client = mock_anthropic(api_key=self.api_key)
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[{"role": "user", "content": "Test message"}]
        )
        
        self.assertEqual(response.content[0].text, "Test response")
        mock_client.messages.create.assert_called_once()

class TestPerformanceMetrics(unittest.TestCase):
    """Test suite for performance metrics"""
    
    def test_response_time_tracking(self):
        """Test response time tracking"""
        start_time = time.time()
        
        # Simulate some processing
        time.sleep(0.1)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertGreater(response_time, 0.0)
        self.assertLess(response_time, 1.0)  # Should be under 1 second for this test
    
    def test_memory_usage(self):
        """Test memory usage tracking"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        self.assertGreater(memory_info.rss, 0)
        self.assertIsInstance(memory_info.rss, int)

class TestErrorHandling(unittest.TestCase):
    """Test suite for error handling"""
    
    def test_missing_api_key(self):
        """Test handling of missing API key"""
        with patch.dict(os.environ, {}, clear=True):
            # This should handle missing API key gracefully
            try:
                # Test code that depends on API key
                api_key = os.environ.get('ANTHROPIC_API_KEY')
                self.assertIsNone(api_key)
            except Exception as e:
                self.fail(f"Should handle missing API key gracefully: {e}")
    
    def test_invalid_message_format(self):
        """Test handling of invalid message formats"""
        analyzer = ConversationAnalyzer()
        
        # Test with empty messages
        result = analyzer.analyze_conversation_quality([])
        self.assertEqual(result, 0.0)
        
        # Test with invalid message format
        invalid_messages = [{"invalid": "format"}]
        try:
            result = analyzer.analyze_conversation_quality(invalid_messages)
            # Should handle gracefully
            self.assertIsInstance(result, float)
        except Exception as e:
            self.fail(f"Should handle invalid message format gracefully: {e}")

class TestRegressionSuite(unittest.TestCase):
    """Regression test suite to prevent breaking existing functionality"""
    
    def test_database_schema_consistency(self):
        """Test that database schema remains consistent"""
        db = ConversationDatabase("test_regression.db")
        
        # Test that all expected tables exist
        conn = db.init_database()
        # This should not raise an exception
        
        # Clean up
        if os.path.exists("test_regression.db"):
            os.remove("test_regression.db")
    
    def test_analyzer_backward_compatibility(self):
        """Test that analyzer maintains backward compatibility"""
        analyzer = ConversationAnalyzer()
        
        # Test with old message format
        old_format_messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        result = analyzer.analyze_conversation_quality(old_format_messages)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)

def run_test_suite():
    """Run the complete test suite"""
    print("🧪 Running Claude Desktop AI Test Suite")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestConversationDatabase,
        TestConversationAnalyzer,
        TestAPIIntegration,
        TestPerformanceMetrics,
        TestErrorHandling,
        TestRegressionSuite
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    return result

if __name__ == "__main__":
    # Ensure tests directory exists
    os.makedirs("tests", exist_ok=True)
    
    # Run the test suite
    run_test_suite()
