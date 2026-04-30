"""
Utility functions for the Distributed Intelligent Chat System.
Includes network communication helpers and text processing.
"""
import socket
import time
from config.settings import SIZE_SPEC, CHAT_WAIT


def mysend(s: socket.socket, msg: str) -> int:
    """
    Send a message with size prefix for framing.
    
    Args:
        s: Socket object
        msg: Message string to send
    
    Returns:
        Total bytes sent
    """
    # Append size to message and send it
    msg = ('0' * SIZE_SPEC + str(len(msg)))[-SIZE_SPEC:] + str(msg)
    msg = msg.encode()
    total_sent = 0
    while total_sent < len(msg):
        try:
            sent = s.send(msg[total_sent:])
            if sent == 0:
                print('[ERROR] Server disconnected')
                break
            total_sent += sent
        except socket.error as e:
            print(f'[ERROR] Send failed: {e}')
            break
    return total_sent


def myrecv(s: socket.socket) -> str:
    """
    Receive a message with size prefix for framing.
    
    Args:
        s: Socket object
    
    Returns:
        Received message string
    """
    # Receive size first
    size = ''
    while len(size) < SIZE_SPEC:
        try:
            text = s.recv(SIZE_SPEC - len(size)).decode()
            if not text:
                print('[INFO] Disconnected')
                return ''
            size += text
        except socket.error as e:
            print(f'[ERROR] Receive failed: {e}')
            return ''
    
    try:
        size = int(size)
    except ValueError:
        # Invalid protocol framing; some other client or HTTP request connected.
        print('[ERROR] Invalid size prefix received, closing socket')
        return ''
    
    # Now receive message
    msg = ''
    while len(msg) < size:
        try:
            text = s.recv(size - len(msg)).decode()
            if not text:
                print('[INFO] Disconnected')
                break
            msg += text
        except socket.error as e:
            print(f'[ERROR] Receive failed: {e}')
            break
    
    return msg


def text_proc(text: str, user: str) -> str:
    """
    Process text with timestamp and username prefix.
    
    Args:
        text: Message content
        user: Username
    
    Returns:
        Formatted message string
    """
    ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
    return f'({ctime}) {user} : {text}'


def format_timestamp() -> str:
    """Get current timestamp in readable format."""
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
