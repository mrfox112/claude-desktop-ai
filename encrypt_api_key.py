#!/usr/bin/env python3
"""
API Key Encryption Utility for Claude Desktop AI
This script helps users encrypt their API keys for secure storage
"""

import os
import sys
import getpass
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def encrypt_api_key_interactive():
    """Interactive API key encryption"""
    print("🔐 Claude Desktop AI - API Key Encryption Utility")
    print("=" * 50)
    print()
    
    try:
        from security_manager import encrypt_api_key, SecurityManager
        
        print("This utility will help you encrypt your Anthropic API key for secure storage.")
        print("The encrypted key can be stored in your .env file as ENCRYPTED_ANTHROPIC_API_KEY")
        print()
        
        # Get API key from user
        api_key = getpass.getpass("Enter your Anthropic API key: ")
        
        if not api_key:
            print("❌ No API key provided. Exiting.")
            return False
        
        # Validate API key format (basic check)
        if not api_key.startswith(('sk-', 'claude-')):
            print("⚠️  Warning: API key doesn't start with expected prefix (sk- or claude-)")
            confirm = input("Continue anyway? (y/N): ").lower()
            if confirm != 'y':
                print("Encryption cancelled.")
                return False
        
        print("\n🔒 Encrypting API key...")
        
        # Encrypt the API key
        encrypted_key = encrypt_api_key(api_key)
        
        print("✅ API key encrypted successfully!")
        print()
        print("Encrypted API key:")
        print("=" * 50)
        print(encrypted_key)
        print("=" * 50)
        print()
        
        # Provide instructions
        print("📝 Instructions:")
        print("1. Copy the encrypted key above")
        print("2. Add it to your .env file as:")
        print(f"   ENCRYPTED_ANTHROPIC_API_KEY={encrypted_key}")
        print("3. Remove or comment out the plain ANTHROPIC_API_KEY line")
        print("4. The application will automatically use the encrypted key")
        print()
        
        # Optional: Save to file
        save_to_file = input("Save encrypted key to file? (y/N): ").lower()
        if save_to_file == 'y':
            filename = f"encrypted_api_key_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(f"# Encrypted API key generated on {datetime.now().isoformat()}\n")
                f.write(f"ENCRYPTED_ANTHROPIC_API_KEY={encrypted_key}\n")
            print(f"✅ Encrypted key saved to {filename}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure the security_manager module is available and cryptography is installed.")
        print("Run: pip install cryptography")
        return False
    except Exception as e:
        print(f"❌ Encryption failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def decrypt_api_key_interactive():
    """Interactive API key decryption (for testing)"""
    print("🔓 Claude Desktop AI - API Key Decryption Utility")
    print("=" * 50)
    print()
    
    try:
        from security_manager import decrypt_api_key
        
        print("This utility will help you decrypt an encrypted API key for testing.")
        print("⚠️  WARNING: This should only be used for testing purposes!")
        print()
        
        # Get encrypted API key from user
        encrypted_key = input("Enter the encrypted API key: ")
        
        if not encrypted_key:
            print("❌ No encrypted key provided. Exiting.")
            return False
        
        print("\n🔓 Decrypting API key...")
        
        # Decrypt the API key
        decrypted_key = decrypt_api_key(encrypted_key)
        
        print("✅ API key decrypted successfully!")
        print()
        print("Decrypted API key:")
        print("=" * 50)
        print(decrypted_key)
        print("=" * 50)
        print()
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure the security_manager module is available.")
        return False
    except Exception as e:
        print(f"❌ Decryption failed: {e}")
        print("The encrypted key may be invalid or corrupted.")
        return False

def test_encryption_decryption():
    """Test encryption and decryption"""
    print("🧪 Testing Encryption/Decryption...")
    
    try:
        from security_manager import encrypt_api_key, decrypt_api_key
        
        # Test with a sample key
        test_key = "sk-test-key-1234567890abcdef"
        
        print(f"Original key: {test_key}")
        
        # Encrypt
        encrypted = encrypt_api_key(test_key)
        print(f"Encrypted: {encrypted}")
        
        # Decrypt
        decrypted = decrypt_api_key(encrypted)
        print(f"Decrypted: {decrypted}")
        
        # Verify
        if decrypted == test_key:
            print("✅ Encryption/Decryption test passed!")
            return True
        else:
            print("❌ Encryption/Decryption test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def show_security_info():
    """Show security information"""
    print("🔒 Security Information")
    print("=" * 50)
    print()
    
    print("🔐 Encryption Details:")
    print("- Algorithm: AES-256 with Fernet")
    print("- Key Derivation: PBKDF2 with SHA-256")
    print("- Salt: 16 bytes, randomly generated")
    print("- Iterations: 100,000")
    print()
    
    print("🛡️  Security Features:")
    print("- Master password-based encryption")
    print("- Data integrity verification (HMAC)")
    print("- Secure session management")
    print("- API request rate limiting")
    print("- Audit logging")
    print()
    
    print("📝 Best Practices:")
    print("- Store encrypted keys in environment variables")
    print("- Use secure master passwords")
    print("- Regularly rotate API keys")
    print("- Monitor security audit logs")
    print("- Keep the security salt file secure")
    print()
    
    print("⚠️  Important Notes:")
    print("- The master password is auto-generated if not provided")
    print("- Store the master password securely")
    print("- Back up the security salt file")
    print("- Don't share encrypted keys without proper authorization")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'encrypt':
            success = encrypt_api_key_interactive()
        elif command == 'decrypt':
            success = decrypt_api_key_interactive()
        elif command == 'test':
            success = test_encryption_decryption()
        elif command == 'info':
            show_security_info()
            success = True
        else:
            print(f"Unknown command: {command}")
            success = False
    else:
        print("🔐 Claude Desktop AI - API Key Encryption Utility")
        print("=" * 50)
        print()
        print("Usage:")
        print("  python encrypt_api_key.py encrypt    - Encrypt an API key")
        print("  python encrypt_api_key.py decrypt    - Decrypt an API key (testing)")
        print("  python encrypt_api_key.py test       - Test encryption/decryption")
        print("  python encrypt_api_key.py info       - Show security information")
        print()
        print("Examples:")
        print("  python encrypt_api_key.py encrypt")
        print("  python encrypt_api_key.py test")
        print()
        
        # Interactive mode
        print("Or run interactively:")
        while True:
            print()
            print("Options:")
            print("1. Encrypt API key")
            print("2. Decrypt API key (testing)")
            print("3. Test encryption/decryption")
            print("4. Show security information")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                encrypt_api_key_interactive()
            elif choice == '2':
                decrypt_api_key_interactive()
            elif choice == '3':
                test_encryption_decryption()
            elif choice == '4':
                show_security_info()
            elif choice == '5':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
        
        success = True
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
