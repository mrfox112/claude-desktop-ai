import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font
import sys
import traceback
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_test():
    """Debug test function to identify issues"""
    print("🔍 Starting Claude Desktop AI Debug...")
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Check environment
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    print(f"🔑 API key configured: {bool(api_key and api_key != 'your_anthropic_api_key_here')}")
    
    # Test imports
    try:
        import anthropic
        print(f"✅ Anthropic library: {anthropic.__version__}")
    except Exception as e:
        print(f"❌ Anthropic import error: {e}")
        return False
    
    try:
        import psutil
        print(f"✅ psutil library: {psutil.__version__}")
    except Exception as e:
        print(f"❌ psutil import error: {e}")
        return False
    
    try:
        import pyperclip
        print(f"✅ pyperclip library available")
    except Exception as e:
        print(f"❌ pyperclip import error: {e}")
        return False
    
    # Test tkinter
    try:
        root = tk.Tk()
        root.title("Debug Test")
        root.geometry("300x200")
        
        label = tk.Label(root, text="Debug Test Window", font=("Arial", 12))
        label.pack(pady=20)
        
        button = tk.Button(root, text="Close", command=root.destroy)
        button.pack(pady=10)
        
        print("✅ Tkinter GUI test window created")
        
        # Don't show window, just test creation
        root.withdraw()
        root.destroy()
        
    except Exception as e:
        print(f"❌ Tkinter error: {e}")
        return False
    
    # Test API connection
    try:
        client = anthropic.Anthropic(api_key=api_key)
        print("✅ Anthropic client created successfully")
        
        # Test a simple API call
        print("🔄 Testing API connection...")
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hello"}]
        )
        print("✅ API connection successful")
        
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False
    
    print("🎉 All debug tests passed!")
    return True

class DebugClaudeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Claude AI - Debug Mode")
        self.root.geometry("800x600")
        
        # Create debug interface
        self.create_debug_interface()
        
        # Test API connection
        self.test_api_connection()
        
    def create_debug_interface(self):
        """Create debug interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Claude AI Debug Console", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Debug output area
        self.debug_output = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            height=25,
            width=80
        )
        self.debug_output.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=(10, 0))
        
        ttk.Button(button_frame, text="Run Debug Tests", 
                  command=self.run_debug_tests).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Test Original App", 
                  command=self.test_original_app).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Test Enhanced App", 
                  command=self.test_enhanced_app).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Log", 
                  command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        # Initial message
        self.log("🚀 Claude AI Debug Console Ready")
        self.log("Click 'Run Debug Tests' to start diagnostics")
        
    def log(self, message):
        """Log message to debug output"""
        self.debug_output.insert(tk.END, message + "\n")
        self.debug_output.see(tk.END)
        self.root.update_idletasks()
        
    def clear_log(self):
        """Clear debug log"""
        self.debug_output.delete(1.0, tk.END)
        
    def run_debug_tests(self):
        """Run all debug tests"""
        self.log("🔍 Starting comprehensive debug tests...")
        
        try:
            # Test 1: Environment
            self.log("\n📋 Test 1: Environment Check")
            self.log(f"Python: {sys.version}")
            self.log(f"Platform: {sys.platform}")
            self.log(f"Current directory: {os.getcwd()}")
            
            # Test 2: API Key
            self.log("\n🔑 Test 2: API Key Check")
            api_key = os.environ.get('ANTHROPIC_API_KEY')
            if api_key and api_key != 'your_anthropic_api_key_here':
                self.log("✅ API key is configured")
            else:
                self.log("❌ API key missing or not configured")
                return
            
            # Test 3: Library imports
            self.log("\n📚 Test 3: Library Imports")
            try:
                import anthropic
                self.log(f"✅ Anthropic: {anthropic.__version__}")
            except Exception as e:
                self.log(f"❌ Anthropic import failed: {e}")
                return
                
            try:
                import psutil
                self.log(f"✅ psutil: {psutil.__version__}")
            except Exception as e:
                self.log(f"❌ psutil import failed: {e}")
                
            try:
                import pyperclip
                self.log("✅ pyperclip available")
            except Exception as e:
                self.log(f"❌ pyperclip import failed: {e}")
            
            # Test 4: API Connection
            self.log("\n🌐 Test 4: API Connection")
            try:
                client = anthropic.Anthropic(api_key=api_key)
                self.log("✅ Client created successfully")
                
                # Simple API test
                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=20,
                    messages=[{"role": "user", "content": "Say 'API test successful'"}]
                )
                self.log("✅ API test successful")
                self.log(f"Response: {response.content[0].text}")
                
            except Exception as e:
                self.log(f"❌ API test failed: {e}")
                self.log(f"Error details: {traceback.format_exc()}")
                
            # Test 5: GUI Components
            self.log("\n🖥️ Test 5: GUI Components")
            try:
                test_window = tk.Toplevel(self.root)
                test_window.title("GUI Test")
                test_window.geometry("200x100")
                
                tk.Label(test_window, text="GUI Test").pack(pady=10)
                tk.Button(test_window, text="Close", 
                         command=test_window.destroy).pack(pady=5)
                
                self.log("✅ GUI components working")
                test_window.destroy()
                
            except Exception as e:
                self.log(f"❌ GUI test failed: {e}")
                
            self.log("\n🎉 Debug tests completed!")
            
        except Exception as e:
            self.log(f"❌ Unexpected error during debug: {e}")
            self.log(f"Traceback: {traceback.format_exc()}")
            
    def test_original_app(self):
        """Test the original app"""
        self.log("\n🔄 Testing original Claude Desktop app...")
        try:
            import claude_desktop
            self.log("✅ Original app module imported successfully")
            
            # Try to create the app (without showing it)
            test_root = tk.Toplevel(self.root)
            test_root.withdraw()  # Hide the window
            
            app = claude_desktop.ClaudeDesktopApp(test_root)
            self.log("✅ Original app created successfully")
            
            test_root.destroy()
            
        except Exception as e:
            self.log(f"❌ Original app test failed: {e}")
            self.log(f"Error details: {traceback.format_exc()}")
            
    def test_enhanced_app(self):
        """Test the enhanced app"""
        self.log("\n🔄 Testing enhanced Claude Desktop app...")
        try:
            import claude_desktop_enhanced
            self.log("✅ Enhanced app module imported successfully")
            
            # Try to create the app (without showing it)
            test_root = tk.Toplevel(self.root)
            test_root.withdraw()  # Hide the window
            
            app = claude_desktop_enhanced.EnhancedClaudeDesktopApp(test_root)
            self.log("✅ Enhanced app created successfully")
            
            test_root.destroy()
            
        except Exception as e:
            self.log(f"❌ Enhanced app test failed: {e}")
            self.log(f"Error details: {traceback.format_exc()}")
            
    def test_api_connection(self):
        """Test API connection on startup"""
        self.log("🔄 Testing API connection...")
        try:
            api_key = os.environ.get('ANTHROPIC_API_KEY')
            if not api_key or api_key == 'your_anthropic_api_key_here':
                self.log("❌ API key not configured")
                return
                
            client = anthropic.Anthropic(api_key=api_key)
            self.log("✅ API client created successfully")
            
        except Exception as e:
            self.log(f"❌ API connection failed: {e}")

def main():
    """Main debug function"""
    # First run console debug
    if debug_test():
        # If console debug passes, run GUI debug
        root = tk.Tk()
        app = DebugClaudeApp(root)
        root.mainloop()
    else:
        print("❌ Debug tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
