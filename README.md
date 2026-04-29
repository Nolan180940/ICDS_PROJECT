# Distributed Intelligent Chat System (ICDS)

A full-featured distributed chat system with AI integration, built for the NYU Shanghai ICS final project.

## 🌟 Features

### Core Features (100% Complete)
- ✅ **Socket-based Communication**: Real-time messaging using Python sockets
- ✅ **Multi-client Support**: Server handles multiple concurrent connections
- ✅ **Group Chat**: Multiple users can chat together
- ✅ **GUI Client**: Full-featured Tkinter interface

### GUI Requirements (Compulsory 50% + Bonus 10%)
- ✅ **Bidirectional Message Display**: Sent messages (right/blue) and received messages (left/gray)
- ✅ **Bug Fix**: `system_msg` explicitly reset after display to prevent repetition
- ✅ **Real-time Refresh**: Background thread for message reception without GUI freezing
- ✅ **Login Interface**: Username entry with bot persona selection (Bonus 10%)
- ✅ **Emoji Support**: Quick-insert emoji buttons

### Chat Bot Core (Selective 20%)
- ✅ **Basic Conversation**: Bot responds to user messages
- ✅ **Context Memory**: Maintains message history for contextual responses
- ✅ **Persona System**: Configurable personalities (helpful, humorous, serious, creative, advisor)
- ✅ **GUI Integration**: Bot messages shown with purple color and 🤖 icon

### Bonus Features (35%)
1. ✅ **Group Chat Interaction (5%)**: Bot joins as regular client, responds only to @Bot mentions
2. ✅ **Sentiment Analysis (10%)**: TextBlob analyzes emotions, displays emoji indicators (😊😐😡)
3. ✅ **Chat Summary (10%)**: `/summary` command summarizes recent 10 messages
4. ✅ **AI Image Generation (10%)**: `/aipic: description` command (simulated with fallback)

## 📁 Project Structure

```
/workspace/
├── server/
│   ├── __init__.py
│   └── chat_server.py          # Enhanced server with group chat support
├── client/
│   ├── __init__.py
│   ├── chat_client.py          # Base network client
│   ├── gui_client.py           # Main GUI application (entry point)
│   └── login_dialog.py         # Login window with persona selection
├── bot/
│   ├── __init__.py
│   ├── ai_bot.py               # AI chatbot with Ollama integration
│   ├── sentiment_analyzer.py   # TextBlob sentiment analysis
│   └── summary_generator.py    # Chat history summarization
├── utils/
│   ├── __init__.py
│   └── chat_utils.py           # Network utilities
├── config/
│   ├── __init__.py
│   └── settings.py             # Configuration constants
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

For TextBlob corpus (improves sentiment analysis):
```bash
python -m textblob.download_corpora
```

### 2. Install Ollama (Optional, for AI features)

**Linux/macOS:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull phi3:mini
```

**Windows:**
Download from https://ollama.com/download

Verify Ollama is running:
```bash
ollama list
# Should show phi3:mini model
```

### 3. Start the Server

```bash
cd /workspace
python -m server.chat_server
```

Expected output:
```
[SERVER] Starting on 127.0.0.1:1112
[SERVER] Server started, waiting for connections...
```

### 4. Start the GUI Client

In a new terminal:
```bash
cd /workspace
python -m client.gui_client
```

### 5. Login and Chat

1. Enter your username in the login dialog
2. Select a bot persona (optional)
3. Click "Login"
4. Start chatting!

## 💬 Usage Guide

### Basic Commands
| Command | Description |
|---------|-------------|
| `/help` | Show help message |
| `/users` | List online users |
| `/time` | Show server time |
| `/clear` | Clear chat display |
| `/quit` | Exit application |

### AI Bot Commands
| Command | Description |
|---------|-------------|
| `@Bot hello` | Chat with AI (must mention @Bot) |
| `/persona <name>` | Change bot personality |
| `/summary` | Summarize recent chat |
| `/aipic: sunset` | Generate AI image (simulated) |

### Bot Personas
- `helpful` - Friendly and assistive
- `humorous` - Witty and funny
- `serious` - Professional and formal
- `creative` - Imaginative responses
- `advisor` - Academic guidance

## 🔧 Configuration

Edit `config/settings.py` to customize:

```python
CHAT_IP = '127.0.0.1'      # Server address
CHAT_PORT = 1112           # Server port
OLLAMA_HOST = "http://localhost:11434"  # Ollama API
OLLAMA_MODEL = "phi3:mini"  # AI model
```

## 🎯 Grading Checklist

### GUI (50% Compulsory + 10% Bonus)
- [x] Bidirectional message display (sent/received)
- [x] Bug fix: system_msg reset after display
- [x] Real-time message refresh via threading
- [x] Login interface with persona selection

### Chat Bot (20%)
- [x] Basic conversation capability
- [x] Context memory (message_history)
- [x] Persona system with system_prompt
- [x] GUI integration with special styling

### Bonus (35%)
- [x] Group chat interaction (@Bot trigger)
- [x] Sentiment analysis with emoji
- [x] Chat summary (/summary command)
- [x] AI image generation (/aipic command)

## 🐛 Known Issues & Solutions

### Issue: "TextBlob not installed" warning
**Solution:** Install with `pip install textblob` and download corpora:
```bash
python -m textblob.download_corpora
```

### Issue: "Ollama not available" warning
**Solution:** 
1. Install Ollama from https://ollama.com
2. Pull the model: `ollama pull phi3:mini`
3. Start Ollama service

*Note: The system works without Ollama using fallback responses.*

### Issue: GUI doesn't open
**Solution:** Ensure tkinter is installed:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk
```

## 📝 Code Highlights

### Bug Fix Location
File: `client/gui_client.py`, method `_display_system()`:
```python
def _display_system(self, text: str):
    # BUG FIX: Explicitly clear system_msg before and after display
    self.system_msg = ""
    # ... display code ...
    self.system_msg = ""  # Reset after display
```

### Thread-Safe GUI Updates
All GUI updates go through the main thread:
```python
if threading.current_thread() is threading.main_thread():
    _insert()
else:
    self.root.after(0, _insert)
```

## 📄 License

This project is created for educational purposes as part of NYU Shanghai ICS final project.
