# ICDS Final Project - Enhanced Chat System with GUI

A distributed chat system enhanced with a Graphical User Interface (GUI) and AI-powered features, built as part of the ICDS Spring 2026 Final Project at NYU Shanghai.

## 📋 Project Overview

This project extends a terminal-based distributed chat system by adding:
- **Graphical User Interface (GUI)** using Tkinter
- **AI Chatbot Integration** using Ollama local LLM models
- **Additional Features** for enhanced user experience

The system follows a client-server architecture where multiple clients can connect to a central server, exchange messages, and interact with AI-powered features.

## 🏗️ System Architecture

```
┌─────────────────┐         ┌─────────────────┐
│   Client 1      │         │   Client 2      │
│   (GUI + SM)    │         │   (GUI + SM)    │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │      Socket Connection    │
         └───────────┬───────────────┘
                     │
            ┌────────▼────────┐
            │  Chat Server    │
            │  - Message      │
            │    Routing      │
            │  - User Mgmt    │
            │  - Group Chat   │
            └─────────────────┘
                     │
            ┌────────▼────────┐
            │  ChatBot Client │
            │  (Ollama LLM)   │
            └─────────────────┘
```

## 📁 Project Structure

```
/workspace
├── chat_server.py          # Main server implementation
├── chat_client_class.py    # Base client class with socket handling
├── client_state_machine.py # Client state machine (offline, logged in, chatting)
├── chat_utils.py           # Utility functions and constants
├── chat_group.py           # Group chat management
├── indexer.py              # Message indexing for search functionality
├── chat_bot_client.py      # AI Chatbot integration (Ollama & OpenAI API)
├── ai_client.py            # Alternative AI client for Qwen model
├── chat_cmdl_client.py     # Command-line client (original version)
├── AllSonnets.txt          # Sonnet database for poem retrieval feature
└── demo/                   # Demo scripts for testing
```

## 🚀 Features

### Compulsory: Graphical User Interface (GUI)
- **Message Display Window**: Shows both sent and received messages in real-time
- **Text Input Area**: For composing messages
- **Send Button**: To transmit messages
- **Real-time Updates**: Messages appear instantly without refreshing
- **Clear Formatting**: Distinguishes between user messages and system notifications

### Selective Topics (Choose based on team size)

#### 1. AI Chatbot Integration 🤖
- **Local LLM Support**: Uses Ollama with models like Phi3, Llama3, Qwen
- **Context Awareness**: Maintains conversation history
- **Personality Mode**: Customizable bot personality
- **Group Chat Participation**: Bot can join multi-user conversations

#### 2. Online Gaming 🎮
- **Single Player with Leaderboard**: Submit scores to global ranking
- **Multiplayer Games**: Tic-Tac-Toe, chess, or other two-player games
- **Game Server Integration**: Uses chat system as communication backbone

#### 3. Bonus Topics (Up to 35% bonus points)
- **AI Picture Generation**: `/aipic: prompt` command generates images
- **NLP Chat Summary**: `/summary` and `/keywords` commands analyze chat history
- **Sentiment Analysis**: Detects emotion (Positive/Neutral/Negative) in messages

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Tkinter (usually included with Python)
- Required packages: `ollama`, `openai`, `requests`

### Step 1: Install Dependencies
```bash
pip install ollama openai requests
```

### Step 2: Install Ollama (for Local LLM)
Follow the installation guide: [Ollama Installation Guide](https://docs.google.com/document/d/1IYDQN9BLoUVgTNia2IcodHBjYO6n6kDQlrXFaH-pB54/edit)

After installation, pull a model:
```bash
ollama pull phi3:mini
```

### Step 3: Start the Server
```bash
python chat_server.py
```

### Step 4: Launch GUI Clients
```bash
# Create your GUI client script (e.g., gui_client.py)
python gui_client.py
```

## 💻 Usage

### Basic Chat Commands
- `time` - Get current system time
- `who` - List all online users
- `c <username>` - Connect to a specific user
- `? <term>` - Search chat history
- `p <number>` - Retrieve sonnet by number
- `q` - Quit the chat system

### AI Chatbot Commands (if implemented)
- `/chat <message>` - Send message to chatbot
- `/personality <type>` - Set bot personality
- `/invite` - Invite bot to group chat

### Bonus Feature Commands
- `/aipic: <prompt>` - Generate AI image
- `/summary` - Summarize recent chat
- `/keywords` - Extract keywords from chat

## 🔧 State Machine Design

The client uses a state machine with four states:
1. **S_OFFLINE (0)**: Initial state, not connected
2. **S_CONNECTED (1)**: Socket connected, awaiting login
3. **S_LOGGEDIN (2)**: User authenticated, can browse/list users
4. **S_CHATTING (3)**: Active conversation with peer(s)

## 📊 Message Protocol

All messages follow JSON format with size prefix:
```json
{
  "action": "login|connect|exchange|disconnect|list|search|poem|time",
  "name": "username",
  "target": "peer_name_or_term",
  "message": "content",
  "from": "sender_name",
  "status": "ok|duplicate|success|no-user"
}
```

## 🎯 Development Notes

### Using pi-mono (AI Code Assistant)
This project requires the use of pi-mono as an AI development assistant. Example usages:
- Generating code snippets for GUI components
- Debugging message handling logic
- Testing state machine transitions
- Understanding library documentation

### Known Issues & Fixes
- **GUI Message Reset Bug**: The sample GUI code intentionally contains a bug where `self.system_msg` is not reset after display. Fix by resetting the variable after each output operation.
- **Login Flow**: Ensure server returns proper "login success" response to prevent client stuck states.

## 👥 Team Information

**Team Members**: [Add your team members here]
**Section**: [Your section number]
**Registration**: [Link to team registration spreadsheet]

## 📹 Video Presentation

The 10-15 minute presentation video should include:
1. **Introduction** (6%): Project goals and motivation
2. **Demo** (6%): Feature showcase including pi-mono usage
3. **Discussion** (6%): Technical decisions and design choices
4. **Analysis** (6%): Reflections and future improvements
5. **Presentation Quality** (6%): Clarity and relevance

## 📝 Grading Breakdown

| Component | Weight | Description |
|-----------|--------|-------------|
| GUI Baseline | 40% | Send/receive/display messages correctly |
| GUI Extra Features | 10% | Login, emoji, file transfer, etc. |
| Selective Topic | 20% | Chatbot or Gaming implementation |
| GUI Integration | 10% | Feature integrated into GUI |
| Bonus Topics | Up to 35% | AI image, NLP summary, sentiment analysis |
| Video Presentation | 30% | 10-15 min video with all sections |

## 🔗 Resources

- [Final Project Guidelines](https://docs.google.com/document/d/1TSLpymBn7Mur6-wI3gviA19aigCKEGB_k9yqSqLXu3U/edit)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Ollama Python Library](https://github.com/ollama/ollama-python)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [GitHub & VSCode Collaboration Tutorial](https://www.youtube.com/playlist?list=PLpPVLI0A0OkLBWbcctmGxxF6VHWSQw1hi)

## 📅 Important Deadlines

- **Team Formation**: April 22, 2026
- **Project Submission**: May 10, 2026
  - Source code
  - Presentation slides
  - 10-15 minute video presentation

## 🙏 Acknowledgments

- Course Instructors: Xiang, Shuo Jiang
- NYU Shanghai ICDS Program
- Open-source contributors of Ollama, Tkinter, and related libraries

---

**Note**: This README should be updated with your specific implementation details, team information, and any additional features you implement beyond the baseline requirements.
