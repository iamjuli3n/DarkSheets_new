"""
DarkSheets GUI Interface
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import threading
import json
from datetime import datetime
import socks
import socket
from tkinter.font import Font
import webbrowser
import requests
import time
import os
import sys

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from darksheets import DarkSheets

class SearchThread(threading.Thread):
    """Thread for performing dark web searches"""
    def __init__(self, darksheets_instance, query, callback, save_path=None, selected_engines=None):
        super().__init__()
        self.darksheets = darksheets_instance
        self.query = query
        self.callback = callback
        self.save_path = save_path
        self.selected_engines = selected_engines if selected_engines else []

    def run(self):
        try:
            results = self.darksheets.search_dark_web(self.query, self.selected_engines)
            self.callback("search_complete", results)
        except Exception as e:
            self.callback("error", str(e))

class TorThread(threading.Thread):
    """Thread for Tor operations"""
    def __init__(self, darksheets_instance, operation, callback, connect=False):
        super().__init__()
        self.darksheets = darksheets_instance
        self.operation = operation
        self.callback = callback
        self.connect = connect

    def run(self):
        try:
            if self.connect:
                success = self.darksheets.connect_tor()
                self.callback("tor_connect", "Connected to Tor" if success else "Failed to connect to Tor")
            elif self.operation == "disconnect":
                success = self.darksheets.disconnect_tor()
                self.callback("tor_disconnect", "Disconnected from Tor" if success else "Failed to disconnect from Tor")
            elif self.operation == "check":
                is_connected = self.darksheets.check_tor()
                self.callback("tor_status", "Connected to Tor" if is_connected else "Not connected to Tor")
        except Exception as e:
            self.callback("error", str(e))

class ModernFrame(ttk.Frame):
    """Modern styled frame with rounded corners and shadow effect"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(style="Modern.TFrame")

class ModernButton(ttk.Button):
    """Modern styled button with hover effect"""
    def __init__(self, master, **kwargs):
        super().__init__(master, style="Modern.TButton", **kwargs)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, _):
        """Handle mouse enter event"""
        self.configure(style="ModernHover.TButton")

    def on_leave(self, _):
        """Handle mouse leave event"""
        self.configure(style="Modern.TButton")

