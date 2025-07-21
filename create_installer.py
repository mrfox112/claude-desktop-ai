#!/usr/bin/env python3
"""
Installer Creation System for Ether AI
Creates professional Windows installers with automatic dependency management.
"""

import os
import sys
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging
import zipfile
import requests
from jinja2 import Template

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InstallerBuilder:
    """Professional installer builder for Ether AI"""
    
    def __init__(self, app_dir: Path = None):
        self.app_dir = app_dir or Path(__file__).parent
        self.build_dir = self.app_dir / "build"
        self.dist_dir = self.app_dir / "dist"
        self.installer_dir = self.app_dir / "installer"
        self.version = "2.1.0"
        
        # Create directories
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        self.installer_dir.mkdir(exist_ok=True)
        
        # Load configuration
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load installer configuration"""
        config_file = self.app_dir / "installer_config.json"
        default_config = {
            "app_name": "Ether AI - Neural Interface",
            "app_version": self.version,
            "publisher": "Ether AI Team",
            "description": "Advanced AI Desktop Interface powered by Claude",
            "license": "MIT",
            "install_dir": "EtherAI",
            "create_desktop_shortcut": True,
            "create_start_menu": True,
            "auto_start": False,
            "include_dependencies": True,
            "compress_level": 6
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    return {**default_config, **config}
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
        
        return default_config
    
    def prepare_application(self) -> bool:
        """Prepare application files for packaging"""
        try:
            logger.info("Preparing application files...")
            
            # Create application directory
            app_build_dir = self.build_dir / "app"
            if app_build_dir.exists():
                shutil.rmtree(app_build_dir)
            app_build_dir.mkdir(parents=True)
            
            # Copy application files
            files_to_copy = [
                "claude_desktop.py",
                "auto_updater.py",
                "web_intelligence.py",
                "claude_intelligence.py",
                "advanced_ai_system.py",
                "memory_system.py",
                "model_optimizer.py",
                "feedback_system.py",
                "security_manager.py",
                "requirements.txt",
                "requirements-optional.txt",
                ".env.example",
                "README.md",
                "LICENSE"
            ]
            
            for file_name in files_to_copy:
                src = self.app_dir / file_name
                if src.exists():
                    if src.is_file():
                        shutil.copy2(src, app_build_dir / file_name)
                    else:
                        shutil.copytree(src, app_build_dir / file_name)
            
            # Copy directories
            dirs_to_copy = ["tests", ".github"]
            for dir_name in dirs_to_copy:
                src = self.app_dir / dir_name
                if src.exists():
                    shutil.copytree(src, app_build_dir / dir_name)
            
            # Create launcher script
            self.create_launcher_script(app_build_dir)
            
            # Create uninstaller
            self.create_uninstaller(app_build_dir)
            
            logger.info("Application files prepared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to prepare application: {e}")
            return False
    
    def create_launcher_script(self, app_dir: Path):
        """Create Windows launcher script"""
        launcher_template = '''@echo off
cd /d "%~dp0"
if not exist "venv\\Scripts\\activate.bat" (
    echo Setting up virtual environment...
    python -m venv venv
    call venv\\Scripts\\activate.bat
    pip install -r requirements.txt
    pip install -r requirements-optional.txt
) else (
    call venv\\Scripts\\activate.bat
)

if not exist ".env" (
    echo Setting up environment file...
    copy .env.example .env
    echo.
    echo Please edit .env file and add your Anthropic API key
    echo Then run this launcher again
    pause
    exit
)

echo Starting Ether AI...
python claude_desktop.py
pause
'''
        
        with open(app_dir / "launch_ether_ai.bat", 'w') as f:
            f.write(launcher_template)
    
    def create_uninstaller(self, app_dir: Path):
        """Create uninstaller script"""
        uninstaller_template = '''@echo off
echo Uninstalling Ether AI...
echo.
echo This will remove all Ether AI files and data.
echo.
set /p confirm=Are you sure? (Y/N): 
if /i not "%confirm%"=="Y" exit

echo Removing files...
cd /d "%~dp0"
cd ..
rmdir /s /q "EtherAI"

echo Removing shortcuts...
del "%USERPROFILE%\\Desktop\\Ether AI.lnk" 2>nul
del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Ether AI.lnk" 2>nul

echo Ether AI has been uninstalled successfully.
pause
'''
        
        with open(app_dir / "uninstall.bat", 'w') as f:
            f.write(uninstaller_template)
    
    def create_nsis_script(self) -> bool:
        """Create NSIS installer script"""
        try:
            logger.info("Creating NSIS installer script...")
            
            nsis_template = '''
# Ether AI Installer Script
!define APP_NAME "{{ config.app_name }}"
!define APP_VERSION "{{ config.app_version }}"
!define PUBLISHER "{{ config.publisher }}"
!define DESCRIPTION "{{ config.description }}"
!define LICENSE_FILE "LICENSE"
!define MAIN_APP_EXE "launch_ether_ai.bat"
!define INSTALL_DIR "{{ config.install_dir }}"
!define WEB_SITE "https://github.com/mrfox112/claude-desktop-ai"

# Installer properties
Name "${APP_NAME}"
OutFile "{{ dist_dir }}/EtherAI_Setup_{{ config.app_version }}.exe"
InstallDir "$PROGRAMFILES\\${INSTALL_DIR}"
InstallDirRegKey HKLM "Software\\${APP_NAME}" "Install_Dir"
RequestExecutionLevel admin
SetCompressor lzma
ShowInstDetails show
ShowUnInstDetails show

# Version information
VIProductVersion "{{ config.app_version }}.0"
VIAddVersionKey "ProductName" "${APP_NAME}"
VIAddVersionKey "ProductVersion" "${APP_VERSION}"
VIAddVersionKey "CompanyName" "${PUBLISHER}"
VIAddVersionKey "FileDescription" "${DESCRIPTION}"
VIAddVersionKey "LegalCopyright" "© 2025 ${PUBLISHER}"

# Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "${LICENSE_FILE}"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

# Languages
!insertmacro MUI_LANGUAGE "English"

# Installer section
Section "MainApp" SecMain
    SetOutPath $INSTDIR
    File /r "{{ app_build_dir }}\\*"
    
    # Create shortcuts
    {% if config.create_desktop_shortcut %}
    CreateShortCut "$DESKTOP\\${APP_NAME}.lnk" "$INSTDIR\\${MAIN_APP_EXE}" "" "$INSTDIR\\icon.ico"
    {% endif %}
    
    {% if config.create_start_menu %}
    CreateDirectory "$SMPROGRAMS\\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk" "$INSTDIR\\${MAIN_APP_EXE}" "" "$INSTDIR\\icon.ico"
    CreateShortCut "$SMPROGRAMS\\${APP_NAME}\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"
    {% endif %}
    
    # Write registry keys
    WriteRegStr HKLM "Software\\${APP_NAME}" "Install_Dir" "$INSTDIR"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "UninstallString" '"$INSTDIR\\uninstall.exe"'
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "Publisher" "${PUBLISHER}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "URLInfoAbout" "${WEB_SITE}"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "NoRepair" 1
    
    # Create uninstaller
    WriteUninstaller "$INSTDIR\\uninstall.exe"
SectionEnd

# Uninstaller section
Section "Uninstall"
    # Remove registry keys
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}"
    DeleteRegKey HKLM "Software\\${APP_NAME}"
    
    # Remove shortcuts
    Delete "$DESKTOP\\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\\${APP_NAME}\\*"
    RMDir "$SMPROGRAMS\\${APP_NAME}"
    
    # Remove files and directories
    RMDir /r "$INSTDIR"
SectionEnd
'''
            
            template = Template(nsis_template)
            nsis_content = template.render(
                config=self.config,
                app_build_dir=self.build_dir / "app",
                dist_dir=self.dist_dir
            )
            
            nsis_file = self.installer_dir / "installer.nsi"
            with open(nsis_file, 'w') as f:
                f.write(nsis_content)
            
            logger.info("NSIS script created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create NSIS script: {e}")
            return False
    
    def create_innosetup_script(self) -> bool:
        """Create Inno Setup installer script"""
        try:
            logger.info("Creating Inno Setup installer script...")
            
            inno_template = '''
[Setup]
AppName={{ config.app_name }}
AppVersion={{ config.app_version }}
AppPublisher={{ config.publisher }}
AppPublisherURL={{ config.web_site }}
AppSupportURL={{ config.web_site }}
AppUpdatesURL={{ config.web_site }}
DefaultDirName={autopf}\\{{ config.install_dir }}
DefaultGroupName={{ config.app_name }}
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir={{ dist_dir }}
OutputBaseFilename=EtherAI_Setup_{{ config.app_version }}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\\icon.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
Source: "{{ app_build_dir }}\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\\{{ config.app_name }}"; Filename: "{app}\\launch_ether_ai.bat"
Name: "{group}\\{cm:UninstallProgram,{{ config.app_name }}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\\{{ config.app_name }}"; Filename: "{app}\\launch_ether_ai.bat"; Tasks: desktopicon
Name: "{userappdata}\\Microsoft\\Internet Explorer\\Quick Launch\\{{ config.app_name }}"; Filename: "{app}\\launch_ether_ai.bat"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\\launch_ether_ai.bat"; Description: "{cm:LaunchProgram,{{ config.app_name }}}"; Flags: nowait postinstall skipifsilent
'''
            
            template = Template(inno_template)
            inno_content = template.render(
                config=self.config,
                app_build_dir=self.build_dir / "app",
                dist_dir=self.dist_dir
            )
            
            inno_file = self.installer_dir / "installer.iss"
            with open(inno_file, 'w') as f:
                f.write(inno_content)
            
            logger.info("Inno Setup script created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Inno Setup script: {e}")
            return False
    
    def build_installer(self, installer_type: str = "innosetup") -> bool:
        """Build the installer using specified tool"""
        try:
            logger.info(f"Building installer with {installer_type}...")
            
            if installer_type == "innosetup":
                return self.build_innosetup_installer()
            elif installer_type == "nsis":
                return self.build_nsis_installer()
            else:
                logger.error(f"Unknown installer type: {installer_type}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to build installer: {e}")
            return False
    
    def build_innosetup_installer(self) -> bool:
        """Build installer using Inno Setup"""
        try:
            # Look for Inno Setup compiler
            possible_paths = [
                "C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe",
                "C:\\Program Files\\Inno Setup 6\\ISCC.exe",
                "C:\\Program Files (x86)\\Inno Setup 5\\ISCC.exe",
                "C:\\Program Files\\Inno Setup 5\\ISCC.exe"
            ]
            
            iscc_path = None
            for path in possible_paths:
                if Path(path).exists():
                    iscc_path = path
                    break
            
            if not iscc_path:
                logger.error("Inno Setup not found. Please install Inno Setup.")
                return False
            
            # Compile installer
            cmd = [iscc_path, str(self.installer_dir / "installer.iss")]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Inno Setup installer built successfully")
                return True
            else:
                logger.error(f"Inno Setup compilation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to build Inno Setup installer: {e}")
            return False
    
    def build_nsis_installer(self) -> bool:
        """Build installer using NSIS"""
        try:
            # Look for NSIS compiler
            possible_paths = [
                "C:\\Program Files (x86)\\NSIS\\makensis.exe",
                "C:\\Program Files\\NSIS\\makensis.exe"
            ]
            
            makensis_path = None
            for path in possible_paths:
                if Path(path).exists():
                    makensis_path = path
                    break
            
            if not makensis_path:
                logger.error("NSIS not found. Please install NSIS.")
                return False
            
            # Compile installer
            cmd = [makensis_path, str(self.installer_dir / "installer.nsi")]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("NSIS installer built successfully")
                return True
            else:
                logger.error(f"NSIS compilation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to build NSIS installer: {e}")
            return False
    
    def create_portable_version(self) -> bool:
        """Create portable ZIP version"""
        try:
            logger.info("Creating portable version...")
            
            portable_name = f"EtherAI_Portable_{self.config['app_version']}.zip"
            portable_path = self.dist_dir / portable_name
            
            with zipfile.ZipFile(portable_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                app_dir = self.build_dir / "app"
                for root, dirs, files in os.walk(app_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arc_path = file_path.relative_to(app_dir)
                        zipf.write(file_path, arc_path)
            
            logger.info(f"Portable version created: {portable_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create portable version: {e}")
            return False
    
    def build_all(self) -> bool:
        """Build all installer types"""
        try:
            logger.info("Building all installers...")
            
            # Prepare application
            if not self.prepare_application():
                return False
            
            # Create installer scripts
            self.create_innosetup_script()
            self.create_nsis_script()
            
            # Try to build installers
            success = False
            
            # Try Inno Setup first
            if self.build_installer("innosetup"):
                success = True
            
            # Try NSIS as fallback
            if not success and self.build_installer("nsis"):
                success = True
            
            # Create portable version
            if self.create_portable_version():
                success = True
            
            if success:
                logger.info("Build completed successfully")
                return True
            else:
                logger.error("All build attempts failed")
                return False
                
        except Exception as e:
            logger.error(f"Build process failed: {e}")
            return False

def main():
    """Main function"""
    builder = InstallerBuilder()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "build":
            if builder.build_all():
                print("Build completed successfully!")
            else:
                print("Build failed!")
        elif command == "portable":
            if builder.prepare_application() and builder.create_portable_version():
                print("Portable version created successfully!")
            else:
                print("Failed to create portable version!")
        else:
            print("Unknown command. Available commands: build, portable")
    else:
        print("Installer Builder for Ether AI")
        print("Usage: python create_installer.py [build|portable]")

if __name__ == "__main__":
    main()
