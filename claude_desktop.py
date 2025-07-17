import tkinter as tk
from tkinter import scrolledtext, messagebox, font, filedialog
import anthropic
import os
from dotenv import load_dotenv
import threading

from transformers import BertTokenizer, BertModel
import speech_recognition as sr
import pyttsx3
import json
import sqlite3
from datetime import datetime, timedelta
import time
import hashlib
import re
from collections import defaultdict
import logging
from typing import Dict, List, Optional, Tuple

import ttkbootstrap as ttkb
from ttkbootstrap.dialogs import Messagebox
try:
    from ttkbootstrap.tooltips import ToolTip
except ImportError:
    ToolTip = None  # Gracefully handle missing tooltips
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import intelligence enhancement system
try:
    from claude_intelligence import SmartClaudeProcessor
    INTELLIGENCE_AVAILABLE = True
except ImportError:
    INTELLIGENCE_AVAILABLE = False
    print("⚠️ Intelligence enhancement not available. Install missing dependencies.")

# Import advanced AI system
try:
    from advanced_ai_system import NextGenAISystem, AdvancedQuery
    ADVANCED_AI_AVAILABLE = True
except ImportError:
    ADVANCED_AI_AVAILABLE = False
    print("⚠️ Advanced AI system not available. Install missing dependencies.")

# Import model optimization system
try:
    from model_optimizer import OptimizationManager, ConversationQualityOptimizer, ResponseTimeOptimizer
    OPTIMIZATION_AVAILABLE = True
