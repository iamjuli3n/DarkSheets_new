"""
DarkSheets GUI Interface with Dark Mode Styling
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import sys
import time
import socks
import socket

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from darksheets import DarkSheets

class SearchThread(threading.Thread):
    """Thread for performing dark web searches"""
    def __init__(self, darksheets_instance, query, callback):
        super().__init__()
        self.darksheets = darksheets_instance
        self.query = query
        self.callback = callback
        
    def run(self):
        """Run the thread"""
        try:
            def progress_callback(msg):
                self.callback("log", msg)
                
            self.darksheets.console.print = progress_callback
            results = self.darksheets.search_dark_web(self.query)
            self.callback("results", results)
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
        """Run the thread"""
        try:
            if self.operation == 'connect' or self.connect:
                # Configure SOCKS proxy
                socks.set_default_proxy(socks.SOCKS5, "localhost", 9050)
                socket.socket = socks.socksocket
                
                # Connect to Tor
                if self.darksheets.connect_tor():
                    self.callback("log", "Connected to Tor network")
                else:
                    self.callback("log", "Failed to connect to Tor")
            elif self.operation == 'disconnect':
                if self.darksheets.disconnect_tor():
                    self.callback("log", "Disconnected from Tor network")
                else:
                    self.callback("log", "Failed to disconnect from Tor")
        except Exception as e:
            self.callback("log", f"Tor operation error: {str(e)}")

class DarkWebGUI:
    def __init__(self):
        self.darksheets = DarkSheets()
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
        self.root.title('DarkSheets - Dark Web Research Tool')
        self.root.geometry('1200x800')
        
        # Configure modern dark theme
        self.root.configure(bg='#1a1a1a')  # Darker background
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure modern styles
        style.configure('TFrame', background='#1a1a1a')
        style.configure('TLabel', background='#1a1a1a', foreground='#e0e0e0', font=('Segoe UI', 10))
        style.configure('TButton', 
                       background='#333333', 
                       foreground='#e0e0e0',
                       padding=[15, 8],
                       font=('Segoe UI', 10))
        style.map('TButton',
                 background=[('active', '#404040'), ('pressed', '#505050')],
                 foreground=[('active', '#ffffff')])
        
        style.configure('Search.TButton',  # Special style for search button
                       background='#2962ff',
                       foreground='white',
                       padding=[20, 10],
                       font=('Segoe UI', 11, 'bold'))
        style.map('Search.TButton',
                 background=[('active', '#1e88e5'), ('pressed', '#1976d2')])
                 
        style.configure('TCheckbutton', 
                       background='#1a1a1a',
                       foreground='#e0e0e0',
                       font=('Segoe UI', 10))
        
        # Configure notebook style
        style.configure('TNotebook', 
                       background='#1a1a1a',
                       tabmargins=[2, 5, 2, 0])
        style.configure('TNotebook.Tab',
                       background='#333333',
                       foreground='#e0e0e0',
                       padding=[15, 8],
                       font=('Segoe UI', 10))
        style.map('TNotebook.Tab',
                 background=[('selected', '#404040')],
                 foreground=[('selected', '#ffffff')])
        
        # Main frame with padding
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Header with modern design
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Title with icon
        title_text = "🌐 DarkSheets"
        title_label = ttk.Label(header_frame, 
                              text=title_text,
                              font=('Segoe UI', 24, 'bold'),
                              foreground='#4a9eff')
        title_label.pack(side=tk.LEFT)
        
        # Subtitle
        subtitle_label = ttk.Label(header_frame,
                                text="Dark Web Research Tool",
                                font=('Segoe UI', 12),
                                foreground='#888888')
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0), pady=(8, 0))
        
        # Tor status and setup in header
        tor_frame = ttk.Frame(header_frame)
        tor_frame.pack(side=tk.RIGHT, pady=(8, 0))
        
        self.setup_tor_button = ttk.Button(tor_frame,
                                         text="⚡ Configure SOCKS",
                                         style='TButton',
                                         command=self.setup_tor_proxy)
        self.setup_tor_button.pack(side=tk.LEFT, padx=5)
        
        self.tor_status = ttk.Label(tor_frame, 
                                  text="Disconnected",
                                  font=('Segoe UI', 10),
                                  foreground='#ff4444')
        self.tor_status.pack(side=tk.LEFT)
        
        # Search frame with modern layout
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Search entry with modern style
        search_entry = ttk.Entry(search_frame, 
                               textvariable=self.search_var,
                               font=('Segoe UI', 12))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Search button with modern style
        search_button = ttk.Button(search_frame,
                                text="🔍 Search",
                                style='Search.TButton',
                                command=self.perform_search)
        search_button.pack(side=tk.RIGHT)
        
        # Engine selection with modern checkboxes
        engines_frame = ttk.Frame(main_frame)
        engines_frame.pack(fill=tk.X, pady=(0, 15))
        
        engines_label = ttk.Label(engines_frame,
                               text="Search Engines:",
                               font=('Segoe UI', 10, 'bold'))
        engines_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Engine checkboxes
        ahmia_cb = ttk.Checkbutton(engines_frame,
                                 text="Ahmia",
                                 variable=self.ahmia_var)
        ahmia_cb.pack(side=tk.LEFT, padx=5)
        
        torch_cb = ttk.Checkbutton(engines_frame,
                                text="Torch",
                                variable=self.torch_var)
        torch_cb.pack(side=tk.LEFT, padx=5)
        
        haystak_cb = ttk.Checkbutton(engines_frame,
                                  text="Haystak",
                                  variable=self.haystak_var)
        haystak_cb.pack(side=tk.LEFT, padx=5)
        
        # Results notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Results tab
        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text="Results")
        
        self.results_text = tk.Text(results_frame,
                                  bg='#141414',
                                  fg='#e0e0e0',
                                  font=('Consolas', 10))
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Log tab
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="Log")
        
        self.log_text = tk.Text(log_frame,
                               bg='#141414',
                               fg='#e0e0e0',
                               font=('Consolas', 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def setup_tor_proxy(self):
        """Configure SOCKS proxy settings"""
        pass  # Implement SOCKS configuration dialog

    def perform_search(self):
        """Execute search query"""
        query = self.search_var.get()
        if not query:
            return
            
        self.log_message(f"Searching for: {query}")
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Searching...\n")
        
        # Start search in background thread
        SearchThread(self.darksheets, query, self.callback_handler).start()

    def callback_handler(self, msg_type, msg):
        """Handle callbacks from threads"""
        if msg_type == "log":
            self.log_message(msg)
        elif msg_type == "results":
            self.update_results(msg)
        elif msg_type == "error":
            self.log_message(f"Error: {msg}")
            messagebox.showerror("Error", str(msg))

    def update_results(self, results):
        """Update results in text widget"""
        self.results_text.delete(1.0, tk.END)
        if not results:
            self.results_text.insert(tk.END, "No results found\n")
            return
            
        for result in results:
            self.results_text.insert(tk.END, f"{result}\n")
            
        self.log_message("Search completed successfully")

    def log_message(self, message):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    gui = DarkWebGUI()
    gui.run()

if __name__ == "__main__":
    main()
