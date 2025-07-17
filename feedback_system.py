import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import time
import uuid
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeedbackDatabase:
    """Database for storing user feedback and analytics"""
    
    def __init__(self, db_path: str = "feedback.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize feedback database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                feedback_type TEXT NOT NULL,
                rating INTEGER,
                comment TEXT,
                feature_request TEXT,
                bug_report TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                response_time REAL,
                conversation_context TEXT
            )
        ''')
        
        # Response ratings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS response_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT NOT NULL,
                rating INTEGER NOT NULL,
                feedback_text TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Feature usage analytics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feature_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature_name TEXT NOT NULL,
                usage_count INTEGER DEFAULT 1,
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_session TEXT
            )
        ''')
        
        # Bug reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bug_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bug_type TEXT NOT NULL,
                description TEXT NOT NULL,
                steps_to_reproduce TEXT,
                expected_behavior TEXT,
                actual_behavior TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'new',
                priority TEXT DEFAULT 'medium'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_feedback(self, feedback_data: Dict) -> int:
        """Save user feedback to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_feedback (
                session_id, feedback_type, rating, comment, feature_request, 
                bug_report, response_time, conversation_context
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            feedback_data.get('session_id', ''),
            feedback_data.get('feedback_type', ''),
            feedback_data.get('rating'),
            feedback_data.get('comment', ''),
            feedback_data.get('feature_request', ''),
            feedback_data.get('bug_report', ''),
            feedback_data.get('response_time'),
            feedback_data.get('conversation_context', '')
        ))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return feedback_id
    
    def save_response_rating(self, message_id: str, rating: int, feedback_text: str = "") -> int:
        """Save rating for a specific response"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO response_ratings (message_id, rating, feedback_text)
            VALUES (?, ?, ?)
        ''', (message_id, rating, feedback_text))
        
        rating_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return rating_id
    
    def track_feature_usage(self, feature_name: str, user_session: str = ""):
        """Track feature usage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if feature already exists for this session
        cursor.execute('''
            SELECT id, usage_count FROM feature_usage 
            WHERE feature_name = ? AND user_session = ?
        ''', (feature_name, user_session))
        
        result = cursor.fetchone()
        
        if result:
            # Update existing record
            cursor.execute('''
                UPDATE feature_usage 
                SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (result[0],))
        else:
            # Insert new record
            cursor.execute('''
                INSERT INTO feature_usage (feature_name, user_session)
                VALUES (?, ?)
            ''', (feature_name, user_session))
        
        conn.commit()
        conn.close()
    
    def get_feedback_analytics(self, days: int = 30) -> Dict:
        """Get feedback analytics for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Overall feedback stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total_feedback,
                AVG(rating) as avg_rating,
                COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive_feedback,
                COUNT(CASE WHEN rating <= 2 THEN 1 END) as negative_feedback
            FROM user_feedback 
            WHERE timestamp >= ? AND rating IS NOT NULL
        ''', (start_date,))
        
        overall_stats = cursor.fetchone()
        
        # Feature usage stats
        cursor.execute('''
            SELECT feature_name, SUM(usage_count) as total_usage
            FROM feature_usage
            WHERE last_used >= ?
            GROUP BY feature_name
            ORDER BY total_usage DESC
        ''', (start_date,))
        
        feature_stats = cursor.fetchall()
        
        # Common feedback themes
        cursor.execute('''
            SELECT comment, COUNT(*) as frequency
            FROM user_feedback
            WHERE timestamp >= ? AND comment IS NOT NULL AND comment != ''
            GROUP BY comment
            ORDER BY frequency DESC
            LIMIT 10
        ''', (start_date,))
        
        common_feedback = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_feedback': overall_stats[0] or 0,
            'avg_rating': overall_stats[1] or 0,
            'positive_feedback': overall_stats[2] or 0,
            'negative_feedback': overall_stats[3] or 0,
            'feature_usage': dict(feature_stats),
            'common_feedback': dict(common_feedback)
        }

class FeedbackCollector:
    """UI component for collecting user feedback"""
    
    def __init__(self, parent_window, session_id: str = None):
        self.parent = parent_window
        self.session_id = session_id or str(uuid.uuid4())
        self.db = FeedbackDatabase()
        self.feedback_window = None
        
    def show_quick_feedback(self, message_id: str = None):
        """Show quick feedback dialog for a specific message"""
        if self.feedback_window and self.feedback_window.winfo_exists():
            self.feedback_window.lift()
            return
        
        self.feedback_window = tk.Toplevel(self.parent)
        self.feedback_window.title("Quick Feedback")
        self.feedback_window.geometry("400x300")
        self.feedback_window.resizable(False, False)
        
        # Make it modal
        self.feedback_window.transient(self.parent)
        self.feedback_window.grab_set()
        
        # Center on parent
        self.feedback_window.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))
        
        # Main frame
        main_frame = ttk.Frame(self.feedback_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="How was this response?", 
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Rating stars
        rating_frame = ttk.Frame(main_frame)
        rating_frame.pack(pady=(0, 20))
        
        self.rating_var = tk.IntVar(value=5)
        
        ttk.Label(rating_frame, text="Rating:").pack(side=tk.LEFT, padx=(0, 10))
        
        for i in range(1, 6):
            ttk.Radiobutton(rating_frame, text=f"★" * i, variable=self.rating_var, 
                           value=i).pack(side=tk.LEFT, padx=5)
        
        # Comment text area
        ttk.Label(main_frame, text="Additional comments (optional):").pack(anchor=tk.W, pady=(0, 5))
        
        self.comment_text = tk.Text(main_frame, height=5, width=40)
        self.comment_text.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Submit", 
                  command=lambda: self.submit_quick_feedback(message_id)).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", 
                  command=self.feedback_window.destroy).pack(side=tk.RIGHT)
        
        self.feedback_window.protocol("WM_DELETE_WINDOW", self.feedback_window.destroy)
    
    def submit_quick_feedback(self, message_id: str = None):
        """Submit quick feedback"""
        rating = self.rating_var.get()
        comment = self.comment_text.get("1.0", tk.END).strip()
        
        if message_id:
            self.db.save_response_rating(message_id, rating, comment)
        
        # Also save to general feedback
        feedback_data = {
            'session_id': self.session_id,
            'feedback_type': 'quick_rating',
            'rating': rating,
            'comment': comment
        }
        
        self.db.save_feedback(feedback_data)
        
        # Show confirmation
        messagebox.showinfo("Thank You", "Your feedback has been submitted!")
        self.feedback_window.destroy()
    
    def show_detailed_feedback(self):
        """Show detailed feedback dialog"""
        if self.feedback_window and self.feedback_window.winfo_exists():
            self.feedback_window.lift()
            return
        
        self.feedback_window = tk.Toplevel(self.parent)
        self.feedback_window.title("Detailed Feedback")
        self.feedback_window.geometry("500x600")
        self.feedback_window.resizable(True, True)
        
        # Make it modal
        self.feedback_window.transient(self.parent)
        self.feedback_window.grab_set()
        
        # Main frame with scrollbar
        canvas = tk.Canvas(self.feedback_window)
        scrollbar = ttk.Scrollbar(self.feedback_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Form content
        form_frame = ttk.Frame(scrollable_frame, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(form_frame, text="Detailed Feedback", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Feedback type
        ttk.Label(form_frame, text="Feedback Type:").pack(anchor=tk.W, pady=(0, 5))
        self.feedback_type_var = tk.StringVar(value="general")
        
        feedback_types = [
            ("General Feedback", "general"),
            ("Feature Request", "feature"),
            ("Bug Report", "bug"),
            ("Performance Issue", "performance")
        ]
        
        for text, value in feedback_types:
            ttk.Radiobutton(form_frame, text=text, variable=self.feedback_type_var, 
                           value=value).pack(anchor=tk.W, padx=20)
        
        # Rating
        ttk.Label(form_frame, text="Overall Rating:").pack(anchor=tk.W, pady=(20, 5))
        self.detailed_rating_var = tk.IntVar(value=5)
        
        rating_frame = ttk.Frame(form_frame)
        rating_frame.pack(anchor=tk.W, padx=20)
        
        for i in range(1, 6):
            ttk.Radiobutton(rating_frame, text=f"{i} Star{'s' if i > 1 else ''}", 
                           variable=self.detailed_rating_var, value=i).pack(anchor=tk.W)
        
        # Comment
        ttk.Label(form_frame, text="Comments:").pack(anchor=tk.W, pady=(20, 5))
        self.detailed_comment_text = tk.Text(form_frame, height=6, width=50)
        self.detailed_comment_text.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Feature request (conditional)
        ttk.Label(form_frame, text="Feature Request (if applicable):").pack(anchor=tk.W, pady=(10, 5))
        self.feature_request_text = tk.Text(form_frame, height=4, width=50)
        self.feature_request_text.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Bug report (conditional)
        ttk.Label(form_frame, text="Bug Description (if applicable):").pack(anchor=tk.W, pady=(10, 5))
        self.bug_report_text = tk.Text(form_frame, height=4, width=50)
        self.bug_report_text.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Submit button
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Submit Feedback", 
                  command=self.submit_detailed_feedback).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", 
                  command=self.feedback_window.destroy).pack(side=tk.RIGHT)
        
        self.feedback_window.protocol("WM_DELETE_WINDOW", self.feedback_window.destroy)
    
    def submit_detailed_feedback(self):
        """Submit detailed feedback"""
        feedback_data = {
            'session_id': self.session_id,
            'feedback_type': self.feedback_type_var.get(),
            'rating': self.detailed_rating_var.get(),
            'comment': self.detailed_comment_text.get("1.0", tk.END).strip(),
            'feature_request': self.feature_request_text.get("1.0", tk.END).strip(),
            'bug_report': self.bug_report_text.get("1.0", tk.END).strip()
        }
        
        self.db.save_feedback(feedback_data)
        
        # Show confirmation
        messagebox.showinfo("Thank You", "Your detailed feedback has been submitted!")
        self.feedback_window.destroy()

class FeedbackAnalytics:
    """Analytics dashboard for feedback data"""
    
    def __init__(self, parent_window):
        self.parent = parent_window
        self.db = FeedbackDatabase()
        self.analytics_window = None
    
    def show_analytics_dashboard(self):
        """Show analytics dashboard"""
        if self.analytics_window and self.analytics_window.winfo_exists():
            self.analytics_window.lift()
            return
        
        self.analytics_window = tk.Toplevel(self.parent)
        self.analytics_window.title("Feedback Analytics")
        self.analytics_window.geometry("800x600")
        
        # Main frame
        main_frame = ttk.Frame(self.analytics_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Feedback Analytics Dashboard", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Notebook for different analytics views
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Overview tab
        overview_frame = ttk.Frame(notebook)
        notebook.add(overview_frame, text="Overview")
        
        # Trends tab
        trends_frame = ttk.Frame(notebook)
        notebook.add(trends_frame, text="Trends")
        
        # Details tab
        details_frame = ttk.Frame(notebook)
        notebook.add(details_frame, text="Details")
        
        # Load analytics data
        self.load_overview_analytics(overview_frame)
        self.load_trends_analytics(trends_frame)
        self.load_details_analytics(details_frame)
        
        # Refresh button
        ttk.Button(main_frame, text="Refresh Data", 
                  command=self.refresh_analytics).pack(pady=(10, 0))
        
        self.analytics_window.protocol("WM_DELETE_WINDOW", self.analytics_window.destroy)
    
    def load_overview_analytics(self, frame):
        """Load overview analytics"""
        analytics = self.db.get_feedback_analytics(days=30)
        
        # Create overview widgets
        overview_text = f"""
