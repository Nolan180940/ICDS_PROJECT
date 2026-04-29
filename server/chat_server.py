"""
Enhanced Chat Server with Group Chat and Bot Support.

This server extends the original functionality to support:
- Multiple clients in group chat
- Bot as a special client that can be triggered with @Bot
- Message broadcasting to all connected users
"""

import time
import socket
import select
import sys
import json
import pickle as pkl
from utils.chat_utils import mysend, myrecv, text_proc
import config.settings as cfg


class ChatGroup:
    """Manage chat groups and user connections."""
    
    def __init__(self):
        self.members = {}  # username -> state (S_ALONE/S_TALKING)
        self.chat_grps = {}  # group_id -> [usernames]
        self.grp_ever = 0
    
    S_ALONE = 0
    S_TALKING = 1
    
    def join(self, name: str):
        """Add a user to the system."""
        self.members[name] = self.S_ALONE
    
    def is_member(self, name: str) -> bool:
        """Check if user is in the system."""
        return name in self.members
    
    def leave(self, name: str):
        """Remove user from system and all groups."""
        self.disconnect(name)
        if name in self.members:
            del self.members[name]
    
    def find_group(self, name: str):
        """Find which group a user belongs to."""
        for k, members in self.chat_grps.items():
            if name in members:
                return True, k
        return False, 0
    
    def connect(self, me: str, peer: str):
        """Connect two users in a chat group."""
        peer_in_group, group_key = self.find_group(peer)
        
        if peer_in_group:
            # Peer is already in a group, join it
            self.chat_grps[group_key].append(me)
            self.members[me] = self.S_TALKING
        else:
            # Create new group
            self.grp_ever += 1
            group_key = self.grp_ever
            self.chat_grps[group_key] = [me, peer]
            self.members[me] = self.S_TALKING
            self.members[peer] = self.S_TALKING
    
    def disconnect(self, name: str):
        """Disconnect user from their current group."""
        in_group, group_key = self.find_group(name)
        if in_group:
            if name in self.chat_grps[group_key]:
                self.chat_grps[group_key].remove(name)
            self.members[name] = self.S_ALONE
            
            # Clean up empty groups
            if len(self.chat_grps[group_key]) <= 1:
                remaining = self.chat_grps[group_key].copy()
                for member in remaining:
                    self.members[member] = self.S_ALONE
                del self.chat_grps[group_key]
    
    def list_all(self) -> str:
        """List all users and groups."""
        full_list = "Users: ------------\n"
        full_list += str(list(self.members.keys())) + "\n"
        full_list += "Groups: -----------\n"
        full_list += str(self.chat_grps) + "\n"
        return full_list
    
    def list_me(self, me: str) -> list:
        """Get list of users in the same group as 'me'."""
        my_list = [me]
        in_group, group_key = self.find_group(me)
        if in_group:
            for member in self.chat_grps[group_key]:
                if member != me:
                    my_list.append(member)
        return my_list
    
    def broadcast_exclude(self, exclude: str, message: dict):
        """Broadcast message to all except excluded user."""
        msg_json = json.dumps(message)
        for name, sock in self.logged_name2sock.items():
            if name != exclude:
                try:
                    mysend(sock, msg_json)
                except:
                    pass


