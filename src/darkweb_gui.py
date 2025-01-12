import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import sys
import time
import socks
import socket
from datetime import datetime
import queue

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from darksheets import DarkSheets

# Dark mode colors
COLORS = {
    'bg_dark': '#1a1a1a',
    'bg_darker': '#141414',
    'bg_lighter': '#2a2a2a',
    'text': '#e0e0e0',
    'text_dim': '#888888',
    'accent': '#4a9eff',
}

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DarkSheets Login")
        self.root.configure(bg=COLORS['bg_dark'])
        
        # Center window
        window_width = 400
        window_height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Title
        title = tk.Label(self.root,
                        text="🌐 DarkSheets",
                        font=('Segoe UI', 24, 'bold'),
                        fg=COLORS['accent'],
                        bg=COLORS['bg_dark'])
        title.pack(pady=20)
        
        # Login frame
        frame = tk.Frame(self.root, bg=COLORS['bg_dark'])
        frame.pack(pady=20)
        
        # Username
        tk.Label(frame,
                text="Username:",
                fg=COLORS['text'],
                bg=COLORS['bg_dark'],
                font=('Segoe UI', 12)).grid(row=0, column=0, pady=5)
        self.username = ttk.Entry(frame, width=30)
        self.username.grid(row=0, column=1, pady=5)
        
        # Password
        tk.Label(frame,
                text="Password:",
                fg=COLORS['text'],
                bg=COLORS['bg_dark'],
                font=('Segoe UI', 12)).grid(row=1, column=0, pady=5)
        self.password = ttk.Entry(frame, width=30, show="●")
        self.password.grid(row=1, column=1, pady=5)
        
        # Login button
        login_btn = ttk.Button(self.root,
                             text="Login",
                             command=self.login)
        login_btn.pack(pady=20)
        
        # Status message
        self.status_label = tk.Label(self.root,
                                   text="Connecting to Tor...",
                                   fg=COLORS['text_dim'],
                                   bg=COLORS['bg_dark'])
        self.status_label.pack()
        
        # Bind Enter key
        self.username.bind('<Return>', lambda _: self.password.focus())
        self.password.bind('<Return>', lambda _: self.login())
        
        # Start Tor connection
        self.darksheets = DarkSheets()
        threading.Thread(target=self.connect_tor, daemon=True).start()
        
        # Focus username
        self.username.focus()
        
    def connect_tor(self):
        """Connect to Tor network"""
        try:
            # Configure SOCKS proxy
            socks.set_default_proxy(socks.SOCKS5, "localhost", 9050)
            socket.socket = socks.socksocket
            
            if self.darksheets.connect_tor():
                self.status_label.config(text="Connected to Tor")
            else:
                self.status_label.config(text="Failed to connect to Tor")
        except Exception as e:
            self.status_label.config(text=f"Connection error: {str(e)}")
    
    def login(self):
        """Handle login"""
        username = self.username.get()
        password = self.password.get()
        
        if username == "admin" and password == "admin":
            self.root.destroy()
            DarkWebGUI(self.darksheets)
        elif username and password:
            messagebox.showerror("Error", "Invalid credentials")
        else:
            messagebox.showerror("Error", "Please enter both username and password")

