import tkinter as tk
from tkinter import ttk, scrolledtext
import anthropic
import os
from dotenv import load_dotenv
import threading
import time

load_dotenv()

class ClaudeMessagingTest:
    def __init__(self, root):
        self.root = root
        self.root.title("Claude Messaging Test")
        self.root.geometry("600x500")
        
        # Initialize client
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.client = anthropic.Anthropic(api_key=api_key)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Claude Messaging Test", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Log area
        self.log_area = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            height=20,
            width=60
        )
        self.log_area.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input area
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        input_frame.columnconfigure(0, weight=1)
        
        self.input_field = tk.Entry(input_frame, font=("Arial", 10))
        self.input_field.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.input_field.bind('<Return>', self.on_enter)
        
        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=1)
        
        ttk.Button(button_frame, text="Send", command=self.send_message).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Test API", command=self.test_api).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Clear", command=self.clear_log).pack(side=tk.LEFT, padx=2)
        
        # Initial test
        self.log("🚀 Claude Messaging Test Ready")
        self.log("Type a message and press Enter or click Send")
        self.log("Click 'Test API' to verify connection")
        
    def log(self, message):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)
        self.root.update_idletasks()
        
    def clear_log(self):
        """Clear the log"""
        self.log_area.delete(1.0, tk.END)
        
    def on_enter(self, event):
        """Handle Enter key"""
        self.send_message()
        
    def test_api(self):
        """Test API connection"""
        self.log("🔄 Testing API connection...")
        
        def api_test():
            try:
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=50,
                    messages=[{
                        "role": "user",
                        "content": "Please respond with: API TEST SUCCESSFUL"
                    }]
                )
                
                result = response.content[0].text
                self.root.after(0, lambda: self.log(f"✅ API Response: {result}"))
                
            except Exception as e:
                self.root.after(0, lambda: self.log(f"❌ API Error: {str(e)}"))
                
        thread = threading.Thread(target=api_test)
        thread.daemon = True
        thread.start()
        
    def send_message(self):
        """Send message to Claude"""
        message = self.input_field.get().strip()
        if not message:
            return
            
        self.log(f"👤 You: {message}")
        self.input_field.delete(0, tk.END)
        
        # Show sending status
        self.log("🔄 Sending to Claude...")
        
        def send_to_claude():
            try:
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=[{
                        "role": "user",
                        "content": message
                    }]
                )
                
                result = response.content[0].text
                self.root.after(0, lambda: self.log(f"🤖 Claude: {result}"))
                
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self.log(f"❌ Error: {error_msg}"))
                
        thread = threading.Thread(target=send_to_claude)
        thread.daemon = True
        thread.start()

def main():
    root = tk.Tk()
    app = ClaudeMessagingTest(root)
    root.mainloop()

if __name__ == "__main__":
    main()