📊 Feedback Overview (Last 30 Days)

Total Feedback: {analytics['total_feedback']}
Average Rating: {analytics['avg_rating']:.2f}/5
Positive Feedback: {analytics['positive_feedback']}
Negative Feedback: {analytics['negative_feedback']}

🎯 Most Used Features:
"""
        
        for feature, count in list(analytics['feature_usage'].items())[:5]:
            overview_text += f"• {feature}: {count} uses\n"
        
        overview_text += f"""
💬 Common Feedback Themes:
"""
        
        for comment, freq in list(analytics['common_feedback'].items())[:5]:
            overview_text += f"• {comment[:50]}{'...' if len(comment) > 50 else ''}: {freq} times\n"
        
        text_widget = tk.Text(frame, wrap=tk.WORD, font=("Arial", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, overview_text)
        text_widget.config(state=tk.DISABLED)
    
    def load_trends_analytics(self, frame):
        """Load trends analytics"""
        ttk.Label(frame, text="Trends Analytics", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Placeholder for trend charts
        trend_text = """
📈 Trend Analysis

• User satisfaction has improved by 15% over the last month
• Feature usage is highest during weekdays
• Response time complaints decreased by 8%
• Most requested feature: Dark mode theme
• Common issues: Slow response times, UI improvements needed

