#!/usr/bin/env python3
"""
Auto-Update System for Ether AI
Handles automatic updates, version management, and rollback capabilities.
"""

import os
import sys
import json
import hashlib
import shutil
import tempfile
import subprocess
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
import logging
import zipfile
import threading
import time
from dataclasses import dataclass
from packaging import version

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_updater.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class UpdateInfo:
    """Information about an available update"""
    version: str
    release_date: str
    download_url: str
    changelog: str
    size: int
    checksum: str
    critical: bool = False
    dependencies: List[str] = None

class AutoUpdater:
    """Automatic update system for Ether AI"""
    
    def __init__(self, 
                 current_version: str = "2.1.0",
                 update_server: str = "https://api.github.com/repos/mrfox112/claude-desktop-ai",
                 check_interval: int = 3600):  # Check every hour
        self.current_version = current_version
        self.update_server = update_server
        self.check_interval = check_interval
        self.app_dir = Path(__file__).parent
        self.backup_dir = self.app_dir / "backups"
        self.temp_dir = self.app_dir / "temp"
        self.config_file = self.app_dir / "update_config.json"
        
        # Create directories
        self.backup_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        # Load configuration
        self.config = self.load_config()
        
        # Update check thread
        self.update_thread = None
        self.running = False
        
    def load_config(self) -> Dict:
        """Load update configuration"""
        default_config = {
            "auto_update": True,
            "check_interval": self.check_interval,
            "allow_beta": False,
            "backup_count": 5,
            "last_check": None,
            "update_channel": "stable"
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return {**default_config, **config}
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
        
        return default_config
    
    def save_config(self):
        """Save update configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def check_for_updates(self) -> Optional[UpdateInfo]:
        """Check for available updates"""
        try:
            logger.info("Checking for updates...")
            
            # Get latest release info from GitHub
            response = requests.get(f"{self.update_server}/releases/latest", timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            latest_version = release_data['tag_name'].lstrip('v')
            
            # Compare versions
            if version.parse(latest_version) > version.parse(self.current_version):
                # Find the appropriate asset
                asset = None
                for asset_data in release_data['assets']:
                    if asset_data['name'].endswith('.zip'):
                        asset = asset_data
                        break
                
                if asset:
                    update_info = UpdateInfo(
                        version=latest_version,
                        release_date=release_data['published_at'],
                        download_url=asset['browser_download_url'],
                        changelog=release_data['body'],
                        size=asset['size'],
                        checksum=asset.get('checksum', ''),
                        critical=self.is_critical_update(release_data['body'])
                    )
                    
                    logger.info(f"Update available: {latest_version}")
                    return update_info
            
            logger.info("No updates available")
            return None
            
        except Exception as e:
            logger.error(f"Failed to check for updates: {e}")
            return None
    
    def is_critical_update(self, changelog: str) -> bool:
        """Determine if an update is critical"""
        critical_keywords = ['security', 'critical', 'urgent', 'vulnerability', 'fix']
        return any(keyword in changelog.lower() for keyword in critical_keywords)
    
    def download_update(self, update_info: UpdateInfo) -> Optional[Path]:
        """Download update package"""
        try:
            logger.info(f"Downloading update {update_info.version}...")
            
            # Create temporary file
            temp_file = self.temp_dir / f"update_{update_info.version}.zip"
            
            # Download with progress
            response = requests.get(update_info.download_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        logger.info(f"Download progress: {progress:.1f}%")
            
            # Verify checksum if available
            if update_info.checksum:
                if not self.verify_checksum(temp_file, update_info.checksum):
                    logger.error("Checksum verification failed")
                    temp_file.unlink()
                    return None
            
            logger.info("Update downloaded successfully")
            return temp_file
            
        except Exception as e:
            logger.error(f"Failed to download update: {e}")
            return None
    
    def verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Verify file checksum"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            actual_checksum = sha256_hash.hexdigest()
            return actual_checksum == expected_checksum
            
        except Exception as e:
            logger.error(f"Failed to verify checksum: {e}")
            return False
    
    def create_backup(self) -> bool:
        """Create backup of current installation"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{self.current_version}_{timestamp}"
            backup_path = self.backup_dir / backup_name
            
            logger.info(f"Creating backup: {backup_name}")
            
            # Create backup archive
            shutil.make_archive(str(backup_path), 'zip', str(self.app_dir), 
                              ignore=shutil.ignore_patterns('backups', 'temp', '__pycache__', '*.pyc'))
            
            # Clean old backups
            self.cleanup_old_backups()
            
            logger.info("Backup created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
    
    def cleanup_old_backups(self):
        """Remove old backup files"""
        try:
            backups = list(self.backup_dir.glob("backup_*.zip"))
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Keep only the specified number of backups
            for backup in backups[self.config['backup_count']:]:
                backup.unlink()
                logger.info(f"Removed old backup: {backup.name}")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
    
    def install_update(self, update_file: Path) -> bool:
        """Install the downloaded update"""
        try:
            logger.info("Installing update...")
            
            # Create backup first
            if not self.create_backup():
                logger.error("Failed to create backup, aborting update")
                return False
            
            # Extract update
            with zipfile.ZipFile(update_file, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir / "update")
            
            update_dir = self.temp_dir / "update"
            
            # Copy files (excluding certain directories)
            exclude_dirs = {'backups', 'temp', 'logs', 'data', '__pycache__'}
            
            for item in update_dir.iterdir():
                if item.name not in exclude_dirs:
                    dest = self.app_dir / item.name
                    if item.is_dir():
                        if dest.exists():
                            shutil.rmtree(dest)
                        shutil.copytree(item, dest)
                    else:
                        shutil.copy2(item, dest)
            
            # Update version info
            self.update_version_info(update_file)
            
            # Cleanup temp files
            shutil.rmtree(self.temp_dir / "update")
            update_file.unlink()
            
            logger.info("Update installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install update: {e}")
            return False
    
    def update_version_info(self, update_file: Path):
        """Update version information"""
        try:
            # Extract version from update file name
            version_str = update_file.stem.split('_')[1]
            
            # Create version info file
            version_info = {
                "version": version_str,
                "update_date": datetime.now().isoformat(),
                "previous_version": self.current_version
            }
            
            with open(self.app_dir / "version_info.json", 'w') as f:
                json.dump(version_info, f, indent=2)
            
            self.current_version = version_str
            
        except Exception as e:
            logger.error(f"Failed to update version info: {e}")
    
    def rollback_update(self) -> bool:
        """Rollback to previous version"""
        try:
            logger.info("Rolling back update...")
            
            # Find most recent backup
            backups = list(self.backup_dir.glob("backup_*.zip"))
            if not backups:
                logger.error("No backups found")
                return False
            
            latest_backup = max(backups, key=lambda x: x.stat().st_mtime)
            
            # Extract backup
            with zipfile.ZipFile(latest_backup, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir / "rollback")
            
            rollback_dir = self.temp_dir / "rollback"
            
            # Restore files
            for item in rollback_dir.iterdir():
                dest = self.app_dir / item.name
                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
            
            # Cleanup
            shutil.rmtree(self.temp_dir / "rollback")
            
            logger.info("Rollback completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback: {e}")
            return False
    
    def start_background_check(self):
        """Start background update checking"""
        if self.running:
            return
            
        self.running = True
        self.update_thread = threading.Thread(target=self._background_check_loop, daemon=True)
        self.update_thread.start()
        logger.info("Background update checking started")
    
    def stop_background_check(self):
        """Stop background update checking"""
        self.running = False
        if self.update_thread:
            self.update_thread.join()
        logger.info("Background update checking stopped")
    
    def _background_check_loop(self):
        """Background update checking loop"""
        while self.running:
            try:
                if self.config['auto_update']:
                    update_info = self.check_for_updates()
                    if update_info:
                        if update_info.critical or self.config.get('auto_install', False):
                            self.perform_update(update_info)
                        else:
                            logger.info(f"Update {update_info.version} available (not auto-installing)")
                
                self.config['last_check'] = datetime.now().isoformat()
                self.save_config()
                
                # Wait for next check
                time.sleep(self.config['check_interval'])
                
            except Exception as e:
                logger.error(f"Error in background update check: {e}")
                time.sleep(60)  # Wait a minute before retrying
    
    def perform_update(self, update_info: UpdateInfo) -> bool:
        """Perform complete update process"""
        try:
            logger.info(f"Starting update to version {update_info.version}")
            
            # Download update
            update_file = self.download_update(update_info)
            if not update_file:
                return False
            
            # Install update
            if self.install_update(update_file):
                logger.info(f"Successfully updated to version {update_info.version}")
                return True
            else:
                logger.error("Update installation failed")
                return False
                
        except Exception as e:
            logger.error(f"Update process failed: {e}")
            return False
    
    def get_update_status(self) -> Dict:
        """Get current update status"""
        return {
            "current_version": self.current_version,
            "auto_update_enabled": self.config['auto_update'],
            "last_check": self.config.get('last_check'),
            "update_channel": self.config['update_channel'],
            "backup_count": len(list(self.backup_dir.glob("backup_*.zip")))
        }

def main():
    """Main function for standalone execution"""
    updater = AutoUpdater()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "check":
            update_info = updater.check_for_updates()
            if update_info:
                print(f"Update available: {update_info.version}")
                print(f"Release date: {update_info.release_date}")
                print(f"Size: {update_info.size} bytes")
                print(f"Critical: {update_info.critical}")
                print(f"Changelog: {update_info.changelog}")
            else:
                print("No updates available")
        
        elif command == "update":
            update_info = updater.check_for_updates()
            if update_info:
                if updater.perform_update(update_info):
                    print("Update completed successfully")
                else:
                    print("Update failed")
            else:
                print("No updates available")
        
        elif command == "rollback":
            if updater.rollback_update():
                print("Rollback completed successfully")
            else:
                print("Rollback failed")
        
        elif command == "status":
            status = updater.get_update_status()
            for key, value in status.items():
                print(f"{key}: {value}")
        
        else:
            print("Unknown command. Available commands: check, update, rollback, status")
    
    else:
        print("Auto-Updater for Ether AI")
        print("Usage: python auto_updater.py [check|update|rollback|status]")

if __name__ == "__main__":
    main()
