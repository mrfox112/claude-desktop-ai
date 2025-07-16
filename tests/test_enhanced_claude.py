import unittest
import tempfile
import os
import json
import sqlite3
from unittest.mock import Mock, patch, MagicMock
import sys
from datetime import datetime, timedelta

# Add parent directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from claude_desktop_enhanced_v2 import (
    ConversationDatabase, 
    ConversationAnalyzer, 
    ConfigurationManager
)

class TestConversationDatabase(unittest.TestCase):
    """Test cases for ConversationDatabase class"""
    
    def setUp(self):
        """Set up test database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = ConversationDatabase(self.temp_db.name)
        
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_database_initialization(self):
        """Test database tables are created correctly"""
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['conversations', 'messages', 'analytics', 'user_preferences']
        for table in expected_tables:
            self.assertIn(table, tables)
        
        conn.close()
    
    def test_save_conversation(self):
        """Test saving a conversation"""
        session_id = "test_session_123"
        messages = [
            {"role": "user", "content": "Hello", "tokens": 5, "response_time": 0.1},
            {"role": "assistant", "content": "Hi there!", "tokens": 10, "response_time": 1.2, "quality_score": 0.85}
        ]
        
        conversation_id = self.db.save_conversation(session_id, messages, "Test conversation")
        
        # Verify conversation was saved
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM conversations WHERE id = ?", (conversation_id,))
        conversation = cursor.fetchone()
        
        self.assertIsNotNone(conversation)
        self.assertEqual(conversation[1], session_id)  # session_id
        self.assertEqual(conversation[3], "Test conversation")  # title
        self.assertEqual(conversation[5], 2)  # total_messages
        self.assertEqual(conversation[6], 15)  # total_tokens
        
        # Verify messages were saved
        cursor.execute("SELECT * FROM messages WHERE conversation_id = ?", (conversation_id,))
        saved_messages = cursor.fetchall()
        
        self.assertEqual(len(saved_messages), 2)
        self.assertEqual(saved_messages[0][2], "user")  # role
        self.assertEqual(saved_messages[0][3], "Hello")  # content
        self.assertEqual(saved_messages[1][2], "assistant")  # role
        self.assertEqual(saved_messages[1][3], "Hi there!")  # content
        
        conn.close()
    
    def test_get_conversation_analytics(self):
        """Test getting conversation analytics"""
        # Create test data
        session_id = "test_session_456"
        messages = [
            {"role": "user", "content": "Test message", "tokens": 5},
            {"role": "assistant", "content": "Test response", "tokens": 8, "quality_score": 0.9}
        ]
        
        self.db.save_conversation(session_id, messages, "Test conversation")
        
        analytics = self.db.get_conversation_analytics(30)
        
        self.assertEqual(analytics['total_conversations'], 1)
        self.assertEqual(analytics['total_messages'], 2)
        self.assertEqual(analytics['avg_quality'], 0.0)  # Only conversations have quality scores in current implementation

class TestConversationAnalyzer(unittest.TestCase):
    """Test cases for ConversationAnalyzer class"""
    
    def setUp(self):
        """Set up analyzer"""
        self.analyzer = ConversationAnalyzer()
    
    def test_identify_topic(self):
        """Test topic identification"""
        test_cases = [
            ("Let's write some Python code", "coding"),
            ("Can you help me write an essay?", "writing"),
            ("Please analyze this data", "analysis"),
            ("I need a creative story idea", "creative"),
            ("Design a technical system", "technical"),
            ("Just a general question", "general")
        ]
        
        for content, expected_topic in test_cases:
            with self.subTest(content=content):
                topic = self.analyzer.identify_topic(content)
                self.assertEqual(topic, expected_topic)
    
    def test_analyze_conversation_quality(self):
        """Test conversation quality analysis"""
        # Test empty conversation
        self.assertEqual(self.analyzer.analyze_conversation_quality([]), 0.0)
        
        # Test good conversation
        good_conversation = [
            {"role": "user", "content": "Hello! Can you help me write a Python function?"},
            {"role": "assistant", "content": "Of course! I'd be happy to help you write a Python function. What would you like the function to do?"},
            {"role": "user", "content": "I need a function that calculates the fibonacci sequence"},
            {"role": "assistant", "content": "Here's a Python function to calculate fibonacci numbers: def fibonacci(n): if n <= 1: return n else: return fibonacci(n-1) + fibonacci(n-2)"}
        ]
        
        quality_score = self.analyzer.analyze_conversation_quality(good_conversation)
        self.assertGreater(quality_score, 0.0)
        self.assertLessEqual(quality_score, 1.0)
    
    def test_calculate_flow_score(self):
        """Test conversation flow scoring"""
        # Perfect alternation
        perfect_flow = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "How are you?"},
            {"role": "assistant", "content": "I'm fine"}
        ]
        
        flow_score = self.analyzer._calculate_flow_score(perfect_flow)
        self.assertEqual(flow_score, 1.0)
        
        # Poor alternation
        poor_flow = [
            {"role": "user", "content": "Hello"},
            {"role": "user", "content": "Are you there?"},
            {"role": "assistant", "content": "Yes, I'm here"}
        ]
        
        flow_score = self.analyzer._calculate_flow_score(poor_flow)
        self.assertLess(flow_score, 1.0)
    
    def test_generate_conversation_summary(self):
        """Test conversation summary generation"""
        conversation = [
            {"role": "user", "content": "Help me write some Python code for data analysis"},
            {"role": "assistant", "content": "I'd be happy to help with Python data analysis code!"}
        ]
        
        summary = self.analyzer.generate_conversation_summary(conversation)
        self.assertIn("Coding discussion", summary)
        self.assertIn("Help me write some Python code", summary)
        
        # Test empty conversation
        empty_summary = self.analyzer.generate_conversation_summary([])
        self.assertEqual(empty_summary, "Empty conversation")

class TestConfigurationManager(unittest.TestCase):
    """Test cases for ConfigurationManager class"""
    
    def setUp(self):
        """Set up configuration manager"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = ConversationDatabase(self.temp_db.name)
        self.config = ConfigurationManager(self.db)
    
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_default_configuration(self):
        """Test default configuration values"""
        self.assertEqual(self.config.get('model'), 'claude-3-5-sonnet-20241022')
        self.assertEqual(self.config.get('max_tokens'), 1000)
        self.assertEqual(self.config.get('temperature'), 0.7)
        self.assertEqual(self.config.get('window_width'), 800)
        self.assertEqual(self.config.get('window_height'), 600)
        self.assertEqual(self.config.get('theme'), 'light')
        self.assertTrue(self.config.get('auto_save'))
        self.assertEqual(self.config.get('export_format'), 'json')
    
    def test_set_and_get_configuration(self):
        """Test setting and getting configuration values"""
        # Test setting string value
        self.config.set('model', 'claude-3-haiku-20240307')
        self.assertEqual(self.config.get('model'), 'claude-3-haiku-20240307')
        
        # Test setting numeric value
        self.config.set('max_tokens', 2000)
        self.assertEqual(self.config.get('max_tokens'), 2000)
        
        # Test setting boolean value
        self.config.set('auto_save', False)
        self.assertFalse(self.config.get('auto_save'))
        
        # Test persistence
        new_config = ConfigurationManager(self.db)
        self.assertEqual(new_config.get('model'), 'claude-3-haiku-20240307')
        self.assertEqual(new_config.get('max_tokens'), 2000)
        self.assertFalse(new_config.get('auto_save'))
    
    def test_get_with_default(self):
        """Test getting configuration with default values"""
        self.assertEqual(self.config.get('nonexistent_key', 'default_value'), 'default_value')
        self.assertIsNone(self.config.get('nonexistent_key'))