class Server:
    """Main chat server class."""
    
    def __init__(self):
        self.new_clients = []  # Sockets waiting for login
        self.logged_name2sock = {}  # username -> socket
        self.logged_sock2name = {}  # socket -> username
        self.all_sockets = []
        self.group = ChatGroup()
        self.group.logged_name2sock = self.logged_name2sock  # Reference for broadcasting
        
        # Start server socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(cfg.SERVER)
        self.server.listen(10)
        self.all_sockets.append(self.server)
        
        # User chat indices (for search functionality)
        self.indices = {}
        
        print(f"[SERVER] Starting on {cfg.CHAT_IP}:{cfg.CHAT_PORT}")
    
    def new_client(self, sock: socket.socket):
        """Handle new client connection."""
        print('[SERVER] New client connecting...')
        sock.setblocking(0)
        self.new_clients.append(sock)
        self.all_sockets.append(sock)
    
    def login(self, sock: socket.socket):
        """Process login request."""
        try:
            msg = myrecv(sock)
            if len(msg) > 0:
                msg = json.loads(msg)
                
                if msg.get("action") == "login":
                    name = msg.get("name", "Unknown")
                    
                    if not self.group.is_member(name):
                        # Move from new clients to logged clients
                        if sock in self.new_clients:
                            self.new_clients.remove(sock)
                        
                        self.logged_name2sock[name] = sock
                        self.logged_sock2name[sock] = name
                        self.group.join(name)
                        
                        print(f'[SERVER] {name} logged in')
                        mysend(sock, json.dumps({"action": "login", "status": "ok"}))
                    else:
                        # Duplicate username
                        mysend(sock, json.dumps({"action": "login", "status": "duplicate"}))
                        print(f'[SERVER] {name} duplicate login attempt')
                else:
                    print('[SERVER] Wrong login code received')
            else:
                self.logout(sock)
        except Exception as e:
            print(f'[SERVER] Login error: {e}')
            if sock in self.all_sockets:
                self.all_sockets.remove(sock)
    
    def logout(self, sock: socket.socket):
        """Handle client logout."""
        if sock in self.logged_sock2name:
            name = self.logged_sock2name[sock]
            
            # Save chat index
            if name in self.indices:
                try:
                    pkl.dump(self.indices[name], open(name + '.idx', 'wb'))
                except:
                    pass
                del self.indices[name]
            
            del self.logged_sock2name[sock]
            if name in self.logged_name2sock:
                del self.logged_name2sock[name]
            
            self.group.leave(name)
            
            if sock in self.all_sockets:
                self.all_sockets.remove(sock)
            sock.close()
            print(f'[SERVER] {name} logged out')
    
    def handle_msg(self, from_sock: socket.socket):
        """Process incoming messages."""
        try:
            msg = myrecv(from_sock)
            if len(msg) == 0:
                self.logout(from_sock)
                return
            
            msg = json.loads(msg)
            action = msg.get("action", "")
            from_name = self.logged_sock2name.get(from_sock, "Unknown")
            
            # === Connect Request ===
            if action == "connect":
                to_name = msg.get("target", "")
                
                if to_name == from_name:
                    response = {"action": "connect", "status": "self"}
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.connect(from_name, to_name)
                    response = {"action": "connect", "status": "success"}
                    
                    # Notify others in the group
                    the_guys = self.group.list_me(from_name)
                    for g in the_guys[1:]:
                        if g in self.logged_name2sock:
                            peer_sock = self.logged_name2sock[g]
                            mysend(peer_sock, json.dumps({
                                "action": "connect",
                                "status": "request",
                                "from": from_name
                            }))
                else:
                    response = {"action": "connect", "status": "no-user"}
                
                mysend(from_sock, json.dumps(response))
            
            # === Exchange Message ===
            elif action == "exchange":
                message_content = msg.get("message", "")
                the_guys = self.group.list_me(from_name)
                
                # Format and store message
                said2 = text_proc(message_content, from_name)
                
                # Store in indices for all participants
                for g in the_guys:
                    if g not in self.indices:
                        self.indices[g] = []
                    self.indices[g].append(said2)
                
                # Broadcast to all in the group
                for g in the_guys:
                    if g != from_name and g in self.logged_name2sock:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps({
                            "action": "exchange",
                            "from": from_name,
                            "message": message_content
                        }))
                
                # Special handling for group broadcast (all users)
                if msg.get("broadcast", False):
                    self._broadcast_message(from_name, message_content)
            
            # === List Users ===
            elif action == "list":
                result = self.group.list_all()
                mysend(from_sock, json.dumps({"action": "list", "results": result}))
            
            # === Time Request ===
            elif action == "time":
                ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
                mysend(from_sock, json.dumps({"action": "time", "results": ctime}))
            
            # === Search ===
            elif action == "search":
                term = msg.get("target", "")
                results = self._search_history(from_name, term)
                mysend(from_sock, json.dumps({"action": "search", "results": results}))
            
            # === Disconnect ===
            elif action == "disconnect":
                the_guys = self.group.list_me(from_name)
                self.group.disconnect(from_name)
                the_guys.remove(from_name)
                
                if len(the_guys) == 1:
                    g = the_guys.pop()
                    if g in self.logged_name2sock:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps({"action": "disconnect"}))
            
            # === Broadcast to All ===
            elif action == "broadcast":
                message_content = msg.get("message", "")
                self._broadcast_message(from_name, message_content, exclude=[from_name])
        
        except Exception as e:
            print(f'[SERVER] Handle msg error: {e}')
            self.logout(from_sock)
    
    def _broadcast_message(self, from_name: str, content: str, exclude: list = None):
        """Broadcast message to all logged-in users."""
        if exclude is None:
            exclude = []
        
        msg_json = json.dumps({
            "action": "exchange",
            "from": from_name,
            "message": content,
            "broadcast": True
        })
        
        for name, sock in list(self.logged_name2sock.items()):
            if name not in exclude:
                try:
                    mysend(sock, msg_json)
                except:
                    pass
    
    def _search_history(self, username: str, term: str) -> str:
        """Search chat history for a user."""
        if username not in self.indices:
            return ""
        
        results = []
        for entry in self.indices[username]:
            if term.lower() in entry.lower():
                results.append(entry)
        
        return '\n'.join(results) if results else f"'{term}' not found"
    
    def run(self):
        """Main server loop."""
        print('[SERVER] Server started, waiting for connections...')
        
        while True:
            try:
                read, write, error = select.select(self.all_sockets, [], [], 1)
                
                # Handle logged clients
                for logc in list(self.logged_name2sock.values()):
                    if logc in read:
                        self.handle_msg(logc)
                
                # Handle new clients (login phase)
                for newc in self.new_clients[:]:
                    if newc in read:
                        self.login(newc)
                
                # Accept new connections
                if self.server in read:
                    sock, address = self.server.accept()
                    self.new_client(sock)
                    
            except KeyboardInterrupt:
                print('\n[SERVER] Shutting down...')
                break
            except Exception as e:
                print(f'[SERVER] Error in main loop: {e}')
                continue


def main():
    """Entry point for server."""
    server = Server()
    try:
        server.run()
    except KeyboardInterrupt:
        print('\nServer stopped by user')
    finally:
        server.server.close()


if __name__ == "__main__":
    main()
