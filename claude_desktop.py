import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font
import anthropic
import os
from dotenv import load_dotenv
import threading
import json
from datetime import datetime

# Load environment variables
load_dotenv()

class ClaudeDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Claude AI - Desktop")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Initialize Anthropic client
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            messagebox.showerror("Error", "ANTHROPIC_API_KEY not found in environment variables!\n\nPlease add your API key to the .env file")
            self.root.destroy()
            return
            
        self.client = anthropic.Anthropic(api_key=api_key)
        self.conversation = []
        
        # Configure colors and fonts
        self.setup_styles()
        
        # Create GUI elements
        self.create_widgets()
        
        # Focus on input field
        self.input_field.focus_set()
        
    def setup_styles(self):
        """Configure colors and fonts"""
        self.bg_color = "#f0f0f0"
        self.chat_bg = "#ffffff"
        self.user_color = "#e3f2fd"
        self.claude_color = "#f5f5f5"
        self.primary_color = "#1976d2"
        self.secondary_color = "#7b1fa2"
        
        # Configure root background
        self.root.configure(bg=self.bg_color)
        
        # Configure fonts
        self.font_normal = font.Font(family="Segoe UI", size=10)
        self.font_bold = font.Font(family="Segoe UI", size=10, weight="bold")
        self.font_header = font.Font(family="Segoe UI", size=14, weight="bold")
        
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
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)
        
        title_label = ttk.Label(header_frame, text="🤖 Claude AI Desktop", font=self.font_header)
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Status label
        self.status_label = ttk.Label(header_frame, text="Ready", foreground="green")
        self.status_label.grid(row=0, column=1, sticky=tk.E)
        
        # Chat display area
        chat_frame = ttk.Frame(main_frame)
        chat_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # Chat text area with scrollbar
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=self.font_normal,
            bg=self.chat_bg,
            relief=tk.SUNKEN,
            borderwidth=1,
            state=tk.DISABLED,
            height=20
        )
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for different message types
        self.chat_display.tag_configure("user", background=self.user_color, font=self.font_bold, spacing1=5, spacing3=5)
        self.chat_display.tag_configure("claude", background=self.claude_color, font=self.font_bold, spacing1=5, spacing3=5)
        self.chat_display.tag_configure("user_text", font=self.font_normal, spacing3=10)
        self.chat_display.tag_configure("claude_text", font=self.font_normal, spacing3=10)
        self.chat_display.tag_configure("timestamp", foreground="gray", font=("Segoe UI", 8))
        
        # Input area
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        # Input field
        self.input_field = tk.Text(
            input_frame,
            height=3,
            font=self.font_normal,
            wrap=tk.WORD,
            relief=tk.SUNKEN,
            borderwidth=1
        )
        self.input_field.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Bind Enter key (Shift+Enter for new line)
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
        self.clear_button.grid(row=1, column=0, sticky=tk.E+tk.W)
        
        # Add initial message
        self.add_message("Hello! I'm Claude, running locally on your desktop. How can I help you today?", "claude")
        
    def on_enter_key(self, event):
        """Handle Enter key press"""
        if event.state & 0x1:  # Shift key is pressed
            return None  # Allow normal newline
        else:
            self.send_message()
            return "break"  # Prevent default behavior
            
    def on_shift_enter(self, event):
        """Handle Shift+Enter key press"""
        return None  # Allow normal newline
        
    def add_message(self, message, sender, timestamp=None):
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
        self.chat_display.insert(tk.END, "\n")
        
        # Add message content
        if sender == "user":
            self.chat_display.insert(tk.END, message + "\n\n", "user_text")
        else:
            self.chat_display.insert(tk.END, message + "\n\n", "claude_text")
        
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
        
        # Disable send button and show loading
        self.send_button.configure(state=tk.DISABLED, text="Sending...")
        self.status_label.configure(text="Claude is thinking...", foreground="orange")
        
        # Send request in separate thread to avoid blocking UI
        thread = threading.Thread(target=self.send_to_claude, args=(message,))
        thread.daemon = True
        thread.start()
        
    def send_to_claude(self, message):
        """Send message to Claude API in background thread"""
        try:
            # Add user message to conversation
            self.conversation.append({
                'role': 'user',
                'content': message
            })
            
            # Send to Claude
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0.7,
                messages=self.conversation
            )
            
            # Extract response
            claude_response = response.content[0].text
            
            # Add Claude's response to conversation
            self.conversation.append({
                'role': 'assistant',
                'content': claude_response
            })
            
            # Update UI in main thread
            self.root.after(0, self.handle_claude_response, claude_response)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, self.handle_error, error_msg)
            
    def handle_claude_response(self, response):
        """Handle Claude's response in main thread"""
        # Add response to chat display
        self.add_message(response, "claude")
        
        # Re-enable send button
        self.send_button.configure(state=tk.NORMAL, text="Send")
        self.status_label.configure(text="Ready", foreground="green")
        
        # Focus back on input field
        self.input_field.focus_set()
        
    def handle_error(self, error_msg):
        """Handle errors in main thread"""
        # Show error message
        self.add_message(error_msg, "claude")
        
        # Re-enable send button
        self.send_button.configure(state=tk.NORMAL, text="Send")
        self.status_label.configure(text="Error", foreground="red")
        
        # Focus back on input field
        self.input_field.focus_set()
        
    def clear_conversation(self):
        """Clear the conversation history"""
        if messagebox.askyesno("Clear Conversation", "Are you sure you want to clear the conversation?"):
            self.conversation = []
            
            # Clear chat display
            self.chat_display.configure(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.configure(state=tk.DISABLED)
            
            # Add initial message
            self.add_message("Hello! I'm Claude, running locally on your desktop. How can I help you today?", "claude")
            
            # Focus on input field
            self.input_field.focus_set()
            
    def save_conversation(self):
        """Save conversation to file"""
        if not self.conversation:
            messagebox.showinfo("Save Conversation", "No conversation to save.")
            return
            
        filename = f"claude_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.conversation, f, indent=2)
            messagebox.showinfo("Save Conversation", f"Conversation saved to {filename}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save conversation: {str(e)}")

def main():
    """Main function to run the application"""
    # Check if API key is set
    load_dotenv()
    if not os.environ.get('ANTHROPIC_API_KEY'):
        root = tk.Tk()
        root.withdraw()  # Hide main window
        messagebox.showerror(
            "API Key Missing",
            "ANTHROPIC_API_KEY not found in environment variables!\n\n"
            "Please:\n"
            "1. Copy .env.example to .env\n"
            "2. Add your Anthropic API key to the .env file\n"
            "3. Get your API key from: https://console.anthropic.com/"
        )
        return
    
    # Create and run the application
    root = tk.Tk()
    app = ClaudeDesktopApp(root)
    
    # Handle window closing
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    print("🚀 Claude Desktop AI started!")
    print("📱 Desktop application is now running")
    root.mainloop()

if __name__ == "__main__":
    main()
