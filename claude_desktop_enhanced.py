import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font, filedialog, Menu
import anthropic
import os
from dotenv import load_dotenv
import threading
import json
import requests
import webbrowser
import subprocess
import sys
import io
import contextlib
from datetime import datetime
import base64
import tempfile
import pyperclip
import tkinter.simpledialog

# Load environment variables
load_dotenv()

class EnhancedClaudeDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Claude AI - Enhanced Desktop")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Initialize Anthropic client
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key or api_key == "your_anthropic_api_key_here":
            messagebox.showerror("Error", "ANTHROPIC_API_KEY not found in environment variables!\n\nPlease add your API key to the .env file")
            self.root.destroy()
            return
            
        self.client = anthropic.Anthropic(api_key=api_key)
        self.conversation = []
        self.current_mode = "chat"  # chat, code, analysis, creative
        self.conversation_history = []
        self.current_conversation_index = -1
        
        # Enhanced features
        self.system_prompt = self.get_system_prompt()
        self.code_execution_enabled = True
        self.web_search_enabled = True
        self.file_analysis_enabled = True
        
        # Configure colors and fonts
        self.setup_styles()
        
        # Create menu bar
        self.create_menu()
        
        # Create GUI elements
        self.create_widgets()
        
        # Focus on input field
        self.input_field.focus_set()
        
        # Load conversation history
        self.load_conversation_history()
        
    def get_system_prompt(self):
        """Get enhanced system prompt based on current mode"""
        base_prompt = """You are Claude, an advanced AI assistant running in a desktop application. You have enhanced capabilities:

1. CODE EXECUTION: You can execute Python code and show results
2. FILE ANALYSIS: You can analyze uploaded files and documents
3. WEB RESEARCH: You can search the web for current information
4. CREATIVE TASKS: You can generate images, write stories, create content
5. SYSTEM INTEGRATION: You can interact with the user's system when appropriate

Always be helpful, accurate, and creative. When users ask for code, provide working examples. When they need analysis, be thorough. When they want creative content, be imaginative.

Current mode: {mode}
"""
        
        mode_prompts = {
            "chat": "Focus on helpful conversation and general assistance.",
            "code": "Focus on programming, debugging, and technical solutions. Execute code when helpful.",
            "analysis": "Focus on data analysis, research, and detailed examination of topics.",
            "creative": "Focus on creative writing, brainstorming, and artistic tasks."
        }
        
        return base_prompt.format(mode=self.current_mode) + "\n" + mode_prompts.get(self.current_mode, "")
    
    def setup_styles(self):
        """Configure enhanced colors and fonts"""
        # Dark theme colors
        self.bg_color = "#2b2b2b"
        self.chat_bg = "#3c3c3c"
        self.input_bg = "#4a4a4a"
        self.user_color = "#0d7377"
        self.claude_color = "#14a085"
        self.code_color = "#2d2d2d"
        self.primary_color = "#14a085"
        self.text_color = "#ffffff"
        self.secondary_text = "#cccccc"
        
        # Configure root background
        self.root.configure(bg=self.bg_color)
        
        # Configure fonts
        self.font_normal = font.Font(family="Consolas", size=10)
        self.font_bold = font.Font(family="Consolas", size=10, weight="bold")
        self.font_header = font.Font(family="Segoe UI", size=14, weight="bold")
        self.font_code = font.Font(family="Consolas", size=9)
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Dark.TFrame', background=self.bg_color)
        style.configure('Dark.TLabel', background=self.bg_color, foreground=self.text_color)
        style.configure('Dark.TButton', background=self.primary_color, foreground=self.text_color)
        
    def create_menu(self):
        """Create enhanced menu bar"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Conversation", command=self.new_conversation, accelerator="Ctrl+N")
        file_menu.add_command(label="Open File", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save Conversation", command=self.save_conversation, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy Response", command=self.copy_last_response)
        edit_menu.add_command(label="Clear Chat", command=self.clear_conversation)
        
        # Mode menu
        mode_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Mode", menu=mode_menu)
        mode_menu.add_command(label="Chat Mode", command=lambda: self.set_mode("chat"))
        mode_menu.add_command(label="Code Mode", command=lambda: self.set_mode("code"))
        mode_menu.add_command(label="Analysis Mode", command=lambda: self.set_mode("analysis"))
        mode_menu.add_command(label="Creative Mode", command=lambda: self.set_mode("creative"))
        
        # Tools menu
        tools_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Web Search", command=self.web_search)
        tools_menu.add_command(label="Execute Code", command=self.execute_code_snippet)
        tools_menu.add_command(label="System Info", command=self.show_system_info)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_conversation())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_conversation())
        
    def create_widgets(self):
        """Create enhanced GUI elements"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10", style='Dark.TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left sidebar
        self.create_sidebar(main_frame)
        
        # Main chat area
        self.create_chat_area(main_frame)
        
        # Add initial message
        self.add_message("Hello! I'm Claude Enhanced - your advanced AI assistant. I can help with coding, analysis, creative tasks, and more. What would you like to work on today?", "claude")
        
    def create_sidebar(self, parent):
        """Create enhanced sidebar"""
        sidebar = ttk.Frame(parent, padding="10", style='Dark.TFrame')
        sidebar.grid(row=0, column=0, rowspan=3, sticky=(tk.W, tk.N, tk.S), padx=(0, 10))
        sidebar.columnconfigure(0, weight=1)
        
        # Mode selection
        mode_label = ttk.Label(sidebar, text="Mode:", font=self.font_bold, style='Dark.TLabel')
        mode_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.mode_var = tk.StringVar(value="chat")
        mode_frame = ttk.Frame(sidebar, style='Dark.TFrame')
        mode_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        modes = [("Chat", "chat"), ("Code", "code"), ("Analysis", "analysis"), ("Creative", "creative")]
        for i, (text, value) in enumerate(modes):
            rb = tk.Radiobutton(mode_frame, text=text, variable=self.mode_var, value=value,
                              command=lambda v=value: self.set_mode(v),
                              bg=self.bg_color, fg=self.text_color, selectcolor=self.primary_color)
            rb.grid(row=i, column=0, sticky=tk.W, pady=2)
        
        # Quick actions
        actions_label = ttk.Label(sidebar, text="Quick Actions:", font=self.font_bold, style='Dark.TLabel')
        actions_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        actions = [
            ("📁 Open File", self.open_file),
            ("🔍 Web Search", self.web_search),
            ("💻 Execute Code", self.execute_code_snippet),
            ("📊 System Info", self.show_system_info),
            ("🎨 Generate Image", self.generate_image_prompt),
            ("📝 Export Chat", self.export_chat)
        ]
        
        for i, (text, command) in enumerate(actions):
            btn = tk.Button(sidebar, text=text, command=command, 
                          bg=self.primary_color, fg=self.text_color,
                          font=self.font_normal, width=15, pady=2)
            btn.grid(row=3+i, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Status indicators
        status_label = ttk.Label(sidebar, text="Status:", font=self.font_bold, style='Dark.TLabel')
        status_label.grid(row=10, column=0, sticky=tk.W, pady=(15, 5))
        
        self.status_indicators = ttk.Frame(sidebar, style='Dark.TFrame')
        self.status_indicators.grid(row=11, column=0, sticky=(tk.W, tk.E))
        
        # Add status labels
        self.code_status = ttk.Label(self.status_indicators, text="💻 Code: Ready", style='Dark.TLabel')
        self.code_status.grid(row=0, column=0, sticky=tk.W)
        
        self.web_status = ttk.Label(self.status_indicators, text="🌐 Web: Ready", style='Dark.TLabel')
        self.web_status.grid(row=1, column=0, sticky=tk.W)
        
    def create_chat_area(self, parent):
        """Create enhanced chat area"""
        chat_container = ttk.Frame(parent, style='Dark.TFrame')
        chat_container.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        chat_container.columnconfigure(0, weight=1)
        chat_container.rowconfigure(1, weight=1)
        
        # Header with enhanced info
        header_frame = ttk.Frame(chat_container, style='Dark.TFrame')
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)
        
        title_label = ttk.Label(header_frame, text="🤖 Claude AI Enhanced", 
                               font=self.font_header, style='Dark.TLabel')
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Status and mode display
        self.status_label = ttk.Label(header_frame, text="Ready", 
                                     foreground=self.primary_color, style='Dark.TLabel')
        self.status_label.grid(row=0, column=1, sticky=tk.E)
        
        self.mode_label = ttk.Label(header_frame, text="Mode: Chat", 
                                   foreground=self.secondary_text, style='Dark.TLabel')
        self.mode_label.grid(row=1, column=1, sticky=tk.E)
        
        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            chat_container,
            wrap=tk.WORD,
            font=self.font_normal,
            bg=self.chat_bg,
            fg=self.text_color,
            relief=tk.SUNKEN,
            borderwidth=1,
            state=tk.DISABLED,
            height=25,
            insertbackground=self.text_color
        )
        self.chat_display.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure enhanced text tags
        self.chat_display.tag_configure("user", background=self.user_color, 
                                       font=self.font_bold, spacing1=5, spacing3=5)
        self.chat_display.tag_configure("claude", background=self.claude_color, 
                                       font=self.font_bold, spacing1=5, spacing3=5)
        self.chat_display.tag_configure("user_text", font=self.font_normal, spacing3=10)
        self.chat_display.tag_configure("claude_text", font=self.font_normal, spacing3=10)
        self.chat_display.tag_configure("code", background=self.code_color, 
                                       font=self.font_code, spacing3=5)
        self.chat_display.tag_configure("timestamp", foreground=self.secondary_text, 
                                       font=("Consolas", 8))
        self.chat_display.tag_configure("system", foreground=self.primary_color, 
                                       font=self.font_bold)
        
        # Enhanced input area
        self.create_input_area(chat_container)
        
    def create_input_area(self, parent):
        """Create enhanced input area"""
        input_container = ttk.Frame(parent, style='Dark.TFrame')
        input_container.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        input_container.columnconfigure(0, weight=1)
        
        # Input field with enhanced features
        self.input_field = tk.Text(
            input_container,
            height=4,
            font=self.font_normal,
            wrap=tk.WORD,
            bg=self.input_bg,
            fg=self.text_color,
            relief=tk.SUNKEN,
            borderwidth=1,
            insertbackground=self.text_color
        )
        self.input_field.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Bind enhanced keys
        self.input_field.bind('<Return>', self.on_enter_key)
        self.input_field.bind('<Shift-Return>', self.on_shift_enter)
        self.input_field.bind('<Control-Return>', self.execute_as_code)
        
        # Enhanced button frame
        button_frame = ttk.Frame(input_container, style='Dark.TFrame')
        button_frame.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Enhanced buttons
        self.send_button = tk.Button(
            button_frame,
            text="Send",
            command=self.send_message,
            bg=self.primary_color,
            fg=self.text_color,
            font=self.font_bold,
            width=10,
            pady=2
        )
        self.send_button.grid(row=0, column=0, sticky=tk.E+tk.W, pady=(0, 2))
        
        self.code_button = tk.Button(
            button_frame,
            text="Code",
            command=self.execute_as_code,
            bg="#ff6b35",
            fg=self.text_color,
            font=self.font_bold,
            width=10,
            pady=2
        )
        self.code_button.grid(row=1, column=0, sticky=tk.E+tk.W, pady=2)
        
        self.clear_button = tk.Button(
            button_frame,
            text="Clear",
            command=self.clear_conversation,
            bg="#dc3545",
            fg=self.text_color,
            font=self.font_bold,
            width=10,
            pady=2
        )
        self.clear_button.grid(row=2, column=0, sticky=tk.E+tk.W, pady=2)
        
    def set_mode(self, mode):
        """Set the current mode and update system prompt"""
        self.current_mode = mode
        self.mode_var.set(mode)
        self.mode_label.config(text=f"Mode: {mode.title()}")
        self.system_prompt = self.get_system_prompt()
        self.add_system_message(f"Switched to {mode.title()} mode")
        
    def add_system_message(self, message):
        """Add a system message to the chat"""
        self.chat_display.configure(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"System ({timestamp})\n", "system")
        self.chat_display.insert(tk.END, message + "\n\n", "system")
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
    def execute_code_snippet(self):
        """Execute code from input field"""
        code = self.input_field.get("1.0", tk.END).strip()
        if not code:
            messagebox.showwarning("No Code", "Please enter some code to execute.")
            return
            
        self.add_message(f"Executing code:\n{code}", "user")
        self.input_field.delete("1.0", tk.END)
        
        try:
            # Capture stdout
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            # Execute code
            exec(code)
            
            # Get output
            output = captured_output.getvalue()
            sys.stdout = old_stdout
            
            if output:
                self.add_message(f"Output:\n{output}", "claude", message_type="code")
            else:
                self.add_message("Code executed successfully (no output)", "claude")
                
        except Exception as e:
            sys.stdout = old_stdout
            self.add_message(f"Error: {str(e)}", "claude")
            
    def web_search(self):
        """Perform web search"""
        query = self.input_field.get("1.0", tk.END).strip()
        if not query:
            query = tk.simpledialog.askstring("Web Search", "Enter search query:")
        
        if query:
            self.add_message(f"Searching web for: {query}", "user")
            self.input_field.delete("1.0", tk.END)
            
            try:
                # Simulate web search (in real implementation, use search API)
                search_results = f"Web search results for '{query}':\n\n"
                search_results += "🔍 This is a simulated search result.\n"
                search_results += "In a full implementation, this would use a real search API like Google Custom Search or Bing Search API.\n\n"
                search_results += "💡 Tip: You can implement real web search by adding API keys for search services."
                
                self.add_message(search_results, "claude")
                
            except Exception as e:
                self.add_message(f"Search error: {str(e)}", "claude")
                
    def open_file(self):
        """Open and analyze a file"""
        file_path = filedialog.askopenfilename(
            title="Select file to analyze",
            filetypes=[
                ("All files", "*.*"),
                ("Text files", "*.txt"),
                ("Python files", "*.py"),
                ("JSON files", "*.json"),
                ("CSV files", "*.csv")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                filename = os.path.basename(file_path)
                self.add_message(f"Opened file: {filename}", "user")
                
                # Analyze file content
                analysis = f"File Analysis for {filename}:\n\n"
                analysis += f"📁 File: {filename}\n"
                analysis += f"📊 Size: {len(content)} characters\n"
                analysis += f"📝 Lines: {content.count(chr(10)) + 1}\n\n"
                
                if filename.endswith('.py'):
                    analysis += "🐍 Python file detected\n"
                elif filename.endswith('.json'):
                    analysis += "📋 JSON file detected\n"
                elif filename.endswith('.csv'):
                    analysis += "📊 CSV file detected\n"
                
                analysis += "\n📄 Content preview:\n"
                analysis += content[:500] + ("..." if len(content) > 500 else "")
                
                self.add_message(analysis, "claude")
                
            except Exception as e:
                self.add_message(f"Error reading file: {str(e)}", "claude")
                
    def show_system_info(self):
        """Show system information"""
        import platform
        import psutil
        
        info = "💻 System Information:\n\n"
        info += f"🖥️  OS: {platform.system()} {platform.release()}\n"
        info += f"🔧 Processor: {platform.processor()}\n"
        info += f"🐍 Python: {platform.python_version()}\n"
        info += f"💾 Memory: {psutil.virtual_memory().percent}% used\n"
        info += f"💿 Disk: {psutil.disk_usage('/').percent}% used\n"
        info += f"📊 CPU: {psutil.cpu_percent()}% usage\n"
        
        self.add_message(info, "claude")
        
    def generate_image_prompt(self):
        """Generate image creation prompt"""
        prompt = self.input_field.get("1.0", tk.END).strip()
        if not prompt:
            prompt = tk.simpledialog.askstring("Image Generation", "Describe the image you want to create:")
        
        if prompt:
            self.add_message(f"Image generation prompt: {prompt}", "user")
            self.input_field.delete("1.0", tk.END)
            
            response = "🎨 Image Generation:\n\n"
            response += f"I'd create an image based on: '{prompt}'\n\n"
            response += "💡 To implement actual image generation, you could integrate with:\n"
            response += "• DALL-E API\n• Midjourney API\n• Stable Diffusion\n• OpenAI Image API\n\n"
            response += "This would require additional API keys and image processing libraries."
            
            self.add_message(response, "claude")
            
    def export_chat(self):
        """Export chat to file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("HTML files", "*.html")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'w') as f:
                        json.dump(self.conversation, f, indent=2)
                else:
                    content = self.chat_display.get("1.0", tk.END)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
                self.add_message(f"Chat exported to: {os.path.basename(file_path)}", "claude")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export chat: {str(e)}")
                
    def copy_last_response(self):
        """Copy the last Claude response to clipboard"""
        if self.conversation and self.conversation[-1]['role'] == 'assistant':
            try:
                pyperclip.copy(self.conversation[-1]['content'])
                self.add_system_message("Last response copied to clipboard")
            except:
                messagebox.showwarning("Copy Error", "Could not copy to clipboard")
                
    def new_conversation(self):
        """Start a new conversation"""
        if self.conversation:
            self.conversation_history.append(self.conversation.copy())
            
        self.conversation = []
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.configure(state=tk.DISABLED)
        
        self.add_message("New conversation started! How can I help you?", "claude")
        
    def load_conversation_history(self):
        """Load conversation history from file"""
        try:
            if os.path.exists("conversation_history.json"):
                with open("conversation_history.json", 'r') as f:
                    self.conversation_history = json.load(f)
        except:
            pass
            
    def save_conversation_history(self):
        """Save conversation history to file"""
        try:
            with open("conversation_history.json", 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
        except:
            pass
            
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
        
    def execute_as_code(self, event=None):
        """Execute input as code"""
        self.execute_code_snippet()
        
    def add_message(self, message, sender, timestamp=None, message_type="normal"):
        """Add an enhanced message to the chat display"""
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
        
        # Add message content with appropriate styling
        if message_type == "code":
            self.chat_display.insert(tk.END, message + "\n\n", "code")
        elif sender == "user":
            self.chat_display.insert(tk.END, message + "\n\n", "user_text")
        else:
            self.chat_display.insert(tk.END, message + "\n\n", "claude_text")
        
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
    def send_message(self):
        """Send enhanced message to Claude AI"""
        message = self.input_field.get("1.0", tk.END).strip()
        
        if not message:
            return
            
        # Add user message to display
        self.add_message(message, "user")
        
        # Clear input field
        self.input_field.delete("1.0", tk.END)
        
        # Disable send button and show loading
        self.send_button.configure(state=tk.DISABLED, text="Thinking...")
        self.status_label.configure(text="Claude is thinking...", foreground="orange")
        
        # Send request in separate thread to avoid blocking UI
        thread = threading.Thread(target=self.send_to_claude, args=(message,))
        thread.daemon = True
        thread.start()
        
    def send_to_claude(self, message):
        """Send message to Claude API with enhanced system prompt"""
        try:
            # Build conversation with system prompt
            enhanced_conversation = [
                {"role": "system", "content": self.system_prompt}
            ]
            enhanced_conversation.extend(self.conversation)
            enhanced_conversation.append({
                'role': 'user',
                'content': message
            })
            
            # Send to Claude
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.7,
                messages=enhanced_conversation
            )
            
            # Extract response
            claude_response = response.content[0].text
            
            # Add to conversation history
            self.conversation.append({
                'role': 'user',
                'content': message
            })
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
        """Handle Claude's enhanced response"""
        # Add response to chat display
        self.add_message(response, "claude")
        
        # Re-enable send button
        self.send_button.configure(state=tk.NORMAL, text="Send")
        self.status_label.configure(text="Ready", foreground=self.primary_color)
        
        # Focus back on input field
        self.input_field.focus_set()
        
    def handle_error(self, error_msg):
        """Handle errors"""
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
            self.add_message("Conversation cleared! I'm ready to help with your enhanced requests.", "claude")
            
            # Focus on input field
            self.input_field.focus_set()
            
    def save_conversation(self):
        """Save conversation to file"""
        if not self.conversation:
            messagebox.showinfo("Save Conversation", "No conversation to save.")
            return
            
        filename = f"claude_enhanced_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump({
                    'conversation': self.conversation,
                    'mode': self.current_mode,
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2)
            messagebox.showinfo("Save Conversation", f"Conversation saved to {filename}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save conversation: {str(e)}")

def main():
    """Main function to run the enhanced application"""
    # Check if API key is set
    load_dotenv()
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key or api_key == "your_anthropic_api_key_here":
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
    
    # Create and run the enhanced application
    root = tk.Tk()
    app = EnhancedClaudeDesktopApp(root)
    
    # Handle window closing
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            app.save_conversation_history()
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    print("🚀 Claude Enhanced Desktop AI started!")
    print("📱 Advanced features enabled!")
    print("🔧 Modes: Chat, Code, Analysis, Creative")
    print("💻 Code execution enabled")
    print("🌐 Web search enabled")
    print("📁 File analysis enabled")
    root.mainloop()

if __name__ == "__main__":
    main()