except ImportError:
    OPTIMIZATION_AVAILABLE = False
    print("⚠️ Model optimization not available. Install optuna and scikit-learn.")

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConversationDatabase:
    """Database handler for conversation storage and analytics"""
    
    def __init__(self, db_path: str = "conversations.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                title TEXT,
                summary TEXT,
                total_messages INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                duration_minutes REAL DEFAULT 0,
                quality_score REAL DEFAULT 0
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                tokens INTEGER DEFAULT 0,
                response_time REAL DEFAULT 0,
                quality_score REAL DEFAULT 0,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        ''')
        
        # Analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                total_conversations INTEGER DEFAULT 0,
                total_messages INTEGER DEFAULT 0,
                avg_response_time REAL DEFAULT 0,
                avg_quality_score REAL DEFAULT 0,
                most_common_topics TEXT
            )
        ''')
        
        # Real-time metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS realtime_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metric_type TEXT NOT NULL,
                metric_value REAL NOT NULL,
                session_id TEXT,
                message_id INTEGER
            )
        ''')
        
        # Trends table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                hour INTEGER NOT NULL,
                messages_count INTEGER DEFAULT 0,
                avg_response_time REAL DEFAULT 0,
                avg_quality_score REAL DEFAULT 0,
                active_sessions INTEGER DEFAULT 0,
                PRIMARY KEY (date, hour)
            ) WITHOUT ROWID
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                preference_key TEXT UNIQUE NOT NULL,
                preference_value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_conversation(self, session_id: str, messages: List[Dict], 
                         title: str = None, summary: str = None) -> int:
        """Save a conversation to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate conversation metrics
        total_messages = len(messages)
        total_tokens = sum(msg.get('tokens', 0) for msg in messages)
        duration_minutes = 0  # Calculate based on timestamps if available
        
        # Insert conversation
        cursor.execute('''
            INSERT INTO conversations (session_id, title, summary, total_messages, total_tokens, duration_minutes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, title, summary, total_messages, total_tokens, duration_minutes))
        
        conversation_id = cursor.lastrowid
        
        # Insert messages
        for msg in messages:
            cursor.execute('''
                INSERT INTO messages (conversation_id, role, content, tokens, response_time, quality_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (conversation_id, msg['role'], msg['content'], 
                  msg.get('tokens', 0), msg.get('response_time', 0), msg.get('quality_score', 0)))
        
        conn.commit()
        conn.close()
        return conversation_id
    
    def get_conversation_analytics(self, days: int = 30) -> Dict:
        """Get analytics for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_conversations,
                SUM(total_messages) as total_messages,
                AVG(quality_score) as avg_quality,
                AVG(duration_minutes) as avg_duration
            FROM conversations 
            WHERE timestamp >= ?
        ''', (start_date,))
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'total_conversations': result[0] or 0,
            'total_messages': result[1] or 0,
            'avg_quality': result[2] or 0,
            'avg_duration': result[3] or 0
        }
    
    def save_realtime_metric(self, metric_type: str, metric_value: float, 
                           session_id: str = None, message_id: int = None):
        """Save a real-time metric to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO realtime_metrics (metric_type, metric_value, session_id, message_id)
            VALUES (?, ?, ?, ?)
        ''', (metric_type, metric_value, session_id, message_id))
        
        conn.commit()
        conn.close()
    
    def get_realtime_metrics(self, hours: int = 24) -> Dict:
        """Get real-time metrics for the last N hours"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_time = datetime.now() - timedelta(hours=hours)
        
        # Get metrics grouped by type
        cursor.execute('''
            SELECT 
                metric_type,
                AVG(metric_value) as avg_value,
                COUNT(*) as count,
                MIN(metric_value) as min_value,
                MAX(metric_value) as max_value
            FROM realtime_metrics 
            WHERE timestamp >= ?
            GROUP BY metric_type
        ''', (start_time,))
        
        metrics = {}
        for row in cursor.fetchall():
            metrics[row[0]] = {
                'avg': row[1] or 0,
                'count': row[2] or 0,
                'min': row[3] or 0,
                'max': row[4] or 0
            }
        
        conn.close()
        return metrics
    
    def get_hourly_trends(self, days: int = 7) -> List[Dict]:
        """Get hourly trends for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT 
                DATE(timestamp) as date,
                strftime('%H', timestamp) as hour,
                COUNT(*) as message_count,
                AVG(response_time) as avg_response_time,
                AVG(quality_score) as avg_quality
            FROM messages 
            WHERE timestamp >= ?
            GROUP BY date, hour
            ORDER BY date, hour
        ''', (start_date,))
        
        trends = []
        for row in cursor.fetchall():
            trends.append({
                'date': row[0],
                'hour': int(row[1]),
                'message_count': row[2],
                'avg_response_time': row[3] or 0,
                'avg_quality': row[4] or 0
            })
        
        conn.close()
        return trends
    
    def get_topic_trends(self, days: int = 7) -> Dict:
        """Get topic trends for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT content, timestamp FROM messages 
            WHERE timestamp >= ? AND role = 'user'
            ORDER BY timestamp DESC
        ''', (start_date,))
        
        # This would need the analyzer to identify topics
        # For now, return placeholder data
        topics = {
            'coding': 25,
            'writing': 20,
            'analysis': 15,
            'creative': 10,
            'technical': 30
        }
        
        conn.close()
        return topics
    
    def update_trend_data(self, session_id: str):
        """Update hourly trend data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        hour = now.hour
        
        # Update or insert trend data
        cursor.execute('''
            INSERT OR REPLACE INTO trends (date, hour, messages_count, avg_response_time, avg_quality_score, active_sessions)
            VALUES (?, ?, 
                COALESCE((SELECT messages_count FROM trends WHERE date = ? AND hour = ?), 0) + 1,
                (SELECT AVG(response_time) FROM messages WHERE DATE(timestamp) = ? AND strftime('%H', timestamp) = ?),
                (SELECT AVG(quality_score) FROM messages WHERE DATE(timestamp) = ? AND strftime('%H', timestamp) = ?),
                (SELECT COUNT(DISTINCT session_id) FROM conversations WHERE DATE(timestamp) = ? AND strftime('%H', timestamp) = ?)
            )
        ''', (date_str, hour, date_str, str(hour).zfill(2), date_str, str(hour).zfill(2), 
              date_str, str(hour).zfill(2), date_str, str(hour).zfill(2)))
        
        conn.commit()
        conn.close()

class ConversationAnalyzer:
    """Analyzer for conversation quality and insights"""
    
    def __init__(self):
        self.topic_patterns = {
            'coding': ['code', 'programming', 'python', 'javascript', 'function', 'class', 'variable'],
            'writing': ['write', 'essay', 'article', 'content', 'draft', 'edit'],
            'analysis': ['analyze', 'data', 'research', 'study', 'report', 'statistics'],
            'creative': ['creative', 'story', 'poem', 'idea', 'brainstorm', 'imagine'],
            'technical': ['technical', 'system', 'architecture', 'design', 'implementation']
        }
    
    def analyze_conversation_quality(self, messages: List[Dict]) -> float:
        """Analyze conversation quality based on various metrics"""
        if not messages:
            return 0.0
        
        scores = []
        
# Length and engagement score
        try:
            avg_length = sum(len(msg['content']) for msg in messages) / len(messages)
            length_score = min(avg_length / 100, 1.0)  # Normalize to 0-1
            scores.append(length_score)
        except KeyError:
            return 0.0  # Handle invalid message format gracefully
        
        # Conversation flow score (alternating user/assistant)
        flow_score = self._calculate_flow_score(messages)
        scores.append(flow_score)
        
        # Topic coherence score
        coherence_score = self._calculate_coherence_score(messages)
        scores.append(coherence_score)
        
        return sum(scores) / len(scores)
    
    def _calculate_flow_score(self, messages: List[Dict]) -> float:
        """Calculate conversation flow score"""
        if len(messages) < 2:
            return 1.0
        
        proper_alternation = 0
        for i in range(1, len(messages)):
            if messages[i]['role'] != messages[i-1]['role']:
                proper_alternation += 1
        
        return proper_alternation / (len(messages) - 1)
    
    def _calculate_coherence_score(self, messages: List[Dict]) -> float:
        """Calculate topic coherence score"""
        if not messages:
            return 0.0
        
        # Simple coherence based on topic consistency
        topics = [self.identify_topic(msg['content']) for msg in messages]
        most_common_topic = max(set(topics), key=topics.count) if topics else None
        
        if most_common_topic:
            coherence = topics.count(most_common_topic) / len(topics)
            return coherence
        
        return 0.5  # Default score
    
    def identify_topic(self, content: str) -> str:
        """Identify the main topic of a message"""
        content_lower = content.lower()
        
        topic_scores = {}
        for topic, keywords in self.topic_patterns.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                topic_scores[topic] = score
        
        if topic_scores:
            return max(topic_scores, key=topic_scores.get)
        
        return 'general'
    
    def generate_conversation_summary(self, messages: List[Dict]) -> str:
        """Generate a summary of the conversation"""
        if not messages:
            return "Empty conversation"
        
        topics = [self.identify_topic(msg['content']) for msg in messages]
        main_topic = max(set(topics), key=topics.count) if topics else 'general'
        
        user_messages = [msg for msg in messages if msg['role'] == 'user']
        
        if user_messages:
            first_message = user_messages[0]['content'][:100] + "..." if len(user_messages[0]['content']) > 100 else user_messages[0]['content']
            return f"{main_topic.title()} discussion: {first_message}"
        
        return f"{main_topic.title()} conversation"

class ConfigurationManager:
    """Manager for application configuration and preferences"""
    
    def __init__(self, db: ConversationDatabase):
        self.db = db
        self.default_config = {
            'model': 'claude-3-5-sonnet-20241022',
            'max_tokens': 1000,
            'temperature': 0.7,
            'window_width': 800,
            'window_height': 600,
            'theme': 'light',
            'auto_save': True,
            'export_format': 'json'
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load configuration from database"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT preference_key, preference_value FROM user_preferences')
        prefs = dict(cursor.fetchall())
        conn.close()
        
        # Merge with defaults
        config = self.default_config.copy()
        for key, value in prefs.items():
            # Convert string values back to appropriate types
            if key in ['max_tokens', 'window_width', 'window_height']:
                config[key] = int(value)
            elif key in ['temperature']:
                config[key] = float(value)
            elif key in ['auto_save']:
                config[key] = value.lower() == 'true'
            else:
                config[key] = value
        
        return config
    
    def save_config(self):
        """Save configuration to database"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        for key, value in self.config.items():
            cursor.execute('''
                INSERT OR REPLACE INTO user_preferences (preference_key, preference_value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, str(value)))
        
        conn.commit()
        conn.close()
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """Set configuration value"""
        self.config[key] = value
        self.save_config()

    def show_visualization(self):
        """Display a sample data visualization"""
        vis_window = tk.Toplevel(self.root)
        vis_window.title("Data Visualization")
        vis_window.geometry("500x400")

        figure = Figure(figsize=(5, 4), dpi=100)
        ax = figure.add_subplot(111)
        ax.plot([0.1, 0.2, 0.3, 0.4], [10, 20, 25, 30], marker='o')
        ax.set_title("Sample Visualization")
        ax.set_xlabel("X Axis")
        ax.set_ylabel("Y Axis")

        canvas = FigureCanvasTkAgg(figure, master=vis_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)