class TestIntegration(unittest.TestCase):
    """Integration tests for the enhanced application"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = ConversationDatabase(self.temp_db.name)
        self.analyzer = ConversationAnalyzer()
        self.config = ConfigurationManager(self.db)
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_full_conversation_workflow(self):
        """Test complete conversation workflow"""
        # Create a conversation
        session_id = "integration_test_session"
        messages = [
            {"role": "user", "content": "Hello, can you help me with Python programming?"},
            {"role": "assistant", "content": "Absolutely! I'd be happy to help you with Python programming. What specific topic or problem would you like to work on?"},
            {"role": "user", "content": "I need to create a function that processes a list of numbers"},
            {"role": "assistant", "content": "Here's a simple example of a function that processes a list of numbers: def process_numbers(numbers): return [x * 2 for x in numbers if x > 0]"}
        ]
        
        # Add timestamps and quality scores
        for i, msg in enumerate(messages):
            msg['timestamp'] = datetime.now().isoformat()
            msg['tokens'] = len(msg['content'].split())
            msg['response_time'] = 0.5 + i * 0.3
            if msg['role'] == 'assistant':
                msg['quality_score'] = self.analyzer.analyze_conversation_quality([msg])
        
        # Analyze conversation
        quality_score = self.analyzer.analyze_conversation_quality(messages)
        summary = self.analyzer.generate_conversation_summary(messages)
        topic = self.analyzer.identify_topic(messages[0]['content'])
        
        # Save conversation
        conversation_id = self.db.save_conversation(session_id, messages, summary)
        
        # Verify results
        self.assertIsNotNone(conversation_id)
        self.assertGreater(quality_score, 0.0)
        self.assertIn("Python", summary)
        self.assertEqual(topic, "coding")
        
        # Check analytics
        analytics = self.db.get_conversation_analytics(30)
        self.assertEqual(analytics['total_conversations'], 1)
        self.assertEqual(analytics['total_messages'], 4)
    
    def test_configuration_persistence(self):
        """Test configuration persistence across sessions"""
        # Set configuration
        self.config.set('model', 'claude-3-haiku-20240307')
        self.config.set('max_tokens', 1500)
        self.config.set('temperature', 0.8)
        self.config.set('auto_save', False)
        
        # Create new configuration manager (simulating app restart)
        new_config = ConfigurationManager(self.db)
        
        # Verify persistence
        self.assertEqual(new_config.get('model'), 'claude-3-haiku-20240307')
        self.assertEqual(new_config.get('max_tokens'), 1500)
        self.assertEqual(new_config.get('temperature'), 0.8)
        self.assertFalse(new_config.get('auto_save'))
    
    def test_export_import_functionality(self):
        """Test conversation export functionality"""
        # Create test conversation
        session_id = "export_test_session"
        messages = [
            {"role": "user", "content": "Test export functionality"},
            {"role": "assistant", "content": "This is a test response for export"}
        ]
        
        # Add required metadata
        for msg in messages:
            msg['timestamp'] = datetime.now().isoformat()
            msg['tokens'] = len(msg['content'].split())
            msg['response_time'] = 1.0
            if msg['role'] == 'assistant':
                msg['quality_score'] = 0.8
        
        # Create export data structure
        export_data = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'conversation': messages,
            'analytics': {
                'total_messages': len(messages),
                'quality_score': self.analyzer.analyze_conversation_quality(messages),
                'summary': self.analyzer.generate_conversation_summary(messages)
            }
        }
        
        # Test JSON serialization
        json_data = json.dumps(export_data, indent=2)
        self.assertIsInstance(json_data, str)
        
        # Test deserialization
        imported_data = json.loads(json_data)
        self.assertEqual(imported_data['session_id'], session_id)
        self.assertEqual(len(imported_data['conversation']), 2)
        self.assertIn('analytics', imported_data)

class TestPerformance(unittest.TestCase):
    """Performance tests for the enhanced application"""
    
    def setUp(self):
        """Set up performance test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = ConversationDatabase(self.temp_db.name)
        self.analyzer = ConversationAnalyzer()
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_large_conversation_analysis(self):
        """Test performance with large conversations"""
        # Create a large conversation
        large_conversation = []
        for i in range(100):
            large_conversation.append({
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"This is message number {i} in a large conversation for performance testing."
            })
        
        # Measure analysis time
        start_time = datetime.now()
        quality_score = self.analyzer.analyze_conversation_quality(large_conversation)
        end_time = datetime.now()
        
        analysis_time = (end_time - start_time).total_seconds()
        
        # Verify results
        self.assertGreater(quality_score, 0.0)
        self.assertLess(analysis_time, 1.0)  # Should complete within 1 second
    
    def test_database_performance(self):
        """Test database performance with multiple conversations"""
        # Create multiple conversations
        start_time = datetime.now()
        
        for i in range(10):
            session_id = f"perf_test_session_{i}"
            messages = [
                {"role": "user", "content": f"Test message {i}"},
                {"role": "assistant", "content": f"Test response {i}"}
            ]
            self.db.save_conversation(session_id, messages, f"Test conversation {i}")
        
        end_time = datetime.now()
        save_time = (end_time - start_time).total_seconds()
        
        # Verify performance
        self.assertLess(save_time, 2.0)  # Should complete within 2 seconds
        
        # Test analytics performance
        start_time = datetime.now()
        analytics = self.db.get_conversation_analytics(30)
        end_time = datetime.now()
        
        analytics_time = (end_time - start_time).total_seconds()
        
        # Verify results
        self.assertEqual(analytics['total_conversations'], 10)
        self.assertLess(analytics_time, 0.5)  # Should complete within 0.5 seconds

if __name__ == '__main__':
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(loader.loadTestsFromTestCase(TestConversationDatabase))
    suite.addTest(loader.loadTestsFromTestCase(TestConversationAnalyzer))
    suite.addTest(loader.loadTestsFromTestCase(TestConfigurationManager))
    suite.addTest(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTest(loader.loadTestsFromTestCase(TestPerformance))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    if result.testsRun > 0:
        print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")
