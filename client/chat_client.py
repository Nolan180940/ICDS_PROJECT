"""
Base Chat Client Class.

Handles socket communication with the server, including:
- Connection management
- Login/logout
- Sending and receiving messages
- Thread-safe message queue for GUI integration
"""

import socket
import threading
import queue
import json
from typing import Optional, Callable

import config.settings as cfg
from utils.chat_utils import mysend, myrecv


class ChatClient:
    """Base chat client for network communication."""
    
    def __init__(self, username: str, host: str = cfg.CHAT_IP, port: int = cfg.CHAT_PORT):
        self.username = username
        self.host = host
        self.port = port
        
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.logged_in = False
        
        # Message queue for thread-safe communication
        self.message_queue = queue.Queue()
        
        # Callbacks for events
        self.on_message_received: Optional[Callable] = None
        self.on_connected: Optional[Callable] = None
        self.on_disconnected: Optional[Callable] = None
        
        # Background receiver thread
        self._receiver_thread: Optional[threading.Thread] = None
        self._stop_receiver = False
    
    def connect(self) -> bool:
        """Establish connection to server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.socket.setblocking(0)  # Non-blocking for select
            self.connected = True
            
            if self.on_connected:
                self.on_connected()
            
            # Start receiver thread
            self._start_receiver()
            
            return True
        except Exception as e:
            print(f"[CLIENT] Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server."""
        self._stop_receiver = True
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        self.connected = False
        self.logged_in = False
        
        if self.on_disconnected:
            self.on_disconnected()
    
    def login(self) -> bool:
        """Send login request to server."""
        if not self.connected or not self.socket:
            return False
        
        try:
            msg = json.dumps({"action": "login", "name": self.username})
            mysend(self.socket, msg)
            
            # Wait for response
            response = myrecv(self.socket)
            if response:
                resp_data = json.loads(response)
                if resp_data.get("status") == "ok":
                    self.logged_in = True
                    return True
            return False
        except Exception as e:
            print(f"[CLIENT] Login failed: {e}")
            return False
    
    def send_message(self, content: str, broadcast: bool = False):
        """Send a chat message."""
        if not self.connected or not self.socket:
            return
        
        try:
            msg = json.dumps({
                "action": "exchange",
                "from": self.username,
                "message": content,
                "broadcast": broadcast
            })
            mysend(self.socket, msg)
        except Exception as e:
            print(f"[CLIENT] Send failed: {e}")
    
    def send_command(self, action: str, target: str = ""):
        """Send a command to server (list, time, search, etc.)."""
        if not self.connected or not self.socket:
            return
        
        try:
            msg = json.dumps({
                "action": action,
                "target": target
            })
            mysend(self.socket, msg)
        except Exception as e:
            print(f"[CLIENT] Command failed: {e}")
    
    def _start_receiver(self):
        """Start background thread to receive messages."""
        self._stop_receiver = False
        self._receiver_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._receiver_thread.start()
    
    def _receive_loop(self):
        """Background loop to receive messages from server."""
        while not self._stop_receiver and self.connected:
            try:
                import select
                read, _, _ = select.select([self.socket], [], [], 0.5)
                
                if self.socket in read:
                    data = myrecv(self.socket)
                    if data:
                        self._process_received_data(data)
                    else:
                        # Empty data means disconnection
                        break
            except Exception as e:
                if not self._stop_receiver:
                    print(f"[CLIENT] Receive error: {e}")
                break
        
        # Connection lost
        if self.connected and not self._stop_receiver:
            self.connected = False
            if self.on_disconnected:
                self.on_disconnected()
    
    def _process_received_data(self, data: str):
        """Process received data and put in queue."""
        try:
            msg_data = json.loads(data)
            
            # Put in queue for main thread to process
            self.message_queue.put(msg_data)
            
            # Call callback if set
            if self.on_message_received:
                self.on_message_received(msg_data)
                
        except json.JSONDecodeError:
            # Not JSON, treat as raw message
            self.message_queue.put({"raw": data})
    
    def get_queued_messages(self) -> list:
        """Get all queued messages (non-blocking)."""
        messages = []
        while not self.message_queue.empty():
            try:
                messages.append(self.message_queue.get_nowait())
            except queue.Empty:
                break
        return messages
    
    def list_users(self):
        """Request list of online users."""
        self.send_command("list")
    
    def get_time(self):
        """Request server time."""
        self.send_command("time")
    
    def search(self, term: str):
        """Search chat history."""
        self.send_command("search", term)
    
    def connect_to_peer(self, peer_name: str):
        """Connect to a specific peer."""
        if not self.connected or not self.socket:
            return
        
        try:
            msg = json.dumps({
                "action": "connect",
                "target": peer_name
            })
            mysend(self.socket, msg)
        except Exception as e:
            print(f"[CLIENT] Connect to peer failed: {e}")


if __name__ == "__main__":
    # Test client connection
    print("Testing ChatClient...")
    client = ChatClient("TestUser")
    
    if client.connect():
        print("Connected!")
        if client.login():
            print("Logged in!")
            client.list_users()
        client.disconnect()
    else:
        print("Failed to connect (server may not be running)")
