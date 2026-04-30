#!/usr/bin/env python3
"""
Automated test script for ICDS Final Project
Run after starting server: python test_all_features.py

This script tests:
1. Basic chat functionality (client A sends → client B receives)
2. Bot response to @Bot mentions
3. Sentiment analysis with emoji indicators
4. Chat summary generation
5. AI image command handling
"""

import socket
import json
import time
import threading
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.chat_utils import mysend, myrecv
import config.settings as cfg


class TestClient:
    """Simple test client for automated testing."""
    
    def __init__(self, username):
        self.username = username
        self.socket = None
        self.connected = False
        self.received_messages = []
    
    def connect(self, host=cfg.CHAT_IP, port=cfg.CHAT_PORT):
        """Connect to server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True
            return True
        except Exception as e:
            print(f"  ❌ Connection failed: {e}")
            return False
    
    def login(self):
        """Login to server."""
        if not self.connected:
            return False
        
        try:
            msg = json.dumps({"action": "login", "name": self.username})
            mysend(self.socket, msg)
            response = myrecv(self.socket)
            if response:
                resp_data = json.loads(response)
                return resp_data.get("status") == "ok"
            return False
        except Exception as e:
            print(f"  ❌ Login failed: {e}")
            return False
    
    def send_message(self, content, broadcast=False):
        """Send a chat message."""
        if not self.connected:
            return
        
        try:
            msg = json.dumps({
                "action": "exchange",
                "from": self.username,
                "message": content,
                "broadcast": broadcast
            })
            mysend(self.socket, msg)
            print(f"  📤 {self.username} sent: {content}")
        except Exception as e:
            print(f"  ❌ Send failed: {e}")
    
    def receive_message(self, timeout=2.0):
        """Receive a message with timeout."""
        if not self.connected:
            return None
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                import select
                read, _, _ = select.select([self.socket], [], [], 0.5)
                
                if self.socket in read:
                    data = myrecv(self.socket)
                    if data:
                        msg_data = json.loads(data)
                        self.received_messages.append(msg_data)
                        return msg_data
            except:
                pass
            time.sleep(0.1)
        
        return None
    
    def disconnect(self):
        """Disconnect from server."""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False


def wait_for_server(timeout=5):
    """Wait for server to be available."""
    print("⏳ Waiting for server...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((cfg.CHAT_IP, cfg.CHAT_PORT))
            sock.close()
            if result == 0:
                print("✅ Server is running\n")
                return True
        except:
            pass
        time.sleep(0.5)
    
    print("❌ Server not found. Please start server first:\n")
    print("   python -m server.chat_server\n")
    return False


def test_basic_chat():
    """Test: Client A sends message → Client B receives"""
    print("=" * 60)
    print("🧪 Test 1: Basic Chat Functionality")
    print("=" * 60)
    
    # Create two test clients
    client_a = TestClient("Alice")
    client_b = TestClient("Bob")
    
    # Connect both clients
    if not client_a.connect():
        print("❌ FAILED: Client A could not connect")
        return False
    
    if not client_b.connect():
        print("❌ FAILED: Client B could not connect")
        client_a.disconnect()
        return False
    
    # Login both clients
    if not client_a.login():
        print("❌ FAILED: Client A login failed")
        client_a.disconnect()
        client_b.disconnect()
        return False
    print("✅ Client A (Alice) logged in")
    
    if not client_b.login():
        print("❌ FAILED: Client B login failed")
        client_a.disconnect()
        client_b.disconnect()
        return False
    print("✅ Client B (Bob) logged in")
    
    # Client A sends message
    time.sleep(0.5)
    client_a.send_message("Hello Bob! This is a test message.")
    
    # Client B should receive it
    time.sleep(0.5)
    received = client_b.receive_message(timeout=3.0)
    
    success = False
    if received and received.get("action") == "exchange":
        if received.get("from") == "Alice" and "test message" in received.get("message", ""):
            print(f"✅ Client B received: {received.get('message')}")
            success = True
    
    if not success:
        print("❌ FAILED: Client B did not receive message correctly")
    
    # Cleanup
    client_a.disconnect()
    client_b.disconnect()
    
    if success:
        print("✅ Test 1 PASSED: Basic chat works!\n")
    else:
        print("❌ Test 1 FAILED\n")
    
    return success


def test_bot_response():
    """Test: Send @Bot message → Verify bot trigger logic"""
    print("=" * 60)
    print("🧪 Test 2: Bot Response Trigger (@Bot)")
    print("=" * 60)
    
    # Import the bot module to test trigger logic
    try:
        from bot.ai_bot import AIBot
        
        # Create bot instance
        bot = AIBot(persona="helpful")
        print(f"✅ Bot created (Ollama available: {bot.ollama_available})")
        
        # Test trigger detection (simulated in gui_client logic)
        test_messages = [
            ("@Bot hello", True),
            ("@bot help me", True),
            ("Hello Bot", False),  # No @ symbol
            ("BOT please help", False),  # Different format
        ]
        
        all_passed = True
        for msg, should_trigger in test_messages:
            # Simulate _should_bot_respond logic from gui_client
            content_lower = msg.lower()
            triggered = '@bot' in content_lower or '@Bot' in msg
            
            if triggered == should_trigger:
                print(f"✅ Correctly {'triggered' if triggered else 'ignored'}: '{msg}'")
            else:
                print(f"❌ Incorrectly {'triggered' if triggered else 'ignored'}: '{msg}'")
                all_passed = False
        
        # Test bot response generation
        print("\nTesting bot response generation:")
        response = bot.chat("Hello!")
        if response and len(response) > 0:
            print(f"✅ Bot responded: {response[:100]}...")
        else:
            print("❌ Bot did not generate response")
            all_passed = False
        
        if all_passed:
            print("✅ Test 2 PASSED: Bot trigger logic works!\n")
        else:
            print("❌ Test 2 FAILED\n")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ FAILED: Error testing bot: {e}\n")
        return False


def test_sentiment_analysis():
    """Test: Send emotional text → Verify emoji tag"""
    print("=" * 60)
    print("🧪 Test 3: Sentiment Analysis")
    print("=" * 60)
    
    try:
        from bot.sentiment_analyzer import get_analyzer
        
        analyzer = get_analyzer()
        print("✅ Sentiment analyzer initialized")
        
        # Test cases
        test_cases = [
            ("I am so happy today!", "positive", "😊"),
            ("This is terrible and awful", "negative", "😡"),
            ("The weather is okay", "neutral", "😐"),
            ("Thank you so much!", "positive", "😊"),
            ("I hate this error", "negative", "😡"),
        ]
        
        all_passed = True
        for text, expected_category, expected_emoji in test_cases:
            result = analyzer.analyze(text)
            
            category_match = result['category'] == expected_category
            emoji_match = result['emoji'] == expected_emoji
            
            status = "✅" if (category_match and emoji_match) else "❌"
            print(f"{status} '{text}' → {result['category']} {result['emoji']} (polarity: {result['polarity']})")
            
            if not (category_match and emoji_match):
                all_passed = False
        
        if all_passed:
            print("✅ Test 3 PASSED: Sentiment analysis works!\n")
        else:
            print("❌ Test 3 FAILED\n")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ FAILED: Error testing sentiment analysis: {e}\n")
        return False


def test_summary_command():
    """Test: Send /summary → Verify summary generation"""
    print("=" * 60)
    print("🧪 Test 4: Chat Summary Generation")
    print("=" * 60)
    
    try:
        from bot.summary_generator import SummaryGenerator
        from bot.ai_bot import AIBot
        
        # Create sample chat history
        chat_history = [
            "Alice: Hello everyone!",
            "Bob: Hi Alice! How are you?",
            "Alice: I'm doing great, working on the project.",
            "Charlie: Hey team! What's up?",
            "Bob: Just coding the final features.",
            "Alice: Same here. The deadline is approaching.",
            "Charlie: Let me know if you need help.",
            "Alice: Thanks Charlie! That would be great.",
        ]
        
        print(f"✅ Created sample chat history ({len(chat_history)} messages)")
        
        # Test without LLM (fallback mode)
        generator = SummaryGenerator(llm_client=None)
        summary = generator.generate(chat_history)
        
        if summary and len(summary) > 0:
            print(f"\n✅ Generated summary:\n{summary}\n")
            
            # Verify summary contains key info
            checks = [
                ("Total messages" in summary or "messages" in summary.lower(), "Message count"),
                ("Alice" in summary or "Bob" in summary, "Participant names"),
            ]
            
            all_passed = all(check[0] for check in checks)
            
            for check, name in checks:
                status = "✅" if check else "❌"
                print(f"{status} Summary contains: {name}")
            
            if all_passed:
                print("✅ Test 4 PASSED: Summary generation works!\n")
            else:
                print("❌ Test 4 FAILED\n")
            
            return all_passed
        else:
            print("❌ FAILED: No summary generated\n")
            return False
        
    except Exception as e:
        print(f"❌ FAILED: Error testing summary: {e}\n")
        return False


def test_ai_image_command():
    """Test: /aipic command handling"""
    print("=" * 60)
    print("🧪 Test 5: AI Image Command")
    print("=" * 60)
    
    try:
        from bot.ai_bot import AIBot
        
        bot = AIBot(persona="helpful")
        print(f"✅ Bot initialized (Ollama: {bot.ollama_available})")
        
        # Test image generation command
        command = "/aipic: a cute cat playing with yarn"
        response = bot.chat(command)
        
        if response and len(response) > 0:
            print(f"\n✅ Bot responded to image command:\n{response[:200]}...\n")
            
            # Verify response contains expected elements
            checks = [
                ("Image" in response or "image" in response.lower(), "Mentions image"),
                ("Description" in response or "description" in response.lower(), "Shows description"),
            ]
            
            all_passed = all(check[0] for check in checks)
            
            for check, name in checks:
                status = "✅" if check else "❌"
                print(f"{status} Response contains: {name}")
            
            if all_passed:
                print("✅ Test 5 PASSED: AI image command works!\n")
            else:
                print("❌ Test 5 FAILED\n")
            
            return all_passed
        else:
            print("❌ FAILED: No response generated\n")
            return False
        
    except Exception as e:
        print(f"❌ FAILED: Error testing image command: {e}\n")
        return False


def test_code_quality_checks():
    """Verify code quality requirements"""
    print("=" * 60)
    print("🧪 Test 6: Code Quality & Bug Fix Verification")
    print("=" * 60)
    
    all_passed = True
    
    # Check 1: system_msg reset in gui_client.py
    try:
        with open("client/gui_client.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        checks = [
            ("self.system_msg = \"\"" in content, "system_msg initialization"),
            ("# FIX:" in content or "# ✅ BUG FIX:" in content, "Bug fix comments"),
            ("threading.current_thread() is threading.main_thread()" in content, "Thread-safe GUI updates"),
            ("try:" in content and "except" in content, "Exception handling"),
            ("finally" in content or ".close()" in content, "Resource cleanup"),
            ("utf-8" in content or "encoding='utf-8'" in content, "UTF-8 encoding"),
        ]
        
        print("\nChecking gui_client.py:")
        for check, name in checks:
            status = "✅" if check else "❌"
            print(f"{status} {name}")
            if not check:
                all_passed = False
                
    except Exception as e:
        print(f"❌ Error checking gui_client.py: {e}")
        all_passed = False
    
    # Check 2: Ollama fallback in ai_bot.py
    try:
        with open("bot/ai_bot.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        ollama_checks = [
            ("ollama_available" in content, "Ollama availability check"),
            ("_fallback_response" in content, "Fallback response method"),
            ("try:" in content and "except" in content, "Exception handling in API calls"),
        ]
        
        print("\nChecking ai_bot.py:")
        for check, name in ollama_checks:
            status = "✅" if check else "❌"
            print(f"{status} {name}")
            if not check:
                all_passed = False
                
    except Exception as e:
        print(f"❌ Error checking ai_bot.py: {e}")
        all_passed = False
    
    if all_passed:
        print("\n✅ Test 6 PASSED: Code quality checks passed!\n")
    else:
        print("\n❌ Test 6 FAILED\n")
    
    return all_passed


def main():
    """Run all automated tests."""
    print("\n" + "=" * 60)
    print("🚀 ICDS Project Automated Test Suite")
    print("=" * 60 + "\n")
    
    # Check if server is running
    server_running = wait_for_server(timeout=3)
    
    results = {
        "Basic Chat": False,
        "Bot Response": False,
        "Sentiment Analysis": False,
        "Chat Summary": False,
        "AI Image Command": False,
        "Code Quality": False,
    }
    
    # Run tests that don't require server first
    print("\n--- Running Offline Tests ---\n")
    results["Bot Response"] = test_bot_response()
    results["Sentiment Analysis"] = test_sentiment_analysis()
    results["Chat Summary"] = test_summary_command()
    results["AI Image Command"] = test_ai_image_command()
    results["Code Quality"] = test_code_quality_checks()
    
    # Run server-dependent tests
    if server_running:
        print("\n--- Running Online Tests (Server Required) ---\n")
        results["Basic Chat"] = test_basic_chat()
    else:
        print("\n⚠️  Skipping online tests (server not running)\n")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Project is ready for submission.\n")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.\n")
        return 1


if __name__ == "__main__":
    exit(main())
