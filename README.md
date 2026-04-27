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

---

## 🤖 Bot Integration Interface (How it works)

This section describes the **internal interface contract** between the GUI/chat client layer and the AI bot module. This is *not* the Ollama HTTP API — it is the Python-level calling convention your code uses to route user messages to the bot and display replies.

### Overview: Two layers of "interface"

### 📡 GUI ↔ Bot Manager 调用约定

#### 1. 触发方式（客户端识别）
```python
# GUI 层识别用户输入是否调用 Bot
if user_input.startswith('/bot ') or user_input.lower().startswith('@bot'):
    # 提取消息内容
    bot_prompt = user_input.split(' ', 1)[1]
    # 调用 Bot 模块
    reply = bot_manager.get_response(bot_prompt, personality="academic")
    # 显示回复
    gui.display_bot_reply(reply)

```
User types in GUI
      │
      ▼
GUI / Bot Manager layer          ← detects trigger command, calls bot module
      │   ChatBotClient.chat(message)
      ▼
chat_bot_client.py               ← your bot module (internal interface)
      │   ollama.Client.chat(...)
      ▼
Ollama local server              ← http://localhost:11434  (external service)
      │
      ▼
LLM model (e.g. phi3:mini)
```

- **Internal interface** = how your GUI/manager calls `ChatBotClient` (this section).
- **External interface** = how `ChatBotClient` talks to the Ollama service (handled automatically by the `ollama` Python library).

---

### The Bot Module: `chat_bot_client.py`

The primary class is **`ChatBotClient`** (in `chat_bot_client.py`), backed by the Ollama Python SDK.

#### Constructor

```python
ChatBotClient(
    name="3po",                          # Display name of the bot (cosmetic)
    model="phi3:mini",                   # Ollama model to use
    host="http://localhost:11434",       # Ollama server URL
    headers={"x-some-header": "some-value"}  # Optional HTTP headers
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | `"3po"` | Bot display name (cosmetic only) |
| `model` | `str` | `"phi3:mini"` | Ollama model name (must be pulled locally) |
| `host` | `str` | `"http://localhost:11434"` | URL of the running Ollama server |
| `headers` | `dict` | `{...}` | Extra HTTP headers forwarded to Ollama |

#### `chat(message: str) → str`  *(primary interface method)*

```python
reply: str = bot.chat(user_message)
```

- **Input**: a plain-text user message string.
- **Output**: the bot's reply as a plain string — display it directly in the GUI.
- **Side-effect**: appends both the user turn and the assistant turn to `self.messages`, preserving conversation context across calls.

#### `stream_chat(message: str)`  *(streaming variant)*

```python
bot.stream_chat(user_message)   # prints tokens to stdout as they arrive
```

- Like `chat`, but streams tokens chunk-by-chunk (currently prints to stdout).
- Useful if you want to display a "typing…" effect in the GUI — adapt the `print` calls to push tokens to the GUI widget instead.

---

### Conversation Context (`self.messages`)

`ChatBotClient` keeps the full conversation history in `self.messages` — a list of `{"role": ..., "content": ...}` dicts that is passed to Ollama on every call:

```python
self.messages = [
    {"role": "user",      "content": "Hello!"},
    {"role": "assistant", "content": "Hi there! How can I help?"},
    {"role": "user",      "content": "Tell me a joke."},
    # ...
]
```

**Important considerations:**

| Concern | Current behaviour | Recommendation |
|---------|------------------|----------------|
| **Reset / new session** | `self.messages` is never cleared automatically | Call `bot.messages = []` (or create a new `ChatBotClient` instance) to start a fresh conversation |
| **Per-user context** | One `ChatBotClient` instance = one shared context | Instantiate a **separate** `ChatBotClient` per user (or per chat room) if you need isolated histories |
| **Global bot** | A single global instance mixes all users' histories | Fine for a demo; not suitable for production multi-user deployment |

---

### Injecting a System Prompt / Personality

To give the bot a persona, prepend a `{"role": "system", ...}` message **before the first user turn**:

```python
bot = ChatBotClient(model="phi3:mini")

# Inject personality once (before any user messages)
bot.messages.append({
    "role": "system",
    "content": "You are a friendly Python tutor named Tom. Keep replies concise."
})

reply = bot.chat("How do I reverse a list?")
print(reply)
```

The system message persists in `self.messages` and influences all subsequent replies. Reset `bot.messages = []` (and re-inject the system prompt if desired) to clear the persona along with history.

---

### Trigger Commands: Application-level conventions

`/bot [message]` and `@Bot [message]` are **application-level command conventions**, not HTTP endpoints or built-in protocol features. Your GUI / Bot Manager layer is responsible for detecting them:

```python
# Example routing logic inside your GUI send-button handler
def on_send(user_input: str):
    if user_input.startswith("/bot ") or user_input.lower().startswith("@bot "):
        # Strip the command prefix and route to the bot module
        message = user_input.split(" ", 1)[1]
        reply = bot.chat(message)
        display_message("Bot", reply)          # show in GUI chat window
    else:
        # Normal message: send to chat server as usual
        client.send(user_input)
```

There is no server-side routing for bot commands — the detection and dispatch happen entirely on the **client side** before any network send.

---

### Practical Integration Example

The following snippet shows the complete lifecycle for wiring a `ChatBotClient` into a GUI client:

```python
from chat_bot_client import ChatBotClient

# 1. Instantiate once (e.g. when the GUI starts up)
bot = ChatBotClient(model="phi3:mini", host="http://localhost:11434")

# 2. (Optional) Inject a system prompt / personality
bot.messages.append({
    "role": "system",
    "content": "You are a helpful assistant. Respond in one or two sentences."
})

# 3. Call .chat() when the user sends a bot-targeted message
def handle_bot_message(user_text: str) -> str:
    reply = bot.chat(user_text)   # blocks until Ollama responds
    return reply                  # caller displays this string in the chat window

# 4. Example usage
BOT_PREFIX = "/bot "
user_input = "/bot What is a socket?"
if user_input.startswith(BOT_PREFIX):
    message = user_input[len(BOT_PREFIX):]    # strip "/bot " prefix
    bot_reply = handle_bot_message(message)
    print(f"[Bot] {bot_reply}")               # replace print with GUI display call

# 5. Reset context when the user ends the bot session
bot.messages = []
```

**Prerequisites before running:**
1. Ollama must be installed and running: `ollama serve`
2. The chosen model must be pulled: `ollama pull phi3:mini`
3. Python package installed: `pip install ollama`

---

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