class DarkWebGUI:
    def __init__(self, darksheets):
        self.darksheets = darksheets
        self.root = tk.Tk()
        self.root.title('DarkSheets - Dark Web Research Tool')
        self.root.geometry('1200x800')
        self.root.configure(bg=COLORS['bg_dark'])
        
        self.search_var = tk.StringVar()
        self.ahmia_var = tk.BooleanVar(value=True)
        self.torch_var = tk.BooleanVar(value=True)
        self.haystak_var = tk.BooleanVar(value=True)
        
        # Configure modern styles
        self.setup_styles()
        self.init_ui()
        
    def setup_styles(self):
        """Configure modern dark theme styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure frame styles
        style.configure('Main.TFrame', background=COLORS['bg_dark'])
        style.configure('Card.TFrame', 
                       background=COLORS['bg_lighter'],
                       relief='solid',
                       borderwidth=1)
        
        # Configure label styles
        style.configure('Title.TLabel',
                       background=COLORS['bg_dark'],
                       foreground=COLORS['accent'],
                       font=('Segoe UI', 24, 'bold'))
        style.configure('Subtitle.TLabel',
                       background=COLORS['bg_dark'],
                       foreground=COLORS['text_dim'],
                       font=('Segoe UI', 12))
        style.configure('Info.TLabel',
                       background=COLORS['bg_dark'],
                       foreground=COLORS['text'],
                       font=('Segoe UI', 10))
        
        # Configure button styles
        style.configure('Search.TButton',
                       background=COLORS['accent'],
                       foreground=COLORS['text'],
                       padding=[20, 10],
                       font=('Segoe UI', 11, 'bold'))
        style.map('Search.TButton',
                 background=[('active', '#3a8eff'),
                           ('pressed', '#2a7eff')])
        
        # Configure entry style
        style.configure('Search.TEntry',
                       fieldbackground=COLORS['bg_darker'],
                       foreground=COLORS['text'],
                       insertcolor=COLORS['text'],
                       padding=[10, 8])
        
        # Configure notebook style
        style.configure('App.TNotebook',
                       background=COLORS['bg_dark'],
                       tabmargins=[2, 5, 2, 0])
        style.configure('App.TNotebook.Tab',
                       background=COLORS['bg_darker'],
                       foreground=COLORS['text'],
                       padding=[15, 8],
                       font=('Segoe UI', 10))
        style.map('App.TNotebook.Tab',
                 background=[('selected', COLORS['bg_lighter'])],
                 foreground=[('selected', COLORS['text'])])
        
    def init_ui(self):
        """Initialize the user interface"""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, style='Main.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Header section
        header_frame = ttk.Frame(main_frame, style='Main.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Title and subtitle
        title_frame = ttk.Frame(header_frame, style='Main.TFrame')
        title_frame.pack(side=tk.LEFT)
        
        ttk.Label(title_frame,
                 text="🌐 DarkSheets",
                 style='Title.TLabel').pack(side=tk.LEFT)
        
        ttk.Label(title_frame,
                 text="Dark Web Research Tool",
                 style='Subtitle.TLabel').pack(side=tk.LEFT, padx=(10, 0), pady=(8, 0))
        
        # Status section
        status_frame = ttk.Frame(header_frame, style='Card.TFrame')
        status_frame.pack(side=tk.RIGHT, pady=(8, 0), padx=10)
        
        self.status_label = ttk.Label(status_frame,
                                    text="⚡ Connected via Tor",
                                    style='Info.TLabel')
        self.status_label.pack(padx=10, pady=5)
        
        # Search section
        search_frame = ttk.Frame(main_frame, style='Main.TFrame')
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Search entry with icon
        entry_frame = ttk.Frame(search_frame, style='Main.TFrame')
        entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Label(entry_frame,
                 text="🔍",
                 style='Info.TLabel').pack(side=tk.LEFT, padx=(5, 0))
        
        self.search_entry = ttk.Entry(entry_frame,
                                    textvariable=self.search_var,
                                    style='Search.TEntry',
                                    font=('Segoe UI', 12))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Search button
        search_button = ttk.Button(search_frame,
                                 text="Search",
                                 style='Search.TButton',
                                 command=self.perform_search)
        search_button.pack(side=tk.RIGHT)
        
        # Engine selection
        engines_frame = ttk.Frame(main_frame, style='Card.TFrame')
        engines_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(engines_frame,
                 text="Search Engines",
                 style='Info.TLabel').pack(side=tk.LEFT, padx=10, pady=5)
        
        for engine, var in [("🔍 Ahmia", self.ahmia_var),
                          ("🔦 Torch", self.torch_var),
                          ("🌾 Haystak", self.haystak_var)]:
            cb = ttk.Checkbutton(engines_frame,
                               text=engine,
                               variable=var)
            cb.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Notebook for results, history, and log
        self.notebook = ttk.Notebook(main_frame, style='App.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Results tab
        results_frame = ttk.Frame(self.notebook, style='Main.TFrame')
        self.notebook.add(results_frame, text="📊 Results")
        
        self.results_text = tk.Text(results_frame,
                                  bg=COLORS['bg_darker'],
                                  fg=COLORS['text'],
                                  font=('Consolas', 10),
                                  wrap=tk.WORD,
                                  padx=10,
                                  pady=10)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # History tab
        history_frame = ttk.Frame(self.notebook, style='Main.TFrame')
        self.notebook.add(history_frame, text="📜 History")
        
        self.history_text = tk.Text(history_frame,
                                  bg=COLORS['bg_darker'],
                                  fg=COLORS['text'],
                                  font=('Consolas', 10),
                                  wrap=tk.WORD,
                                  padx=10,
                                  pady=10)
        self.history_text.pack(fill=tk.BOTH, expand=True)
        
        # Log tab
        log_frame = ttk.Frame(self.notebook, style='Main.TFrame')
        self.notebook.add(log_frame, text="📝 Log")
        
        self.log_text = tk.Text(log_frame,
                              bg=COLORS['bg_darker'],
                              fg=COLORS['text'],
                              font=('Consolas', 10),
                              wrap=tk.WORD,
                              padx=10,
                              pady=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Bind Enter key to search
        self.search_entry.bind('<Return>', lambda e: self.perform_search())
        
        # Add initial log message
        self.log_message("DarkSheets started successfully")
        
    def perform_search(self):
        """Execute search query"""
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query")
            return
        
        # Get enabled search engines
        engines = {
            'ahmia': self.ahmia_var.get(),
            'torch': self.torch_var.get(),
            'haystak': self.haystak_var.get()
        }
        
        # Log the search
        self.log_message(f"Searching for: {query}")
        self.history_text.insert(1.0, f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {query}\n")
        
        # Clear results
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Searching...\n")
        
        # Create a queue for thread communication
        result_queue = queue.Queue()
        
        def search():
            try:
                results = self.darksheets.search_dark_web(query, engines)
                result_queue.put(('success', results))
            except Exception as e:
                result_queue.put(('error', str(e)))
        
        def check_results():
            try:
                if not result_queue.empty():
                    status, data = result_queue.get_nowait()
                    if status == 'success':
                        self.update_results(data)
                    else:
                        self.handle_error(data)
                    return
                self.root.after(100, check_results)
            except Exception as e:
                self.handle_error(f"Error checking results: {str(e)}")
        
        # Start search thread and checker
        threading.Thread(target=search, daemon=True).start()
        self.root.after(100, check_results)
    
    def update_results(self, results):
        """Update results in text widget"""
        self.results_text.delete(1.0, tk.END)
        if results:
            for i, result in enumerate(results, 1):
                self.results_text.insert(tk.END, f"Result #{i}\n")
                self.results_text.insert(tk.END, f"{'='*50}\n")
                self.results_text.insert(tk.END, f"Title: {result['title']}\n")
                self.results_text.insert(tk.END, f"URL: {result['url']}\n")
                self.results_text.insert(tk.END, f"Description: {result['description']}\n\n")
            self.log_message(f"Found {len(results)} results")
        else:
            self.results_text.insert(tk.END, "No results found.")
            self.log_message("Search completed with no results")
    
    def handle_error(self, error_msg):
        """Handle search errors"""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Error: {error_msg}")
        self.log_message(f"Error during search: {error_msg}")
        messagebox.showerror("Search Error", error_msg)
    
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(1.0, f"[{timestamp}] {message}\n")
        self.log_text.see("1.0")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    login = LoginWindow()
    login.root.mainloop()

if __name__ == "__main__":
    main()
