#!/usr/bin/env python3
"""
Simple launcher for Claude Desktop AI
"""

import sys
import os
import subprocess

def main():
    print("🚀 Starting Claude Desktop AI...")
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not sys.base_prefix != sys.prefix:
        print("⚠️  Virtual environment not detected.")
        print("💡 Consider activating the virtual environment first:")
        print("   .\\venv\\Scripts\\activate")
        print()
    
    # Check if API key exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please run setup.ps1 first or copy .env.example to .env")
        input("Press Enter to exit...")
        return
    
    # Run the desktop application
    try:
        subprocess.run([sys.executable, "claude_desktop.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Claude Desktop AI closed by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running application: {e}")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
