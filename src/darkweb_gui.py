import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import winreg
import threading
import queue
import json
from datetime import datetime
from .darksheets import DarkSheets
import socks
import socket
import os
import ctypes

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

class DarkWebGUI:
    def __init__(self):
        self.darksheets = DarkSheets()
        self.save_path = None
        self.search_history = []
        self.tor_browser_path = None
        self.root = tk.Tk()
        self.status_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.ahmia_var = tk.BooleanVar(value=True)
        self.torch_var = tk.BooleanVar(value=True)
        self.haystak_var = tk.BooleanVar(value=True)
        self.tag_to_url = {}
        self.init_ui()
        # Start Tor connection immediately
        TorThread(self.darksheets, None, self.callback_handler, connect=True).start()

    def init_ui(self):
        """Initialize the user interface"""
        self.root.title("DarkSheets - Dark Web Research Tool")
        self.root.geometry("800x600")
        
        # Configure dark theme
        style = ttk.Style()
        style.configure("TFrame", background="#2b2b2b")
        style.configure("TLabel", background="#2b2b2b", foreground="white")
        style.configure("TButton", background="#363636", foreground="white")
        style.configure("TCheckbutton", background="#2b2b2b", foreground="white")
        
        self.root.configure(bg="#2b2b2b")
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search frame
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        search_label = ttk.Label(search_frame, text="Search Query:")
        search_label.pack(side=tk.LEFT, padx=5)
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        search_button = ttk.Button(search_frame, text="Search", command=self.perform_search)
        search_button.pack(side=tk.LEFT, padx=5)
        
        # Search engine options
        engine_frame = ttk.Frame(main_frame)
        engine_frame.pack(fill=tk.X, pady=5)
        
        ahmia_check = ttk.Checkbutton(engine_frame, text="Ahmia", variable=self.ahmia_var)
        ahmia_check.pack(side=tk.LEFT, padx=5)
        
        torch_check = ttk.Checkbutton(engine_frame, text="Torch", variable=self.torch_var)
        torch_check.pack(side=tk.LEFT, padx=5)
        
        haystak_check = ttk.Checkbutton(engine_frame, text="Haystak", variable=self.haystak_var)
        haystak_check.pack(side=tk.LEFT, padx=5)
        
        # Results text widget
        self.results_text = tk.Text(main_frame, wrap=tk.WORD, bg="#363636", fg="white",
                                  insertbackground="white", height=20)
        self.results_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.results_text.tag_configure("link", foreground="#00a8ff", underline=True)
        self.results_text.tag_bind("link", "<Button-1>", self.handle_click)
        self.results_text.tag_bind("link", "<Button-3>", self.handle_right_click)
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        connect_button = ttk.Button(control_frame, text="Connect Tor",
                                  command=self.connect_tor)
        connect_button.pack(side=tk.LEFT, padx=5)
        
        disconnect_button = ttk.Button(control_frame, text="Disconnect Tor",
                                     command=self.disconnect_tor)
        disconnect_button.pack(side=tk.LEFT, padx=5)
        
        check_button = ttk.Button(control_frame, text="Check Connection",
                                command=lambda: TorThread(self.darksheets, "check",
                                                       self.callback_handler).start())
        check_button.pack(side=tk.LEFT, padx=5)
        
        tor_path_button = ttk.Button(control_frame, text="Set Tor Path",
                                   command=self.set_tor_browser_path)
        tor_path_button.pack(side=tk.LEFT, padx=5)
        
        # Get Tor Browser path
        self.get_tor_browser_path()

    def callback_handler(self, msg_type, msg):
        """Handle callbacks from threads"""
        if msg_type == "search_complete":
            self.display_results(msg)
        elif msg_type in ["tor_connect", "tor_disconnect", "tor_status"]:
            self.status_var.set(msg)
        elif msg_type == "error":
            messagebox.showerror("Error", str(msg))

    def get_tor_browser_path(self):
        """Get Tor Browser path from registry or user selection"""
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe")
            path = winreg.QueryValue(key, None)
            if "Tor Browser" in path:
                self.tor_browser_path = path
                return
        except:
            pass
        
        self.set_tor_browser_path()

    def set_tor_browser_path(self):
        """Let user select Tor Browser location"""
        path = filedialog.askopenfilename(
            title="Select Tor Browser firefox.exe",
            filetypes=[("Executable files", "*.exe")]
        )
        if path and "Tor Browser" in path:
            self.tor_browser_path = path
        elif path:
            messagebox.showwarning("Warning",
                                 "Selected file is not Tor Browser. Please select firefox.exe from Tor Browser folder.")

    def open_in_tor_browser(self, url):
        """Open URL in Tor Browser"""
        if not self.tor_browser_path:
            messagebox.showerror("Error", "Tor Browser path not set")
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
            
            self.results_text.insert(tk.END, f"Engine: {result['engine']}\n")
            self.results_text.insert(tk.END, "URL: ")
            self.results_text.insert(tk.END, result["url"] + "\n", (tag, "link"))
            self.results_text.insert(tk.END, f"Title: {result['title']}\n\n")
            
        self.add_to_history(self.search_var.get())

    def handle_click(self, event):
        """Handle left click on text widget"""
        for tag in self.results_text.tag_names(tk.CURRENT):
            if tag in self.tag_to_url:
                self.handle_link_click(self.tag_to_url[tag])
                break

    def handle_right_click(self, event):
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
        self.search_history.append({"query": query, "timestamp": timestamp})
        
        # Save to file
        if self.save_path:
            try:
                with open(self.save_path, "a") as f:
                    json.dump({"query": query, "timestamp": timestamp}, f)
                    f.write("\n")
            except Exception as e:
                self.status_var.set(f"Failed to save to history: {e}")

    def connect_tor(self):
        """Connect to Tor network"""
        TorThread(self.darksheets, None, self.callback_handler, connect=True).start()

    def disconnect_tor(self):
        """Disconnect from Tor network"""
        TorThread(self.darksheets, "disconnect", self.callback_handler).start()

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

    def is_admin(self):
        """Check if running with admin privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def run(self):
        """Start the GUI"""
        if not self.is_admin() and messagebox.askyesno(
            "Admin Rights Required",
            "DarkSheets requires administrator privileges to configure Tor. "
            "Do you want to restart with admin rights?"
        ):
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit()
        
        self.setup_tor_proxy()
        self.root.mainloop()

def main():
    gui = DarkWebGUI()
    gui.run()

if __name__ == "__main__":
    main()
