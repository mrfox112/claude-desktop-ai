# Local Claude AI Desktop

A local desktop application that provides a chat interface to interact with Claude AI through the Anthropic API.

## Features

- 🤖 **Desktop Claude AI Interface**: Chat with Claude AI through a native desktop application
- 💬 **Conversation History**: Maintains conversation context during your session
- 🎨 **Modern GUI**: Clean, native Windows interface using tkinter
- 🔒 **Privacy Focused**: Runs locally on your machine
- 🚀 **Easy Setup**: Simple installation and configuration process
- ⌨️ **Keyboard Shortcuts**: Enter to send, Shift+Enter for new line
- 💾 **No Browser Required**: Pure desktop application

## Enhanced Features

- 📊 **Conversation Analytics**: Real-time quality scoring and conversation metrics
- 🎯 **Universal Mode**: Combined capabilities for all conversation types (creative, analytical, coding, writing)
- 💾 **Persistent Storage**: Conversations automatically saved to SQLite database
- 📈 **Performance Monitoring**: Response time tracking and token usage analytics
- 🔧 **Configuration Management**: Customizable settings with GUI configuration panel
- 📤 **Export Capabilities**: Export conversations to JSON with full analytics
- 🧪 **Comprehensive Testing**: Full test suite for reliability and quality assurance
- 📝 **Feedback System**: Built-in user feedback collection and analytics dashboard
- 🔄 **Auto-save**: Automatic conversation persistence with quality assessment

## Prerequisites

- Python 3.7 or higher
- Anthropic API key (get one at [console.anthropic.com](https://console.anthropic.com/))

## Quick Start

### 1. Setup

Run the setup script:
```powershell
.\setup.ps1
```

Or manually:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

### 2. Configure API Key

Edit the `.env` file and add your Anthropic API key:
```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

### 3. Run the Desktop Application

**Option 1: Using the batch file (recommended)**
```batch
run_claude.bat
```

**Option 2: Direct Python execution**
```bash
python claude_desktop.py
```

**Option 3: Run tests**
```bash
python tests/test_suite.py
```

## Usage

1. Launch the application using one of the methods above
2. Type your message in the input field at the bottom
3. Press **Enter** to send your message to Claude
4. Press **Shift+Enter** to add a new line without sending
5. Wait for Claude's response in the chat area
6. Continue the conversation with context maintained
7. Use "Clear" button to start a new conversation
8. Close the window to exit the application

## Project Structure

```
claude-desktop-ai/
├── claude_desktop.py        # Main enhanced desktop application
├── feedback_system.py       # Feedback collection and analytics
├── run_claude.bat          # Windows batch launcher
├── requirements.txt        # Python dependencies
├── setup.ps1              # Setup script for Windows
├── .env.example           # Environment variables template
├── .env                  # Your environment variables (create this)
├── tests/
│   └── test_suite.py     # Comprehensive test suite
├── conversations.db       # SQLite database for conversation storage
├── feedback.db           # SQLite database for feedback data
└── README.md            # This file
```

## Configuration

You can modify the following settings in `claude_desktop.py`:

- **Claude Model**: Change the model in the `client.messages.create()` call
- **Max Tokens**: Adjust the `max_tokens` parameter
- **Temperature**: Modify the `temperature` for response creativity
- **Window Size**: Change the `geometry()` call in `__init__`
- **Colors**: Modify the color settings in `setup_styles()`

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your `.env` file contains a valid Anthropic API key
2. **Module Not Found**: Ensure you've activated the virtual environment and installed dependencies
3. **Import Errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`

### Getting Help

- Check the console output for error messages
- Verify your API key is valid at [console.anthropic.com](https://console.anthropic.com/)
- Make sure you have sufficient API credits

## Security Notes

- Never commit your `.env` file to version control
- Keep your API key secure and don't share it
- The application runs on localhost by default for security

## License

This project is open source and available under the MIT License.

---

Enjoy chatting with Claude locally! 🚀