class EnhancedClaudeDesktopApp:
    """Enhanced Claude Desktop Application with analytics and improved features"""
    
    def __init__(self, root):
        self.style = ttkb.Style(theme='cosmo')
        self.root = root
        self.root.title("Claude AI Desktop - Enhanced")
        
        # Load NLP model
        print("Loading BERT model...")
        self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.bert_model = BertModel.from_pretrained('bert-base-uncased')
        print("BERT model loaded successfully!")
        
        # Initialize speech recognition and synthesis
        print("Initializing speech systems...")
        self.init_speech_systems()

        # Initialize components
        self.db = ConversationDatabase()
        self.analyzer = ConversationAnalyzer()
        self.config = ConfigurationManager(self.db)
        
        # Initialize intelligence enhancement
        if INTELLIGENCE_AVAILABLE:
            self.intelligence = SmartClaudeProcessor()
            print("🧠 Intelligence enhancement loaded successfully!")
        else:
            self.intelligence = None
        
        # Initialize advanced AI system
        if ADVANCED_AI_AVAILABLE:
            self.advanced_ai = NextGenAISystem()
            print("🤖 Advanced AI system loaded successfully!")
        else:
            self.advanced_ai = None
        
        # Initialize model optimization system
        if OPTIMIZATION_AVAILABLE:
            self.optimization_manager = OptimizationManager(self.db.db_path)
            print("🔧 Model optimization system loaded successfully!")
        else:
            self.optimization_manager = None
        
        # Set window geometry from config
        width = self.config.get('window_width', 800)
        height = self.config.get('window_height', 600)
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(600, 400)
        
        # Initialize session
        self.session_id = self._generate_session_id()
        self.conversation = []
        self.conversation_start_time = datetime.now()
        
        # Initialize Anthropic client with security manager
        api_key_encrypted = os.environ.get('ENCRYPTED_ANTHROPIC_API_KEY')
        api_key_plain = os.environ.get('ANTHROPIC_API_KEY')
        
        if api_key_encrypted:
            try:
                # Try to decrypt the API key
                from security_manager import decrypt_api_key
                api_key = decrypt_api_key(api_key_encrypted)
                logger.info("✓ Using encrypted API key")
            except Exception as e:
                logger.error(f"Failed to decrypt API key: {e}")
                if api_key_plain:
                    api_key = api_key_plain
                    logger.warning("⚠️ Falling back to plain text API key")
                else:
                    messagebox.showerror("Error", "Failed to decrypt API key and no fallback available!")
                    self.root.destroy()
                    return
        elif api_key_plain:
            api_key = api_key_plain
            logger.warning("⚠️ Using plain text API key (consider encrypting)")
        else:
            messagebox.showerror("Error", "No API key found in environment variables!")
            self.root.destroy()
            return
        
        self.client = anthropic.Anthropic(api_key=api_key)
        
        # UI components
        self.setup_styles()
        self.create_widgets()
        self.create_menu()
        
        # Focus on input field
        self.input_field.focus_set()
        
        # Auto-save on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return hashlib.md5(f"{datetime.now().isoformat()}{os.getpid()}".encode()).hexdigest()[:12]
    
    def init_speech_systems(self):
        """Initialize speech systems for input and output"""
        try:
            # Initialize recognizer instance
            self.recognizer = sr.Recognizer()
            
            # Initialize text-to-speech engine
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)  # Speed of speech
            self.tts_engine.setProperty('volume', 0.9)  # Volume 0-1
            voices = self.tts_engine.getProperty('voices')
            if voices:
                self.tts_engine.setProperty('voice', voices[0].id)  # Set default voice
            
            print("Speech systems initialized successfully!")
            
        except Exception as e:
            print(f"Warning: Speech systems initialization failed: {e}")
            self.recognizer = None
            self.tts_engine = None
    
    def setup_styles(self):
        """Configure colors and fonts"""
        theme = self.config.get('theme', 'light')
        
        if theme == 'dark':
            self.bg_color = "#2b2b2b"
            self.chat_bg = "#1e1e1e"
            self.user_color = "#0d47a1"
            self.claude_color = "#424242"
            self.text_color = "#ffffff"
        else:
            self.bg_color = "#f0f0f0"
            self.chat_bg = "#ffffff"
            self.user_color = "#e3f2fd"
            self.claude_color = "#f5f5f5"
            self.text_color = "#000000"
        
        self.primary_color = "#1976d2"
        self.secondary_color = "#7b1fa2"
        
        self.root.configure(bg=self.bg_color)
        
        # Configure fonts
        self.font_normal = font.Font(family="Segoe UI", size=10)
        self.font_bold = font.Font(family="Segoe UI", size=10, weight="bold")
        self.font_header = font.Font(family="Segoe UI", size=14, weight="bold")
    
    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Conversation", command=self.new_conversation)
        file_menu.add_command(label="Save Conversation", command=self.save_conversation)
        file_menu.add_command(label="Export Conversation", command=self.export_conversation)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Analytics Dashboard", command=self.show_analytics)
        tools_menu.add_command(label="Configuration", command=self.show_config)
        tools_menu.add_command(label="Conversation History", command=self.show_history)
        tools_menu.add_separator()
        if OPTIMIZATION_AVAILABLE:
            tools_menu.add_command(label="Model Optimization", command=self.show_optimization)
        else:
            tools_menu.add_command(label="Model Optimization (Unavailable)", command=self.show_optimization_unavailable, state="disabled")
        
        # Visualization menu
        visualize_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualizations", menu=visualize_menu)
        visualize_menu.add_command(label="Show Sample", command=self.show_visualization)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_widgets(self):
        """Create and layout GUI elements"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header with analytics
        self.create_header(main_frame)
        
        # Chat display area
        self.create_chat_area(main_frame)
        
        # Input area
        self.create_input_area(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
        
        # Add initial message
        intelligence_status = "🧠 with Real-Time Intelligence" if INTELLIGENCE_AVAILABLE else "⚠️ (Intelligence limited - install dependencies)"
        self.add_message(f"Hello! I'm Claude Enhanced {intelligence_status}, featuring conversation analytics and improved capabilities. How can I help you today?", "claude")
    
    def create_header(self, parent):
        """Create header with title and stats"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)
        
        title_label = ttk.Label(header_frame, text="🤖 Claude AI Desktop Enhanced", font=self.font_header)
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Stats frame
        stats_frame = ttk.Frame(header_frame)
        stats_frame.grid(row=0, column=1, sticky=tk.E)
        
        self.stats_label = ttk.Label(stats_frame, text="Messages: 0 | Quality: N/A", foreground="gray")
        self.stats_label.grid(row=0, column=0, padx=(10, 0))
        
        self.status_label = ttk.Label(stats_frame, text="Ready", foreground="green")
        self.status_label.grid(row=0, column=1, padx=(10, 0))
    
    def create_chat_area(self, parent):
        """Create chat display area"""
        chat_frame = ttk.Frame(parent)
        chat_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # Chat text area with scrollbar
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=self.font_normal,
            bg=self.chat_bg,
            fg=self.text_color,
            relief=tk.SUNKEN,
            borderwidth=1,
            state=tk.DISABLED,
            height=20
        )
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags
        self.chat_display.tag_configure("user", background=self.user_color, font=self.font_bold, spacing1=5, spacing3=5)
        self.chat_display.tag_configure("claude", background=self.claude_color, font=self.font_bold, spacing1=5, spacing3=5)
        self.chat_display.tag_configure("user_text", font=self.font_normal, spacing3=10)
        self.chat_display.tag_configure("claude_text", font=self.font_normal, spacing3=10)
        self.chat_display.tag_configure("timestamp", foreground="gray", font=("Segoe UI", 8))
        self.chat_display.tag_configure("quality", foreground="blue", font=("Segoe UI", 8))
    
    def create_input_area(self, parent):
        """Create input area with enhanced controls"""
        input_frame = ttk.Frame(parent)
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        # Input field
        self.input_field = tk.Text(
            input_frame,
            height=3,
            font=self.font_normal,
            wrap=tk.WORD,
            relief=tk.SUNKEN,
            borderwidth=1,
            bg=self.chat_bg,
            fg=self.text_color
        )
        self.input_field.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Bind events
        self.input_field.bind('<Return>', self.on_enter_key)
        self.input_field.bind('<Shift-Return>', self.on_shift_enter)
        
        # Button frame
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Send button
        self.send_button = ttk.Button(
            button_frame,
            text="Send",
            command=self.send_message,
            width=10
        )
        self.send_button.grid(row=0, column=0, sticky=tk.E+tk.W, pady=(0, 5))
        
        # Clear button
        self.clear_button = ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_conversation,
            width=10
        )
        self.clear_button.grid(row=1, column=0, sticky=tk.E+tk.W, pady=(0, 5))
        
        # Voice input button
        self.voice_button = ttk.Button(
            button_frame,
            text="🎤 Voice",
            command=self.start_voice_input,
            width=10
        )
        self.voice_button.grid(row=2, column=0, sticky=tk.E+tk.W, pady=(0, 5))
        
        # TTS toggle button
        self.tts_enabled = tk.BooleanVar(value=True)
        self.tts_button = ttk.Checkbutton(
            button_frame,
            text="🔊 TTS",
            variable=self.tts_enabled,
            command=self.toggle_tts,
            width=10
        )
        self.tts_button.grid(row=3, column=0, sticky=tk.E+tk.W, pady=(0, 5))
        
        # Universal mode indicator
        mode_frame = ttk.LabelFrame(button_frame, text="Mode", padding="5")
        mode_frame.grid(row=4, column=0, sticky=tk.E+tk.W, pady=(5, 0))
        
        mode_label = ttk.Label(mode_frame, text="Universal\n(All Modes Combined)", font=("Segoe UI", 8))
        mode_label.grid(row=0, column=0, sticky=tk.W)
    
    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.token_label = ttk.Label(status_frame, text="Tokens: 0", foreground="gray")
        self.token_label.grid(row=0, column=1)
    
    def update_stats(self):
        """Update conversation statistics"""
        if not self.conversation:
            self.stats_label.config(text="Messages: 0 | Quality: N/A")
            return
        
        message_count = len(self.conversation)
        quality_score = self.analyzer.analyze_conversation_quality(self.conversation)
        
        self.stats_label.config(text=f"Messages: {message_count} | Quality: {quality_score:.2f}")
    
    def get_mode_parameters(self) -> Dict:
        """Get API parameters for universal mode"""
        base_params = {
            'model': self.config.get('model'),
            'max_tokens': 1500,  # Blended max_tokens for versatility
            'temperature': 0.6   # Blended temperature for balanced creativity and focus
        }
        return base_params
    
    def on_enter_key(self, event):
        """Handle Enter key press"""
        if event.state & 0x1:  # Shift key is pressed
            return None
        else:
            self.send_message()
            return "break"
    
    def on_shift_enter(self, event):
        """Handle Shift+Enter key press"""
        return None
    
    def add_message(self, message, sender, timestamp=None, quality_score=None):
        """Add a message to the chat display"""
        self.chat_display.configure(state=tk.NORMAL)
        
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add sender label
        if sender == "user":
            self.chat_display.insert(tk.END, "You", "user")
        else:
            self.chat_display.insert(tk.END, "Claude", "claude")
        
        # Add timestamp
        self.chat_display.insert(tk.END, f" ({timestamp})", "timestamp")
        
        # Add quality score if available
        if quality_score is not None:
            self.chat_display.insert(tk.END, f" [Q: {quality_score:.2f}]", "quality")
        
        self.chat_display.insert(tk.END, "\n")
        
        # Add message content
        tag = "user_text" if sender == "user" else "claude_text"
        self.chat_display.insert(tk.END, message + "\n\n", tag)
        
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def send_message(self):
        """Send message to Claude AI"""
        message = self.input_field.get("1.0", tk.END).strip()
        
        if not message:
            return
        
        # Add user message to display
        self.add_message(message, "user")
        
        # Clear input field
        self.input_field.delete("1.0", tk.END)
        
        # Update UI state
        self.send_button.configure(state=tk.DISABLED, text="Sending...")
        self.status_label.configure(text="Claude is thinking...", foreground="orange")
        self.progress_bar.start()
        
        # Send request in separate thread
        thread = threading.Thread(target=self.send_to_claude, args=(message,))
        thread.daemon = True
        thread.start()
    
    def send_to_claude(self, message):
        """Send message to Claude API in background thread"""
        start_time = time.time()
        
        try:
            # Enhance message with intelligence if available
            enhanced_message = message
            if hasattr(self, 'bert_model') and hasattr(self, 'bert_tokenizer'):
                try:
                    inputs = self.bert_tokenizer(message, return_tensors='pt')
                    outputs = self.bert_model(**inputs)
                    # Use original message for now, but we've processed it with BERT
                    enhanced_message = message
                    self.root.after(0, lambda: self.status_label.configure(text="Processing with BERT...", foreground="purple"))
                    print(f"BERT processed message: {message[:50]}...")
                except Exception as e:
                    print(f"BERT processing failed: {e}")
                    enhanced_message = message

            elif self.intelligence and INTELLIGENCE_AVAILABLE:
                try:
                    enhanced_message = self.intelligence.enhance_message(message)
                    self.root.after(0, lambda: self.status_label.configure(text="Enhancing with intelligence...", foreground="blue"))
                except Exception as e:
                    logger.warning(f"Intelligence enhancement failed: {e}")
                    enhanced_message = message
            
            # Add user message to conversation (with enhanced content)
            user_msg = {
                'role': 'user',
                'content': enhanced_message,
                'timestamp': datetime.now().isoformat(),
                'response_time': 0
            }
            self.conversation.append(user_msg)
            
            # Get API parameters based on mode
            params = self.get_mode_parameters()
            
            # Clean messages for API (only role and content)
            api_messages = []
            for msg in self.conversation:
                clean_msg = {
                    'role': msg['role'],
                    'content': msg['content']
                }
                api_messages.append(clean_msg)
            
            # Send to Claude
            response = self.client.messages.create(
                messages=api_messages,
                **params
            )
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Extract response
            claude_response = response.content[0].text
            
            # Add Claude's response to conversation
            claude_msg = {
                'role': 'assistant',
                'content': claude_response,
                'timestamp': datetime.now().isoformat(),
                'response_time': response_time,
                'tokens': response.usage.output_tokens if hasattr(response, 'usage') else 0
            }
            self.conversation.append(claude_msg)
            
            # Calculate quality score
            quality_score = self.analyzer.analyze_conversation_quality([claude_msg])
            claude_msg['quality_score'] = quality_score
            
            # Update UI in main thread
            self.root.after(0, self.handle_claude_response, claude_response, response_time, quality_score)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, self.handle_error, error_msg)
    
    def handle_claude_response(self, response, response_time, quality_score):
        """Handle Claude's response in main thread"""
        # Add response to chat display
        self.add_message(response, "claude", quality_score=quality_score)
        
        # Update UI state
        self.send_button.configure(state=tk.NORMAL, text="Send")
        self.status_label.configure(text="Ready", foreground="green")
        self.progress_bar.stop()
        
        # Update statistics
        self.update_stats()
        
        # Update token count
        total_tokens = sum(msg.get('tokens', 0) for msg in self.conversation)
        self.token_label.config(text=f"Tokens: {total_tokens}")
        
        # Focus back on input field
        self.input_field.focus_set()
        
        # Auto-save if enabled
        if self.config.get('auto_save', True):
            self.auto_save_conversation()
        
        # Speak Claude's response if TTS is enabled
        if self.tts_enabled.get() and self.tts_engine:
            self.speak_text(response)
    
    def handle_error(self, error_msg):
        """Handle errors in main thread"""
        self.add_message(error_msg, "claude")
        self.send_button.configure(state=tk.NORMAL, text="Send")
        self.status_label.configure(text="Error", foreground="red")
        self.progress_bar.stop()
        self.input_field.focus_set()
    
    def auto_save_conversation(self):
        """Auto-save conversation to database"""
        if self.conversation:
            try:
                title = self.analyzer.generate_conversation_summary(self.conversation)
                self.db.save_conversation(self.session_id, self.conversation, title=title)
                logger.info(f"Auto-saved conversation: {title}")
            except Exception as e:
                logger.error(f"Auto-save failed: {e}")
    
    def save_conversation(self):
        """Manual save conversation"""
        if not self.conversation:
            messagebox.showinfo("Save Conversation", "No conversation to save.")
            return
        
        title = self.analyzer.generate_conversation_summary(self.conversation)
        self.db.save_conversation(self.session_id, self.conversation, title=title)
        messagebox.showinfo("Save Conversation", f"Conversation saved: {title}")
    
    def export_conversation(self):
        """Export conversation to file"""
        if not self.conversation:
            messagebox.showinfo("Export Conversation", "No conversation to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                export_data = {
                    'session_id': self.session_id,
                    'timestamp': datetime.now().isoformat(),
                    'conversation': self.conversation,
                    'analytics': {
                        'total_messages': len(self.conversation),
                        'quality_score': self.analyzer.analyze_conversation_quality(self.conversation),
                        'summary': self.analyzer.generate_conversation_summary(self.conversation)
                    }
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Export Conversation", f"Conversation exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export conversation: {str(e)}")
    
    def new_conversation(self):
        """Start a new conversation"""
        if self.conversation and messagebox.askyesno("New Conversation", "Save current conversation before starting new one?"):
            self.save_conversation()
        
        self.clear_conversation()
        self.session_id = self._generate_session_id()
        self.conversation_start_time = datetime.now()
    
    def clear_conversation(self):
        """Clear the conversation"""
        self.conversation = []
        
        # Clear chat display
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.configure(state=tk.DISABLED)
        
        # Add initial message
        self.add_message("Hello! I'm Claude Enhanced. How can I help you today?", "claude")
        
        # Update stats
        self.update_stats()
        self.token_label.config(text="Tokens: 0")
        
        # Focus on input field
        self.input_field.focus_set()
    
    def show_analytics(self):
        """Show analytics dashboard"""
        analytics_window = tk.Toplevel(self.root)
        analytics_window.title("Analytics Dashboard")
        analytics_window.geometry("600x400")
        
        # Get analytics data
        analytics = self.db.get_conversation_analytics(30)
        
        # Create analytics display
        frame = ttk.Frame(analytics_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="📊 Analytics Dashboard", font=self.font_header).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Stats
        stats = [
            ("Total Conversations (30 days)", analytics['total_conversations']),
            ("Total Messages", analytics['total_messages']),
            ("Average Quality Score", f"{analytics['avg_quality']:.2f}"),
            ("Average Duration", f"{analytics['avg_duration']:.1f} min")
        ]
        
        for i, (label, value) in enumerate(stats):
            ttk.Label(frame, text=f"{label}:", font=self.font_bold).grid(row=i+1, column=0, sticky=tk.W, pady=5)
            ttk.Label(frame, text=str(value)).grid(row=i+1, column=1, sticky=tk.W, padx=(20, 0), pady=5)
    
    def show_config(self):
        """Show configuration window"""
        config_window = tk.Toplevel(self.root)
        config_window.title("Configuration")
        config_window.geometry("400x300")
        
        frame = ttk.Frame(config_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="⚙️ Configuration", font=self.font_header).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Configuration options
        configs = [
            ("Model", 'model', ['claude-3-5-sonnet-20241022', 'claude-3-haiku-20240307']),
            ("Max Tokens", 'max_tokens', None),
            ("Temperature", 'temperature', None),
            ("Theme", 'theme', ['light', 'dark']),
            ("Auto Save", 'auto_save', None)
        ]
        
        self.config_vars = {}
        
        for i, (label, key, options) in enumerate(configs):
            ttk.Label(frame, text=f"{label}:").grid(row=i+1, column=0, sticky=tk.W, pady=5)
            
            if options:
                var = tk.StringVar(value=self.config.get(key))
                combo = ttk.Combobox(frame, textvariable=var, values=options, state="readonly")
                combo.grid(row=i+1, column=1, sticky=tk.W, padx=(20, 0), pady=5)
                self.config_vars[key] = var
            elif key == 'auto_save':
                var = tk.BooleanVar(value=self.config.get(key))
                check = ttk.Checkbutton(frame, variable=var)
                check.grid(row=i+1, column=1, sticky=tk.W, padx=(20, 0), pady=5)
                self.config_vars[key] = var
            else:
                var = tk.StringVar(value=str(self.config.get(key)))
                entry = ttk.Entry(frame, textvariable=var)
                entry.grid(row=i+1, column=1, sticky=tk.W, padx=(20, 0), pady=5)
                self.config_vars[key] = var
        
        # Save button
        def save_config():
            for key, var in self.config_vars.items():
                value = var.get()
                if key in ['max_tokens']:
                    value = int(value)
                elif key in ['temperature']:
                    value = float(value)
                elif key in ['auto_save']:
                    value = bool(value)
                
                self.config.set(key, value)
            
            messagebox.showinfo("Configuration", "Configuration saved successfully!")
            config_window.destroy()
        
        ttk.Button(frame, text="Save", command=save_config).grid(row=len(configs)+2, column=0, columnspan=2, pady=20)

    def show_optimization(self):
        """Show model optimization interface"""
        optimization_window = tk.Toplevel(self.root)
        optimization_window.title("Model Optimization")
        optimization_window.geometry("600x400")
        
        frame = ttk.Frame(optimization_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="🔧 Model Optimization", font=self.font_header).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        if self.optimization_manager:
            # Assume models to optimize
            models_to_optimize = ['conversation_quality', 'response_time']
            
            for i, model_type in enumerate(models_to_optimize):
                ttk.Label(frame, text=f"Optimize {model_type}:").grid(row=i+1, column=0, sticky=tk.W, pady=5)
                ttk.Button(frame, text="Start Optimization", command=lambda mt=model_type: self.start_model_optimization(mt)).grid(row=i+1, column=1, pady=5)

    def show_optimization_unavailable(self):
        """Show message when optimization is unavailable"""
        messagebox.showerror("Optimization Unavailable", "Model optimization requires additional libraries (optuna, scikit-learn). Please install them to use this feature.")

    def start_model_optimization(self, model_type: str):
        """Start model optimization process"""
        if not self.optimization_manager:
            messagebox.showerror("Error", "Model optimization manager is not available.")
            return

        result = self.optimization_manager.optimizers[model_type].optimize_model(n_trials=50)
        messagebox.showinfo("Optimization Complete", f"Optimization for {model_type} completed. Best Value: {result.best_value:.4f}")  



    
    def show_history(self):
        """Show conversation history"""
        history_window = tk.Toplevel(self.root)
        history_window.title("Conversation History")
        history_window.geometry("500x400")
        
        # Implementation for conversation history browser
        frame = ttk.Frame(history_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="📚 Conversation History", font=self.font_header).grid(row=0, column=0, pady=(0, 20))
        ttk.Label(frame, text="History browser coming soon...").grid(row=1, column=0)
    
    def show_about(self):
        """Show about dialog"""
        intelligence_features = "\n• Real-time web search and current information\n• Weather data integration\n• News feed access\n• Enhanced contextual responses" if INTELLIGENCE_AVAILABLE else "\n• Intelligence enhancement available (install dependencies)"
        
        about_text = f"""
Claude AI Desktop - Enhanced Version

Features:
• Conversation analytics and quality scoring
• Multi-mode conversation support
• Persistent conversation storage
• Export capabilities
• Configuration management
• Performance monitoring{intelligence_features}

Version: 2.1.0 - Intelligence Enhanced
"""
        messagebox.showinfo("About", about_text)
    
    def start_voice_input(self):
        """Start voice input in a separate thread"""
        if not self.recognizer:
            messagebox.showerror("Voice Input Error", "Speech recognition is not available")
            return
        
        self.voice_button.configure(state=tk.DISABLED, text="🎤 Listening...")
        self.status_label.configure(text="Listening for voice input...", foreground="blue")
        
        # Start voice recognition in a separate thread
        thread = threading.Thread(target=self.perform_voice_input)
        thread.daemon = True
        thread.start()
    
    def perform_voice_input(self):
        """Perform voice input using microphone"""
        try:
            with sr.Microphone() as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source)
                
                # Listen for audio with a 5-second timeout
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                # Update status
                self.root.after(0, lambda: self.status_label.configure(text="Processing voice input...", foreground="purple"))
                
                # Recognize speech using Google Web Speech API
                text = self.recognizer.recognize_google(audio)
                
                # Update UI in main thread
                self.root.after(0, self.handle_voice_input, text)
                
        except sr.WaitTimeoutError:
            self.root.after(0, self.handle_voice_error, "Voice input timeout. Please try again.")
        except sr.UnknownValueError:
            self.root.after(0, self.handle_voice_error, "Could not understand audio. Please try again.")
        except sr.RequestError as e:
            self.root.after(0, self.handle_voice_error, f"Could not request results from speech recognition service: {e}")
        except Exception as e:
            self.root.after(0, self.handle_voice_error, f"Voice input error: {e}")
    
    def handle_voice_input(self, text):
        """Handle successful voice input"""
        # Insert text into input field
        self.input_field.insert(tk.END, text)
        
        # Reset voice button
        self.voice_button.configure(state=tk.NORMAL, text="🎤 Voice")
        self.status_label.configure(text="Voice input captured", foreground="green")
        
        # Focus on input field
        self.input_field.focus_set()
    
    def handle_voice_error(self, error_msg):
        """Handle voice input errors"""
        self.voice_button.configure(state=tk.NORMAL, text="🎤 Voice")
        self.status_label.configure(text=error_msg, foreground="red")
        
        # Show error message
        messagebox.showerror("Voice Input Error", error_msg)
    
    def toggle_tts(self):
        """Toggle text-to-speech on/off"""
        if self.tts_enabled.get():
            self.status_label.configure(text="Text-to-speech enabled", foreground="green")
        else:
            self.status_label.configure(text="Text-to-speech disabled", foreground="gray")
    
    def speak_text(self, text):
        """Speak text using TTS in a separate thread"""
        if not self.tts_engine:
            return
        
        def tts_worker():
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"TTS error: {e}")
        
        thread = threading.Thread(target=tts_worker)
        thread.daemon = True
        thread.start()
    
    def on_closing(self):
        """Handle application closing"""
        if self.conversation and self.config.get('auto_save', True):
            self.auto_save_conversation()
        
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            # Save window geometry
            geometry = self.root.geometry()
            width, height = geometry.split('x')[0], geometry.split('x')[1].split('+')[0]
            self.config.set('window_width', int(width))
            self.config.set('window_height', int(height))
            
            self.root.destroy()

def main():
    """Main function to run the enhanced application"""
    # Check if API key is set
    load_dotenv()
    if not os.environ.get('ANTHROPIC_API_KEY'):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "API Key Missing",
            "ANTHROPIC_API_KEY not found in environment variables!\\n\\n"
            "Please:\\n"
            "1. Copy .env.example to .env\\n"
            "2. Add your Anthropic API key to the .env file\\n"
            "3. Get your API key from: https://console.anthropic.com/"
        )
        return
    
    # Create and run the application
    root = tk.Tk()
    app = EnhancedClaudeDesktopApp(root)
    
    print("🚀 Claude Desktop AI Enhanced started!")
    print("📱 Desktop application with analytics is now running")
    root.mainloop()

if __name__ == "__main__":
    main()
