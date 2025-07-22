# Ether AI Desktop Setup Script

Write-Host "🚀 Setting up Ether AI Desktop..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ first." -ForegroundColor Red
    Write-Host "   Download from: https://python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Create virtual environment
Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "⬆️  Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install requirements
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️  IMPORTANT: Please edit .env file and add your Anthropic API key!" -ForegroundColor Red
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Test installation
Write-Host "🧪 Testing installation..." -ForegroundColor Yellow
try {
    python -c "import anthropic, tkinter; print('✅ Core dependencies working')"
    Write-Host "✅ Installation test passed" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Some dependencies may have issues" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file and add your Anthropic API key"
Write-Host "2. Run: .\run_claude.bat (or python claude_desktop.py)"
Write-Host "3. Enjoy your desktop AI interface!"
Write-Host ""
Write-Host "Get your API key at: https://console.anthropic.com/" -ForegroundColor Yellow
Write-Host "Need help? Check the README.md or open an issue on GitHub" -ForegroundColor Cyan
