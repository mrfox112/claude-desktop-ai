"""Basic tests for Ether AI Desktop application."""

import pytest
import os
import sys
import tempfile

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Test that core modules can be imported without errors."""
    try:
        import claude_desktop
        assert hasattr(claude_desktop, 'EtherAIDesktop')
    except ImportError as e:
        pytest.skip(f"Import failed due to missing dependencies: {e}")


def test_required_files_exist():
    """Test that all required files exist in the project."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    required_files = [
        'claude_desktop.py',
        'requirements.txt',
        'README.md',
        '.env.example',
        'run_claude.bat',
        'setup.ps1',
        'LICENSE'
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(project_root, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
    
    assert len(missing_files) == 0, f"Missing required files: {missing_files}"


def test_env_example_format():
    """Test that .env.example has proper format."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_example_path = os.path.join(project_root, '.env.example')
    
    if os.path.exists(env_example_path):
        with open(env_example_path, 'r') as f:
            content = f.read()
            assert 'ANTHROPIC_API_KEY' in content
            assert '=' in content


def test_requirements_format():
    """Test that requirements.txt is properly formatted."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    requirements_path = os.path.join(project_root, 'requirements.txt')
    
    with open(requirements_path, 'r') as f:
        content = f.read()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Check for essential dependencies
        has_anthropic = any('anthropic' in line for line in lines)
        has_dotenv = any('python-dotenv' in line for line in lines)
        
        assert has_anthropic, "requirements.txt missing anthropic dependency"
        assert has_dotenv, "requirements.txt missing python-dotenv dependency"


if __name__ == '__main__':
    pytest.main([__file__])