class DarkWebGUI:
    def __init__(self):
        self.darksheets = DarkSheets()
        self.save_path = None
        self.search_history = []
        self.tor_browser_path = None
        self.root = tk.Tk()
        self.setup_styles()
        
        # Variables
        self.status_var = tk.StringVar(value="Ready")
        self.search_var = tk.StringVar()
        self.ahmia_var = tk.BooleanVar(value=True)
        self.torch_var = tk.BooleanVar(value=True)
        self.haystak_var = tk.BooleanVar(value=True)
        self.tag_to_url = {}
        self.conn_status_var = tk.StringVar(value="Not Connected")
        self.latency_var = tk.StringVar(value="Latency: --")
        self.ip_var = tk.StringVar(value="IP: --")
        
        self.init_ui()
        # Start Tor connection immediately
        TorThread(self.darksheets, None, self.callback_handler, connect=True).start()

    def setup_styles(self):
        """Setup modern styles for widgets"""
        # Color scheme - softer, eye-friendly colors
        self.colors = {
            'bg': '#1a1b26',  # Soft dark background
            'bg_light': '#24283b',  # Lighter background for contrast
            'text': '#7aa2f7',  # Soft blue text
            'text_dim': '#9aa5ce',  # Dimmed blue text
            'accent': '#2ac3de',  # Bright blue accent
            'accent_hover': '#73daca',  # Cyan hover
            'success': '#9ece6a',  # Soft green
            'warning': '#e0af68',  # Soft orange
            'error': '#f7768e',  # Soft red
            'log_bg': '#1f2335'  # Dark blue for log background
        }

        # Configure ttk styles
        style = ttk.Style()
        style.configure("Modern.TFrame", background=self.colors['bg'])
        style.configure("ModernInner.TFrame", background=self.colors['bg_light'])
        
        # Button styles
        style.configure("Modern.TButton",
                       background=self.colors['accent'],
                       foreground=self.colors['bg'],
                       padding=(10, 5),
                       font=('Segoe UI', 9))
        
        style.configure("ModernHover.TButton",
                       background=self.colors['accent_hover'],
                       foreground=self.colors['bg'],
                       padding=(10, 5),
                       font=('Segoe UI', 9))
        
        # Entry style
        style.configure("Modern.TEntry",
                       fieldbackground=self.colors['bg_light'],
                       foreground=self.colors['text'],
                       padding=5)
        
        # Label style
        style.configure("Modern.TLabel",
                       background=self.colors['bg'],
                       foreground=self.colors['text'],
                       font=('Segoe UI', 9))
        
        # Checkbutton style
        style.configure("Modern.TCheckbutton",
                       background=self.colors['bg'],
                       foreground=self.colors['text'],
                       font=('Segoe UI', 9))

        # Notebook style
        style.configure("TNotebook",
                       background=self.colors['bg'],
                       foreground=self.colors['text'])
        style.configure("TNotebook.Tab",
                       background=self.colors['bg_light'],
                       foreground=self.colors['text'],
                       padding=(10, 5))
        style.map("TNotebook.Tab",
                 background=[("selected", self.colors['accent'])],
                 foreground=[("selected", self.colors['bg'])])

    def init_ui(self):
        """Initialize the user interface"""
        self.root.title("DarkSheets - Dark Web Research Tool")
        self.root.geometry("1200x800")
        self.root.configure(bg=self.colors['bg'])
        
        # Main container
        main_container = ModernFrame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ModernFrame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_font = Font(family="Segoe UI", size=24, weight="bold")
        title = ttk.Label(header_frame, text="DarkSheets",
                         font=title_font, style="Modern.TLabel")
        title.pack(side=tk.LEFT)
        
        # Search section
        search_frame = ModernFrame(main_container)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var,
                               style="Modern.TEntry", font=('Segoe UI', 11))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        search_button = ModernButton(search_frame, text="Search",
                                   command=self.perform_search)
        search_button.pack(side=tk.LEFT)
        
        # Search engines frame
        engines_frame = ModernFrame(main_container)
        engines_frame.pack(fill=tk.X, pady=(0, 20))
        
        for var, text in [(self.ahmia_var, "Ahmia"),
                         (self.torch_var, "Torch"),
                         (self.haystak_var, "Haystak")]:
            cb = ttk.Checkbutton(engines_frame, text=text, variable=var,
                               style="Modern.TCheckbutton")
            cb.pack(side=tk.LEFT, padx=10)

        # Create main content frame with left and right panes
        content_frame = ModernFrame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left pane - Results and History
        left_pane = ModernFrame(content_frame)
        left_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Notebook for different sections
        self.notebook = ttk.Notebook(left_pane)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Results tab
        results_frame = ModernFrame(self.notebook)
        self.notebook.add(results_frame, text="Results")
        
        self.results_text = tk.Text(results_frame, wrap=tk.WORD,
                                  bg=self.colors['bg_light'],
                                  fg=self.colors['text'],
                                  insertbackground=self.colors['text'],
                                  font=('Segoe UI', 10),
                                  bd=0,
                                  padx=10,
                                  pady=10)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags
        self.results_text.tag_configure("link",
                                      foreground=self.colors['accent'],
                                      underline=True)
        self.results_text.tag_configure("title",
                                      font=('Segoe UI', 12, 'bold'),
                                      foreground=self.colors['text'])
        self.results_text.tag_configure("engine",
                                      foreground=self.colors['text_dim'])
        
        # Bind text widget events
        self.results_text.tag_bind("link", "<Button-1>", self.handle_click)
        self.results_text.tag_bind("link", "<Button-3>", self.handle_right_click)
        self.results_text.tag_bind("link", "<Enter>",
                                 lambda e: self.results_text.configure(cursor="hand2"))
        self.results_text.tag_bind("link", "<Leave>",
                                 lambda e: self.results_text.configure(cursor=""))
        
        # History tab
        history_frame = ModernFrame(self.notebook)
        self.notebook.add(history_frame, text="History")
        
        self.history_text = tk.Text(history_frame,
                                  bg=self.colors['bg_light'],
                                  fg=self.colors['text'],
                                  font=('Segoe UI', 10),
                                  bd=0,
                                  padx=10,
                                  pady=10)
        self.history_text.pack(fill=tk.BOTH, expand=True)

        # Right pane - Log and Connection Info
        right_pane = ModernFrame(content_frame)
        right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0), width=400)

        # Connection info frame
        conn_frame = ModernFrame(right_pane)
        conn_frame.pack(fill=tk.X, pady=(0, 10))

        conn_label = ttk.Label(conn_frame, text="Connection Status",
                             font=('Segoe UI', 12, 'bold'),
                             style="Modern.TLabel")
        conn_label.pack(anchor=tk.W)

        # Connection metrics
        for var in [self.conn_status_var, self.latency_var, self.ip_var]:
            label = ttk.Label(conn_frame, textvariable=var, style="Modern.TLabel")
            label.pack(anchor=tk.W, pady=2)

        # Log frame
        log_frame = ModernFrame(right_pane)
        log_frame.pack(fill=tk.BOTH, expand=True)

        log_label = ttk.Label(log_frame, text="System Log",
                            font=('Segoe UI', 12, 'bold'),
                            style="Modern.TLabel")
        log_label.pack(anchor=tk.W)

        self.log_text = tk.Text(log_frame,
                              bg=self.colors['log_bg'],
                              fg=self.colors['text'],
                              font=('Consolas', 9),
                              bd=0,
                              padx=10,
                              pady=10,
                              height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Configure log text tags
        self.log_text.tag_configure("info",
                                  foreground=self.colors['text'])
        self.log_text.tag_configure("success",
                                  foreground=self.colors['success'])
        self.log_text.tag_configure("warning",
                                  foreground=self.colors['warning'])
        self.log_text.tag_configure("error",
                                  foreground=self.colors['error'])
        
        # Status bar
        status_frame = ModernFrame(main_container)
        status_frame.pack(fill=tk.X, pady=(20, 0))
        
        status_label = ttk.Label(status_frame,
                               textvariable=self.status_var,
                               style="Modern.TLabel")
        status_label.pack(side=tk.LEFT)
        
        # Control buttons
        control_frame = ModernFrame(status_frame)
        control_frame.pack(side=tk.RIGHT)
        
        for text, command in [
            ("Check Connection", self.check_connection),
            ("Set Tor Path", self.set_tor_browser_path)
        ]:
            btn = ModernButton(control_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=5)

    def callback_handler(self, msg_type, msg):
        """Handle callbacks from threads"""
        if msg_type == "search_complete":
            self.display_results(msg)
        elif msg_type in ["tor_connect", "tor_disconnect", "tor_status"]:
            self.status_var.set(msg)
        elif msg_type == "error":
            messagebox.showerror("Error", str(msg))

    def set_tor_browser_path(self):
        """Let user select Tor Browser location"""
        path = filedialog.askopenfilename(
            title="Select Tor Browser firefox.exe",
            filetypes=[("Executable files", "*.exe")]
        )
        if path and "Tor Browser" in path:
            self.tor_browser_path = path
            self.status_var.set("Tor Browser path set successfully")
        elif path:
            messagebox.showwarning("Warning",
                                 "Selected file is not Tor Browser. Please select firefox.exe from Tor Browser folder.")

    def open_in_tor_browser(self, url):
        """Open URL in Tor Browser"""
        if not self.tor_browser_path:
            if messagebox.askyesno("Tor Browser Required",
                                 "Tor Browser is required to open .onion links safely. "
                                 "Would you like to download it now?"):
                webbrowser.open("https://www.torproject.org/download/")
            return
        
        try:
            subprocess.Popen([self.tor_browser_path, url])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Tor Browser: {e}")

    def display_results(self, results):
        """Display results with clickable links"""
        self.results_text.delete(1.0, tk.END)
        self.tag_to_url.clear()
        
        for i, result in enumerate(results):
            tag = f"link_{i}"
            self.tag_to_url[tag] = result["url"]
            
            # Add engine name
            self.results_text.insert(tk.END, f"{result['engine']}\n", "engine")
            
            # Add title
            self.results_text.insert(tk.END, f"{result['title']}\n", "title")
            
            # Add URL as clickable link
            self.results_text.insert(tk.END, result["url"] + "\n", (tag, "link"))
            
            # Add separator
            self.results_text.insert(tk.END, "\n" + "─" * 50 + "\n\n")
            
        self.add_to_history(self.search_var.get())

    def handle_click(self, _):
        """Handle left click on text widget"""
        for tag in self.results_text.tag_names(tk.CURRENT):
            if tag in self.tag_to_url:
                self.handle_link_click(self.tag_to_url[tag])
                break

    def handle_right_click(self, _):
        """Handle right click on text widget"""
        for tag in self.results_text.tag_names(tk.CURRENT):
            if tag in self.tag_to_url:
                self.copy_to_clipboard(self.tag_to_url[tag])
                break

    def handle_link_click(self, url):
        """Handle clicking a link"""
        if messagebox.askyesno("Open URL",
                             "Do you want to open this URL in Tor Browser?"):
            self.open_in_tor_browser(url)

    def copy_to_clipboard(self, url):
        """Copy URL to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(url)
        self.status_var.set("URL copied to clipboard")

    def add_to_history(self, query):
        """Add search query to history"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {"query": query, "timestamp": timestamp}
        self.search_history.append(entry)
        
        # Update history tab
        self.history_text.delete(1.0, tk.END)
        for item in reversed(self.search_history):
            self.history_text.insert(tk.END,
                                   f"{item['timestamp']} - {item['query']}\n")
        
        # Save to file
        if self.save_path:
            try:
                with open(self.save_path, "a") as f:
                    json.dump(entry, f)
                    f.write("\n")
            except Exception as e:
                self.status_var.set(f"Failed to save to history: {e}")

    def perform_search(self):
        """Perform dark web search"""
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query")
            return
        
        selected_engines = []
        if self.ahmia_var.get():
            selected_engines.append("ahmia")
        if self.torch_var.get():
            selected_engines.append("torch")
        if self.haystak_var.get():
            selected_engines.append("haystak")
        
        if not selected_engines:
            messagebox.showwarning("Warning", "Please select at least one search engine")
            return
        
        self.status_var.set("Searching...")
        SearchThread(self.darksheets, query, self.callback_handler,
                    self.save_path, selected_engines).start()

    def setup_tor_proxy(self):
        """Configure SOCKS proxy for Tor"""
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
        socket.socket = socks.socksocket

    def log_message(self, message, level="info"):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", level)
        self.log_text.see(tk.END)

    def check_connection(self):
        """Check Tor connection and update metrics"""
        self.log_message("Checking Tor connection...")
        
        def check():
            try:
                start_time = time.time()
                sock = socks.socksocket()
                sock.set_proxy(socks.SOCKS5, "127.0.0.1", 9050)
                sock.settimeout(10)
                
                # Check connection
                sock.connect(("check.torproject.org", 443))
                latency = (time.time() - start_time) * 1000  # Convert to ms
                
                # Get IP
                response = requests.get('https://check.torproject.org/api/ip')
                data = response.json()
                
                # Update UI
                self.root.after(0, lambda: self.update_connection_info(True, latency, data.get('IP', 'Unknown')))
                self.log_message("Connection check successful!", "success")
                
            except Exception as e:
                self.root.after(0, lambda: self.update_connection_info(False, None, None))
                self.log_message(f"Connection check failed: {str(e)}", "error")
            
            finally:
                if 'sock' in locals():
                    sock.close()
        
        threading.Thread(target=check, daemon=True).start()

    def update_connection_info(self, connected, latency=None, ip=None):
        """Update connection information display"""
        if connected:
            self.conn_status_var.set("Connected to Tor")
            self.latency_var.set(f"Latency: {latency:.0f}ms")
            self.ip_var.set(f"IP: {ip}")
        else:
            self.conn_status_var.set("Not Connected")
            self.latency_var.set("Latency: --")
            self.ip_var.set("IP: --")

    def run(self):
        """Start the GUI"""
        self.setup_tor_proxy()
        self.root.mainloop()

def main():
    gui = DarkWebGUI()
    gui.run()

if __name__ == "__main__":
    main()
