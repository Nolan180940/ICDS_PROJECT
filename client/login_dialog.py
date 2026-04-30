"""
Login Dialog for Chat Application.

Provides a simple login window to enter username before accessing the main chat.
This fulfills the "simple login interface" bonus requirement (10%).
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional


class LoginDialog:
    """Login dialog window."""
    
    def __init__(self, parent=None, title: str = "Chat Login"):
        try:
            self.parent = parent
            self.result: Optional[str] = None
            self.owns_root = parent is None
            
            # Create top-level dialog
            if self.owns_root:
                self.dialog = tk.Tk()
            else:
                self.dialog = tk.Toplevel(parent)
            self.dialog.title(title)
            self.dialog.resizable(False, False)
            self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)
            
            # Set window size
            self.dialog.geometry("420x380")
            
            # Make dialog appear on top
            self.dialog.attributes('-topmost', True)
            
            self._setup_ui()
            
            # Update display to ensure window is shown
            self.dialog.update_idletasks()
            
            # Force window to appear on screen center
            self.dialog.deiconify()
            self.dialog.lift()
            x = (self.dialog.winfo_screenwidth() // 2) - 210
            y = (self.dialog.winfo_screenheight() // 2) - 190
            self.dialog.geometry(f"420x380+{x}+{y}")
            
            print("[DEBUG] 登录对话框已创建并显示在屏幕中央")
            
            # Make transient and grab after positioning
            if not self.owns_root:
                self.dialog.transient(parent)
            self.dialog.update()
            self.dialog.grab_set()
            self.dialog.focus_force()
        except Exception as e:
            print(f"[ERROR] 登录对话框创建失败: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _setup_ui(self):
        """Setup the login UI."""
        # Main frame with padding
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        title_label = ttk.Label(
            main_frame,
            text="Welcome to ICDS Chat",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Username frame
        user_frame = ttk.Frame(main_frame)
        user_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(user_frame, text="Username:", width=12).pack(side=tk.LEFT)
        
        self.username_entry = ttk.Entry(user_frame, width=25)
        self.username_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.username_entry.focus_set()
        self.username_entry.bind('<Return>', lambda e: self._on_ok())
        
        # Persona selection (for bot feature preview)
        persona_frame = ttk.LabelFrame(main_frame, text="Bot Persona (Optional)", padding="10")
        persona_frame.pack(fill=tk.X, pady=15)
        
        self.persona_var = tk.StringVar(value="helpful")
        personas = [
            ("Helpful 😊", "helpful"),
            ("Humorous 🎭", "humorous"),
            ("Serious 💼", "serious"),
            ("Creative 🎨", "creative"),
            ("Advisor 📚", "advisor")
        ]
        
        for text, value in personas:
            ttk.Radiobutton(
                persona_frame,
                text=text,
                variable=self.persona_var,
                value=value
            ).pack(anchor=tk.W, pady=2)
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.ok_btn = ttk.Button(btn_frame, text="Login", command=self._on_ok, width=10)
        self.ok_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self._on_cancel, width=10)
        self.cancel_btn.pack(side=tk.RIGHT)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack(pady=(10, 0))
    
    def _on_ok(self):
        """Handle OK button click."""
        username = self.username_entry.get().strip()
        
        if not username:
            self.status_label.config(text="Please enter a username")
            return
        
        if len(username) < 2:
            self.status_label.config(text="Username must be at least 2 characters")
            return
        
        if len(username) > 20:
            self.status_label.config(text="Username too long (max 20 chars)")
            return
        
        # Validate username (alphanumeric + underscore)
        if not all(c.isalnum() or c == '_' for c in username):
            self.status_label.config(text="Only letters, numbers, and underscores allowed")
            return
        
        self.result = username
        self.dialog.destroy()
        self.dialog.quit()
    
    def _on_cancel(self):
        """Handle Cancel button click."""
        self.result = None
        self.dialog.destroy()
        self.dialog.quit()
    
    def _on_close(self):
        """Handle window close button."""
        self._on_cancel()
    
    def get_username(self) -> Optional[str]:
        """Get the entered username."""
        return self.result
    
    def get_persona(self) -> str:
        """Get selected bot persona."""
        return self.persona_var.get()


def show_login_dialog(parent) -> tuple:
    """
    Show login dialog and return (username, persona).
    
    Args:
        parent: Parent Tk window
    
    Returns:
        Tuple of (username or None, persona string)
    """
    print("[DEBUG] 显示登录对话框...")
    dialog = LoginDialog(parent)
    dialog.dialog.mainloop()
    username = dialog.get_username()
    persona = dialog.get_persona()
    print(f"[DEBUG] 登录结果: username={username}, persona={persona}")
    if dialog.owns_root:
        try:
            dialog.dialog.destroy()
        except Exception:
            pass
    return username, persona


if __name__ == "__main__":
    # Test the login dialog
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    def test_login():
        username, persona = show_login_dialog(root)
        if username:
            print(f"Logged in as: {username}")
            print(f"Selected persona: {persona}")
        else:
            print("Login cancelled")
        root.quit()
    
    root.after(100, test_login)
    root.mainloop()
