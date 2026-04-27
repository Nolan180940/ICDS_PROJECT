# gui_client.py - 最小可运行 GUI 客户端
import tkinter as tk
from tkinter import scrolledtext, END, messagebox
import threading
import queue
import json
import socket

# 导入现有模块（确保路径正确）
from chat_client_class import ChatClient
from client_state_machine import ClientStateMachine

class GUIChatClient:
    def __init__(self, host='127.0.0.1', port=5555, username="User"):
        self.host = host
        self.port = port
        self.username = username
        
        # 消息队列（线程安全，用于子线程→主线程通信）
        self.message_queue = queue.Queue()
        
        # 初始化状态机和客户端（后续集成）
        # self.client = ChatClient(host, port, username)
        # self.sm = ClientStateMachine(self.client)
        
        # 初始化 GUI
        self.root = tk.Tk()
        self.root.title(f"ICDS Chat - {username}")
        self.root.geometry("650x750")
        self.root.minsize(500, 600)
        
        self._setup_styles()
        self._setup_gui()
        self._start_message_listener()
        
    def _setup_styles(self):
        """配置消息样式标签"""
        # 在 Text widget 中定义 tag 样式
        self.style_config = {
            'sent': {'justify': 'right', 'foreground': '#0066cc', 'font': ('Arial', 10)},
            'received': {'justify': 'left', 'foreground': '#333333', 'font': ('Arial', 10)},
            'bot': {'justify': 'left', 'foreground': '#9933cc', 'font': ('Arial', 10, 'italic')},
            'system': {'justify': 'center', 'foreground': '#666666', 'font': ('Arial', 9, 'italic')}
        }
        
    def _setup_gui(self):
        """构建 GUI 界面"""
        # 1️⃣ 消息显示区域（核心！）
        self.chat_window = scrolledtext.ScrolledText(
            self.root, 
            state='disabled', 
            wrap='word', 
            font=('Arial', 10),
            padx=10, pady=10
        )
        self.chat_window.pack(padx=15, pady=(15, 5), fill='both', expand=True)
        
        # 应用样式配置
        for tag, config in self.style_config.items():
            self.chat_window.tag_config(tag, **config)
        
        # 2️⃣ 输入区域
        input_frame = tk.Frame(self.root)
        input_frame.pack(padx=15, pady=(0, 10), fill='x')
        
        self.msg_entry = tk.Entry(input_frame, font=('Arial', 11), relief='solid', bd=1)
        self.msg_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.msg_entry.bind('<Return>', lambda e: self._send_message())
        self.msg_entry.focus_set()
        
        send_btn = tk.Button(
            input_frame, 
            text="Send", 
            command=self._send_message,
            bg='#007acc', fg='white', relief='flat', padx=15
        )
        send_btn.pack(side='right')
        
        # 3️⃣ 【额外功能】Emoji 按钮（简单加分项⭐）
        emoji_frame = tk.Frame(self.root)
        emoji_frame.pack(pady=(0, 5))
        emojis = ["😊", "👍", "🎉", "🤖", "❓", "✨"]
        for emoji in emojis:
            btn = tk.Button(emoji_frame, text=emoji, width=2, 
                          command=lambda e=emoji: self._insert_emoji(e),
                          relief='flat', font=('Arial', 12))
            btn.pack(side='left', padx=2)
            
    def _insert_emoji(self, emoji):
        """插入 emoji 到输入框"""
        self.msg_entry.insert('end', emoji + " ")
        self.msg_entry.focus_set()
        
    def _send_message(self):
        """处理用户发送消息"""
        message = self.msg_entry.get().strip()
        if not message:
            return
            
        # ✅ 显示自己发送的消息（右对齐 + 蓝色）
        self._display_message(f"{self.username}: {message}", tag='sent')
        
        # 🔜 后续：通过 socket 发送给服务器
        # if self.client and self.client.socket:
        #     self.client.send_message(message)
        
        # 清空输入框
        self.msg_entry.delete(0, 'end')
        
    def _display_message(self, text, tag='received'):
        """在 GUI 显示消息（线程安全）⭐关键函数"""
        def _insert():
            self.chat_window.config(state='normal')
            self.chat_window.insert(END, text + "\n", tag)
            self.chat_window.config(state='disabled')
            self.chat_window.see(END)  # 自动滚动到最新
            
        # 确保在主线程执行（避免 Tkinter 线程错误）
        if threading.current_thread() is threading.main_thread():
            _insert()
        else:
            self.root.after(0, _insert)
            
    def _start_message_listener(self):
        """后台线程：监听来自服务器的消息"""
        def listener():
            while True:
                try:
                    # 从队列获取消息（由 socket 接收线程放入）
                    msg_data = self.message_queue.get(timeout=1)
                    sender = msg_data.get('from', msg_data.get('sender', 'Unknown'))
                    content = msg_data.get('message', msg_data.get('content', ''))
                    msg_type = msg_data.get('type', 'chat')
                    
                    # 区分消息类型并显示
                    if sender == "Bot" or msg_type == 'bot':
                        self._display_message(f"🤖 Bot: {content}", tag='bot')
                    elif sender == self.username:
                        pass  # 自己发的已显示，跳过
                    else:
                        self._display_message(f"{sender}: {content}", tag='received')
                        
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"[Listener Error] {e}")
                    
        thread = threading.Thread(target=listener, daemon=True)
        thread.start()
        
    def receive_message(self, msg_dict: dict):
        """外部调用：将收到的消息放入队列（线程安全）"""
        self.message_queue.put(msg_dict)
        
    def run(self):
        """启动 GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()
        
    def _on_close(self):
        """关闭窗口前的清理"""
        # TODO: 优雅断开连接
        self.root.destroy()

# 🧪 测试运行（独立测试 GUI，不依赖服务器）
if __name__ == "__main__":
    app = GUIChatClient(username="Alice")
    
    # 模拟收到消息（测试用）
    def simulate_messages():
        import time
        time.sleep(1)
        app.receive_message({'from': 'Bob', 'content': 'Hello! 👋'})
        time.sleep(1)
        app.receive_message({'from': 'Bot', 'content': 'Hi there! How can I help?', 'type': 'bot'})
        app._display_message("Alice: Hi everyone!", tag='sent')
        
    threading.Thread(target=simulate_messages, daemon=True).start()
    app.run()
