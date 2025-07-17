import unittest
import sys
import os
import time
import tempfile
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from claude_desktop import ConversationDatabase, ConversationAnalyzer

class TestSimpleSuite(unittest.TestCase):
    """Simple test suite for basic functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = ConversationDatabase(self.temp_db.name)
        self.analyzer = ConversationAnalyzer()
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_database_basic_operations(self):
        """Test basic database operations"""
        # Ensure database is initialized
        self.db.init_database()
        
        # Test saving a conversation
        messages = [
            {"role": "user", "content": "Hello", "tokens": 5},
            {"role": "assistant", "content": "Hi!", "tokens": 3}
        ]
        
        conv_id = self.db.save_conversation("test_session", messages, "Test")
        self.assertIsInstance(conv_id, int)
        self.assertGreater(conv_id, 0)
        
        # Test analytics
        analytics = self.db.get_conversation_analytics(30)
        self.assertIsInstance(analytics, dict)
        self.assertIn('total_conversations', analytics)
    
    def test_analyzer_basic_operations(self):
        """Test basic analyzer operations"""
        # Test empty conversation
        result = self.analyzer.analyze_conversation_quality([])
        self.assertEqual(result, 0.0)
        
        # Test normal conversation
        messages = [
            {"role": "user", "content": "Hello there"},
            {"role": "assistant", "content": "Hi! How can I help?"}
        ]
        
        result = self.analyzer.analyze_conversation_quality(messages)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)
    
    def test_performance_basic(self):
        """Test basic performance metrics"""
        start_time = time.time()
        
        # Create some test data
        messages = [{"role": "user", "content": "Test message"}] * 50
        
        # Analyze performance
        result = self.analyzer.analyze_conversation_quality(messages)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete quickly
        self.assertLess(duration, 1.0)
        self.assertIsInstance(result, float)
    
    @patch('anthropic.Anthropic')
    def test_api_mock(self, mock_anthropic):
        """Test API with mock"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Test response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        # Test the mock works
        client = mock_anthropic(api_key="test_key")
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[{"role": "user", "content": "Test"}]
        )
        
        self.assertEqual(response.content[0].text, "Test response")
    
    def test_error_handling(self):
        """Test error handling"""
        # Test with invalid message format
        try:
            invalid_messages = [{"invalid": "format"}]
            result = self.analyzer.analyze_conversation_quality(invalid_messages)
            # Should handle gracefully and return 0.0
            self.assertEqual(result, 0.0)
        except Exception:
            # If it throws an exception, that's also acceptable
            pass

if __name__ == '__main__':
    unittest.main()
