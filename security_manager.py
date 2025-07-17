"""
Enhanced Security Manager for Claude Desktop AI
Provides encryption, secure API calls, and data integrity protection
"""

import os
import hashlib
import hmac
import secrets
import base64
import json
import sqlite3
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import ssl
import urllib.request
import urllib.parse
import urllib.error
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    encryption_key_length: int = 32
    salt_length: int = 16
    hash_algorithm: str = 'sha256'
    max_failed_attempts: int = 3
    lockout_duration: int = 300  # 5 minutes
    session_timeout: int = 3600  # 1 hour
    api_timeout: int = 30
    max_retries: int = 3
    backoff_factor: float = 0.5

class EncryptionManager:
    """Handles encryption and decryption of sensitive data"""
    
    def __init__(self, master_password: str = None):
        """Initialize encryption manager with master password"""
        self.config = SecurityConfig()
        self._master_password = master_password or self._get_master_password()
        self._encryption_key = None
        self._salt = None
        self._initialize_encryption()
    
    def _get_master_password(self) -> str:
        """Get master password from environment or generate one"""
        master_password = os.environ.get('CLAUDE_MASTER_PASSWORD')
        if not master_password:
            # Generate a secure master password
            master_password = secrets.token_urlsafe(32)
            logger.warning("Generated new master password. Store it securely!")
            logger.info(f"Master password: {master_password}")
        return master_password
    
    def _initialize_encryption(self):
        """Initialize encryption key and salt"""
        # Generate or load salt
        salt_file = '.security_salt'
        if os.path.exists(salt_file):
            with open(salt_file, 'rb') as f:
                self._salt = f.read()
        else:
            self._salt = os.urandom(self.config.salt_length)
            with open(salt_file, 'wb') as f:
                f.write(self._salt)
            # Set restrictive permissions
            os.chmod(salt_file, 0o600)
        
        # Derive encryption key from master password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.config.encryption_key_length,
            salt=self._salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self._master_password.encode()))
        self._encryption_key = Fernet(key)
    
    def encrypt_data(self, data: Union[str, bytes]) -> str:
        """Encrypt data and return base64 encoded string"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted_data = self._encryption_key.encrypt(data)
        return base64.urlsafe_b64encode(encrypted_data).decode('ascii')
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt base64 encoded encrypted data"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('ascii'))
            decrypted_data = self._encryption_key.decrypt(encrypted_bytes)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise SecurityException("Failed to decrypt data")
    
    def encrypt_file(self, file_path: str, encrypted_path: str = None) -> str:
        """Encrypt file and save to encrypted path"""
        if not encrypted_path:
            encrypted_path = f"{file_path}.encrypted"
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            encrypted_data = self._encryption_key.encrypt(data)
            
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Set restrictive permissions
            os.chmod(encrypted_path, 0o600)
            
            return encrypted_path
        except Exception as e:
            logger.error(f"File encryption failed: {e}")
            raise SecurityException("Failed to encrypt file")
    
    def decrypt_file(self, encrypted_path: str, output_path: str = None) -> str:
        """Decrypt file and save to output path"""
        if not output_path:
            output_path = encrypted_path.replace('.encrypted', '')
        
        try:
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self._encryption_key.decrypt(encrypted_data)
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            return output_path
        except Exception as e:
            logger.error(f"File decryption failed: {e}")
            raise SecurityException("Failed to decrypt file")

class IntegrityManager:
    """Manages data integrity verification"""
    
    def __init__(self, secret_key: str = None):
        """Initialize integrity manager with secret key"""
        self.secret_key = secret_key or os.environ.get('CLAUDE_INTEGRITY_KEY', secrets.token_urlsafe(32))
    
    def generate_hash(self, data: Union[str, bytes]) -> str:
        """Generate HMAC-SHA256 hash for data"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        hmac_hash = hmac.new(
            self.secret_key.encode('utf-8'),
            data,
            hashlib.sha256
        )
        return hmac_hash.hexdigest()
    
    def verify_integrity(self, data: Union[str, bytes], expected_hash: str) -> bool:
        """Verify data integrity using HMAC"""
        actual_hash = self.generate_hash(data)
        return hmac.compare_digest(actual_hash, expected_hash)
    
    def sign_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sign data with integrity hash"""
        data_str = json.dumps(data, sort_keys=True)
        signature = self.generate_hash(data_str)
        
        return {
            'data': data,
            'signature': signature,
            'timestamp': datetime.now().isoformat()
        }
    
    def verify_signed_data(self, signed_data: Dict[str, Any]) -> bool:
        """Verify signed data integrity"""
        try:
            data = signed_data['data']
            signature = signed_data['signature']
            
            data_str = json.dumps(data, sort_keys=True)
            return self.verify_integrity(data_str, signature)
        except KeyError:
            logger.error("Invalid signed data format")
            return False

class SecureAPIManager:
    """Manages secure API calls with retry logic and security measures"""
    
    def __init__(self, config: SecurityConfig = None):
        """Initialize secure API manager"""
        self.config = config or SecurityConfig()
        self.session = self._create_secure_session()
        self.failed_attempts = {}
        self.lockout_times = {}
    
    def _create_secure_session(self) -> requests.Session:
        """Create secure requests session with retry strategy"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set secure defaults
        session.headers.update({
            'User-Agent': 'Claude-Desktop-AI/2.0 (Secure)',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        return session
    
    def _is_locked_out(self, endpoint: str) -> bool:
        """Check if endpoint is locked out due to failed attempts"""
        if endpoint not in self.lockout_times:
            return False
        
        lockout_time = self.lockout_times[endpoint]
        if datetime.now() - lockout_time > timedelta(seconds=self.config.lockout_duration):
            # Lockout expired
            del self.lockout_times[endpoint]
            if endpoint in self.failed_attempts:
                del self.failed_attempts[endpoint]
            return False
        
        return True
    
    def _record_failed_attempt(self, endpoint: str):
        """Record failed attempt and lock out if necessary"""
        self.failed_attempts[endpoint] = self.failed_attempts.get(endpoint, 0) + 1
        
        if self.failed_attempts[endpoint] >= self.config.max_failed_attempts:
            self.lockout_times[endpoint] = datetime.now()
            logger.warning(f"Endpoint {endpoint} locked out due to failed attempts")
    
    def _reset_failed_attempts(self, endpoint: str):
        """Reset failed attempts for successful request"""
        if endpoint in self.failed_attempts:
            del self.failed_attempts[endpoint]
    
    def make_secure_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make secure API request with error handling and retries"""
        endpoint = urllib.parse.urlparse(url).netloc
        
        # Check if endpoint is locked out
        if self._is_locked_out(endpoint):
            raise SecurityException(f"Endpoint {endpoint} is locked out due to failed attempts")
        
        # Set timeout
        kwargs.setdefault('timeout', self.config.api_timeout)
        
        # Ensure HTTPS
        if url.startswith('http://'):
            logger.warning(f"Converting HTTP to HTTPS for {url}")
            url = url.replace('http://', 'https://', 1)
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Check for successful response
            if response.status_code < 400:
                self._reset_failed_attempts(endpoint)
                return response
            else:
                self._record_failed_attempt(endpoint)
                response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            self._record_failed_attempt(endpoint)
            logger.error(f"API request failed: {e}")
            raise APIException(f"API request failed: {e}")
        
        return response

class DatabaseSecurityManager:
    """Manages database security and encryption"""
    
    def __init__(self, db_path: str, encryption_manager: EncryptionManager):
        """Initialize database security manager"""
        self.db_path = db_path
        self.encryption_manager = encryption_manager
        self.integrity_manager = IntegrityManager()
        self._init_security_tables()
    
    def _init_security_tables(self):
        """Initialize security-related database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Security audit log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                user_agent TEXT,
                session_id TEXT,
                integrity_hash TEXT
            )
        ''')
        
        # Encrypted data store
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS encrypted_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_name TEXT UNIQUE NOT NULL,
                encrypted_value TEXT NOT NULL,
                integrity_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Failed authentication attempts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auth_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                success BOOLEAN DEFAULT FALSE,
                failure_reason TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_security_event(self, event_type: str, details: str = None, 
                          ip_address: str = None, user_agent: str = None,
                          session_id: str = None):
        """Log security event with integrity verification"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        event_data = {
            'event_type': event_type,
            'details': details,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        }
        
        # Generate integrity hash
        integrity_hash = self.integrity_manager.generate_hash(json.dumps(event_data, sort_keys=True))
        
        cursor.execute('''
            INSERT INTO security_audit_log 
            (event_type, details, ip_address, user_agent, session_id, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (event_type, details, ip_address, user_agent, session_id, integrity_hash))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Security event logged: {event_type}")
    
    def store_encrypted_data(self, key_name: str, data: str):
        """Store encrypted data in database"""
        encrypted_value = self.encryption_manager.encrypt_data(data)
        integrity_hash = self.integrity_manager.generate_hash(data)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO encrypted_data 
            (key_name, encrypted_value, integrity_hash, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (key_name, encrypted_value, integrity_hash))
        
        conn.commit()
        conn.close()
        
        self.log_security_event('DATA_ENCRYPTED', f'Key: {key_name}')
    
    def retrieve_encrypted_data(self, key_name: str) -> Optional[str]:
        """Retrieve and decrypt data from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT encrypted_value, integrity_hash FROM encrypted_data 
            WHERE key_name = ?
        ''', (key_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        encrypted_value, stored_hash = result
        
        try:
            decrypted_data = self.encryption_manager.decrypt_data(encrypted_value)
            
            # Verify integrity
            if not self.integrity_manager.verify_integrity(decrypted_data, stored_hash):
                self.log_security_event('INTEGRITY_VIOLATION', f'Key: {key_name}')
                raise SecurityException("Data integrity verification failed")
            
            self.log_security_event('DATA_DECRYPTED', f'Key: {key_name}')
            return decrypted_data
            
        except Exception as e:
            self.log_security_event('DECRYPTION_FAILED', f'Key: {key_name}, Error: {str(e)}')
            raise

class SessionSecurityManager:
    """Manages session security and authentication"""
    
    def __init__(self, db_security: DatabaseSecurityManager):
        """Initialize session security manager"""
        self.db_security = db_security
        self.active_sessions = {}
        self.config = SecurityConfig()
    
    def create_session(self, user_id: str = 'default') -> str:
        """Create secure session with timeout"""
        session_id = secrets.token_urlsafe(32)
        session_data = {
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'is_active': True
        }
        
        self.active_sessions[session_id] = session_data
        
        self.db_security.log_security_event(
            'SESSION_CREATED',
            f'User: {user_id}',
            session_id=session_id
        )
        
        return session_id
    
    def validate_session(self, session_id: str) -> bool:
        """Validate session and check for timeout"""
        if session_id not in self.active_sessions:
            return False
        
        session_data = self.active_sessions[session_id]
        
        # Check if session is still active
        if not session_data['is_active']:
            return False
        
        # Check for timeout
        time_since_activity = datetime.now() - session_data['last_activity']
        if time_since_activity.total_seconds() > self.config.session_timeout:
            self.invalidate_session(session_id, 'timeout')
            return False
        
        # Update last activity
        session_data['last_activity'] = datetime.now()
        return True
    
    def invalidate_session(self, session_id: str, reason: str = 'logout'):
        """Invalidate session"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['is_active'] = False
            
            self.db_security.log_security_event(
                'SESSION_INVALIDATED',
                f'Reason: {reason}',
                session_id=session_id
            )
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session_data in self.active_sessions.items():
            time_since_activity = current_time - session_data['last_activity']
            if time_since_activity.total_seconds() > self.config.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.invalidate_session(session_id, 'expired')

class SecurityException(Exception):
    """Custom exception for security-related errors"""
    pass

class APIException(Exception):
    """Custom exception for API-related errors"""
    pass

# Global instances for consistency
_global_encryption_manager = None
_global_integrity_manager = None

def _get_global_encryption_manager() -> EncryptionManager:
    """Get or create global encryption manager"""
    global _global_encryption_manager
    if _global_encryption_manager is None:
        _global_encryption_manager = EncryptionManager()
    return _global_encryption_manager

def _get_global_integrity_manager() -> IntegrityManager:
    """Get or create global integrity manager"""
    global _global_integrity_manager
    if _global_integrity_manager is None:
        _global_integrity_manager = IntegrityManager()
    return _global_integrity_manager

def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt API key - convenience function for backward compatibility"""
    try:
        encryption_manager = _get_global_encryption_manager()
        return encryption_manager.decrypt_data(encrypted_key)
    except Exception as e:
        logger.error(f"Failed to decrypt API key: {e}")
        # Fall back to treating it as plain text if decryption fails
        return encrypted_key

def encrypt_api_key(api_key: str) -> str:
    """Encrypt API key - convenience function"""
    encryption_manager = _get_global_encryption_manager()
    return encryption_manager.encrypt_data(api_key)

def create_secure_config(config_data: Dict[str, Any]) -> str:
    """Create secure configuration with encryption and integrity"""
    encryption_manager = _get_global_encryption_manager()
    integrity_manager = _get_global_integrity_manager()
    
    # Sign the configuration
    signed_config = integrity_manager.sign_data(config_data)
    
    # Encrypt the signed configuration
    encrypted_config = encryption_manager.encrypt_data(json.dumps(signed_config))
    
    return encrypted_config

def load_secure_config(encrypted_config: str) -> Dict[str, Any]:
    """Load and verify secure configuration"""
    encryption_manager = _get_global_encryption_manager()
    integrity_manager = _get_global_integrity_manager()
    
    try:
        # Decrypt configuration
        decrypted_config = encryption_manager.decrypt_data(encrypted_config)
        signed_config = json.loads(decrypted_config)
        
        # Verify integrity
        if not integrity_manager.verify_signed_data(signed_config):
            raise SecurityException("Configuration integrity verification failed")
        
        return signed_config['data']
        
    except Exception as e:
        logger.error(f"Failed to load secure configuration: {e}")
        raise SecurityException("Failed to load secure configuration")

# Main security manager class that orchestrates all security components
class SecurityManager:
    """Main security manager that coordinates all security components"""
    
    def __init__(self, db_path: str = "conversations.db"):
        """Initialize comprehensive security manager"""
        self.encryption_manager = EncryptionManager()
        self.integrity_manager = IntegrityManager()
        self.api_manager = SecureAPIManager()
        self.db_security = DatabaseSecurityManager(db_path, self.encryption_manager)
        self.session_manager = SessionSecurityManager(self.db_security)
        
        # Log initialization
        self.db_security.log_security_event('SECURITY_MANAGER_INITIALIZED')
    
    def secure_api_call(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make secure API call with all security measures"""
        return self.api_manager.make_secure_request(method, url, **kwargs)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.encryption_manager.encrypt_data(data)
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.encryption_manager.decrypt_data(encrypted_data)
    
    def store_secure_data(self, key: str, data: str):
        """Store data securely in database"""
        self.db_security.store_encrypted_data(key, data)
    
    def retrieve_secure_data(self, key: str) -> Optional[str]:
        """Retrieve secure data from database"""
        return self.db_security.retrieve_encrypted_data(key)
    
    def create_secure_session(self, user_id: str = 'default') -> str:
        """Create secure session"""
        return self.session_manager.create_session(user_id)
    
    def validate_session(self, session_id: str) -> bool:
        """Validate session"""
        return self.session_manager.validate_session(session_id)
    
    def cleanup_security(self):
        """Cleanup expired sessions and perform security maintenance"""
        self.session_manager.cleanup_expired_sessions()
        self.db_security.log_security_event('SECURITY_CLEANUP_PERFORMED')

if __name__ == "__main__":
    # Example usage
    security_manager = SecurityManager()
    
    # Example: Encrypt an API key
    api_key = "your-api-key-here"
    encrypted_key = security_manager.encrypt_sensitive_data(api_key)
    print(f"Encrypted API key: {encrypted_key}")
    
    # Example: Store secure data
    security_manager.store_secure_data("test_key", "sensitive_data")
    
    # Example: Retrieve secure data
    retrieved_data = security_manager.retrieve_secure_data("test_key")
    print(f"Retrieved data: {retrieved_data}")
