import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import anthropic
import os
from dotenv import load_dotenv
import threading
import time
import traceback

load_dotenv()

class ClaudeTroubleshooter:
    def __init__(self, root):
        self.root = root
        self.root.title("Claude Response Troubleshooter")
        self.root.geometry("800x600")
        
        # Initialize client
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key or api_key == 'your_anthropic_api_key_here':
            messagebox.showerror("Error", "API key not configured!")
            return
            
        self.client = anthropic.Anthropic(api_key=api_key)
        self.conversation = []
        
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
        title_label = ttk.Label(main_frame, text="Claude Response Troubleshooter", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            height=20,
            width=80,
            state=tk.DISABLED
        )
        self.chat_display.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags
        self.chat_display.tag_configure("user", foreground="blue", font=("Consolas", 10, "bold"))
        self.chat_display.tag_configure("claude", foreground="green", font=("Consolas", 10, "bold"))
        self.chat_display.tag_configure("error", foreground="red", font=("Consolas", 10, "bold"))
        self.chat_display.tag_configure("system", foreground="orange", font=("Consolas", 10, "bold"))
        
        # Input area
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        input_frame.columnconfigure(0, weight=1)
        
        # Input field
        self.input_field = tk.Text(input_frame, height=3, font=("Arial", 10))
        self.input_field.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.input_field.bind('<Return>', self.on_enter)
        
        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.send_button = ttk.Button(button_frame, text="Send", command=self.send_message)
        self.send_button.grid(row=0, column=0, sticky=tk.E+tk.W, pady=(0, 5))
        
        ttk.Button(button_frame, text="Test API", command=self.test_api).grid(row=1, column=0, sticky=tk.E+tk.W, pady=(0, 5))
        ttk.Button(button_frame, text="Clear", command=self.clear_chat).grid(row=2, column=0, sticky=tk.E+tk.W)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Ready", foreground="green")
        self.status_label.grid(row=3, column=0, pady=(5, 0))\
        
        # Initial message
        self.add_message("🔍 Claude Response Troubleshooter Ready", "system")
        self.add_message("Type a message and click Send to test Claude responses", "system")
        
    def add_message(self, message, sender):
        """Add message to chat display"""
        self.chat_display.configure(state=tk.NORMAL)
        
        timestamp = time.strftime("%H:%M:%S")
        
        if sender == "user":
            self.chat_display.insert(tk.END, f"[{timestamp}] You: ", "user")
        elif sender == "claude":
            self.chat_display.insert(tk.END, f"[{timestamp}] Claude: ", "claude")
        elif sender == "error":
            self.chat_display.insert(tk.END, f"[{timestamp}] ERROR: ", "error")
        else:
            self.chat_display.insert(tk.END, f"[{timestamp}] SYSTEM: ", "system")
            
        self.chat_display.insert(tk.END, message + "\n\n")
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
    def clear_chat(self):
        """Clear chat display"""
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.configure(state=tk.DISABLED)
        self.conversation = []
        
    def on_enter(self, event):
        """Handle Enter key"""
        if event.state & 0x1:  # Shift pressed
            return None
        else:
            self.send_message()
            return "break"
            
    def test_api(self):
        """Test API connection"""
        self.add_message("Testing API connection...", "system")
        self.status_label.config(text="Testing API...", foreground="orange")
        
        def api_test():
            try:
                start_time = time.time()
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=100,
                    messages=[{
                        "role": "user",
                        "content": "Please respond with: API TEST SUCCESSFUL - I am working correctly!"
                    }]
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                result = response.content[0].text
                self.root.after(0, lambda: self.add_message(f"API Test Result: {result}", "claude"))
                self.root.after(0, lambda: self.add_message(f"Response time: {response_time:.2f} seconds", "system"))
                self.root.after(0, lambda: self.status_label.config(text="API test successful", foreground="green"))
                
            except Exception as e:
                error_msg = f"API Test Failed: {str(e)}"
                self.root.after(0, lambda: self.add_message(error_msg, "error"))
                self.root.after(0, lambda: self.add_message(f"Full error: {traceback.format_exc()}", "error"))
                self.root.after(0, lambda: self.status_label.config(text="API test failed", foreground="red"))
                
        thread = threading.Thread(target=api_test)
        thread.daemon = True
        thread.start()
        
    def send_message(self):
        """Send message to Claude"""
        message = self.input_field.get("1.0", tk.END).strip()
        if not message:
            return
            
        self.add_message(message, "user")
        self.input_field.delete("1.0", tk.END)
        
        # Show sending status
        self.send_button.configure(state=tk.DISABLED, text="Sending...")
        self.status_label.config(text="Claude is thinking...", foreground="orange")
        
        def send_to_claude():
            try:
                start_time = time.time()
                
                # Add to conversation
                self.conversation.append({
                    'role': 'user',
                    'content': message
                })
                
                # Send to Claude
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    temperature=0.7,
                    messages=self.conversation
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # Extract response
                claude_response = response.content[0].text
                
                # Add to conversation
                self.conversation.append({
                    'role': 'assistant',
                    'content': claude_response
                })
                
                # Update UI
                self.root.after(0, lambda: self.add_message(claude_response, "claude"))
                self.root.after(0, lambda: self.add_message(f"Response time: {response_time:.2f}s", "system"))
                self.root.after(0, self.handle_success)
                
            except Exception as e:
                error_msg = f"Message failed: {str(e)}"
                self.root.after(0, lambda: self.add_message(error_msg, "error"))
                self.root.after(0, lambda: self.add_message(f"Full error: {traceback.format_exc()}", "error"))
                self.root.after(0, self.handle_error)
                
        thread = threading.Thread(target=send_to_claude)
        thread.daemon = True
        thread.start()
        
    def handle_success(self):
        """Handle successful response"""
        self.send_button.configure(state=tk.NORMAL, text="Send")
        self.status_label.config(text="Ready", foreground="green")
        self.input_field.focus_set()
        
    def handle_error(self):
        """Handle error response"""
        self.send_button.configure(state=tk.NORMAL, text="Send")
        self.status_label.config(text="Error occurred", foreground="red")
        self.input_field.focus_set()

def main():
    root = tk.Tk()
    app = ClaudeTroubleshooter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