(Note: This is a placeholder - in a full implementation, 
you would integrate with a charting library like matplotlib 
or plotly to show visual trends)
"""
        
        text_widget = tk.Text(frame, wrap=tk.WORD, font=("Arial", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, trend_text)
        text_widget.config(state=tk.DISABLED)
    
    def load_details_analytics(self, frame):
        """Load detailed analytics"""
        ttk.Label(frame, text="Detailed Analytics", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Create treeview for detailed data
        columns = ('Date', 'Type', 'Rating', 'Comment')
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Load recent feedback
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DATE(timestamp), feedback_type, rating, comment
            FROM user_feedback
            ORDER BY timestamp DESC
            LIMIT 50
        ''')
        
        for row in cursor.fetchall():
            tree.insert('', 'end', values=row)
        
        conn.close()
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
    
    def refresh_analytics(self):
        """Refresh analytics data"""
        if self.analytics_window and self.analytics_window.winfo_exists():
            self.analytics_window.destroy()
        self.show_analytics_dashboard()

# Example integration with main application
class FeedbackIntegration:
    """Integration class for adding feedback to existing application"""
    
    def __init__(self, main_app):
        self.main_app = main_app
        self.session_id = str(uuid.uuid4())
        self.collector = FeedbackCollector(main_app.root, self.session_id)
        self.analytics = FeedbackAnalytics(main_app.root)
        self.db = FeedbackDatabase()
        
        # Add feedback menu to main app
        self.add_feedback_menu()
    
    def add_feedback_menu(self):
        """Add feedback menu to main application"""
        # Create menu bar if it doesn't exist
        if not hasattr(self.main_app.root, 'menubar'):
            self.main_app.root.menubar = tk.Menu(self.main_app.root)
            self.main_app.root.config(menu=self.main_app.root.menubar)
        
        # Add feedback menu
        feedback_menu = tk.Menu(self.main_app.root.menubar, tearoff=0)
        self.main_app.root.menubar.add_cascade(label="Feedback", menu=feedback_menu)
        
        feedback_menu.add_command(label="Quick Feedback", command=self.collector.show_quick_feedback)
        feedback_menu.add_command(label="Detailed Feedback", command=self.collector.show_detailed_feedback)
        feedback_menu.add_separator()
        feedback_menu.add_command(label="View Analytics", command=self.analytics.show_analytics_dashboard)
    
    def track_feature_usage(self, feature_name: str):
        """Track feature usage"""
        self.db.track_feature_usage(feature_name, self.session_id)
    
    def add_response_rating_button(self, parent_frame, message_id: str):
        """Add rating button for a specific response"""
        rating_frame = ttk.Frame(parent_frame)
        rating_frame.pack(anchor=tk.E, padx=5, pady=2)
        
        ttk.Button(rating_frame, text="Rate Response", 
                  command=lambda: self.collector.show_quick_feedback(message_id)).pack(side=tk.RIGHT)

if __name__ == "__main__":
    # Test the feedback system
    root = tk.Tk()
    root.title("Feedback System Test")
    root.geometry("600x400")
    
    # Create test interface
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="Feedback System Test", 
             font=("Arial", 14, "bold")).pack(pady=(0, 20))
    
    # Create feedback system
    collector = FeedbackCollector(root)
    analytics = FeedbackAnalytics(root)
    
    # Test buttons
    ttk.Button(main_frame, text="Quick Feedback", 
              command=collector.show_quick_feedback).pack(pady=5)
    ttk.Button(main_frame, text="Detailed Feedback", 
              command=collector.show_detailed_feedback).pack(pady=5)
    ttk.Button(main_frame, text="View Analytics", 
              command=analytics.show_analytics_dashboard).pack(pady=5)
    
    root.mainloop()
