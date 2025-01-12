#!/usr/bin/env python3
"""
DarkSheets GUI - Dark Web Search Interface
"""
import tkinter as tk
from tkinter import ttk, messagebox, font
import threading
import queue
import webbrowser
from datetime import datetime
import logging
import os
import sys
import subprocess

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from darksheets import DarkSheets

# Configure logging
log_file = os.path.join(os.path.dirname(current_dir), 'darksheets.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file, encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Theme configuration
THEME = {
    'dark': {
        'bg_primary': '#1E1E1E',
        'bg_secondary': '#252526',
        'bg_tertiary': '#2D2D2D',
        'fg_primary': '#FFFFFF',
        'fg_secondary': '#CCCCCC',
        'accent': '#007ACC',
        'accent_hover': '#1C97EA',
        'success': '#4CAF50',
        'warning': '#FFA500',
        'error': '#FF3333',
        'font_family': 'Segoe UI',
        'font_size': {
            'small': 9,
            'normal': 10,
            'large': 12,
            'title': 24,
            'header': 32
        }
    }
}

class BaseFrame(tk.Frame):
    """Base frame with common functionality"""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.theme = THEME['dark']
        self.configure(bg=self.theme['bg_primary'])
        
    def create_label(self, text, size='normal', fg=None, bold=False):
        """Create a themed label"""
        if fg is None:
            fg = self.theme['fg_primary']
            
        font_weight = 'bold' if bold else 'normal'
        font_spec = (self.theme['font_family'], 
                    self.theme['font_size'][size], 
                    font_weight)
        
        return tk.Label(
            self,
            text=text,
            fg=fg,
            bg=self.theme['bg_primary'],
            font=font_spec
        )

class ModernButton(tk.Button):
    """Modern styled button"""
    def __init__(self, master=None, **kwargs):
        self.theme = THEME['dark']
        super().__init__(master, **kwargs)
        
        self.configure(
            relief=tk.FLAT,
            bd=0,
            bg=self.theme['accent'],
            fg=self.theme['fg_primary'],
            activebackground=self.theme['accent_hover'],
            activeforeground=self.theme['fg_primary'],
            font=(self.theme['font_family'], 
                  self.theme['font_size']['normal']),
            cursor='hand2',
            padx=15,
            pady=8
        )
        
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, _):
        self['background'] = self.theme['accent_hover']
    
    def _on_leave(self, _):
        self['background'] = self.theme['accent']

class ModernEntry(ttk.Entry):
    """Modern styled entry"""
    def __init__(self, master=None, **kwargs):
        self.theme = THEME['dark']
        
        style = ttk.Style()
        style.configure(
            'Modern.TEntry',
            fieldbackground=self.theme['bg_tertiary'],
            foreground=self.theme['fg_primary'],
            insertcolor=self.theme['fg_primary']
        )
        
        kwargs['style'] = 'Modern.TEntry'
        super().__init__(master, **kwargs)

class SearchFrame(BaseFrame):
    """Frame containing search controls"""
    def __init__(self, master=None, on_search=None):
        super().__init__(master)
        self.on_search = on_search
        self.search_var = tk.StringVar()
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the search UI"""
        # Search bar
        search_container = tk.Frame(self, bg=self.theme['bg_primary'])
        search_container.pack(fill='x', pady=(0, 10))
        
        self.search_entry = ModernEntry(
            search_container,
            textvariable=self.search_var,
            font=(self.theme['font_family'], 
                  self.theme['font_size']['large'])
        )
        self.search_entry.pack(side='left', expand=True, fill='x', padx=(0, 10))
        self.search_entry.bind('<Return>', self._handle_search)
        
        self.search_button = ModernButton(
            search_container,
            text="Search",
            command=self._handle_search
        )
        self.search_button.pack(side='right')
        
        # Search engines frame with scrollable area
        engines_frame = tk.Frame(self, bg=self.theme['bg_primary'])
        engines_frame.pack(fill='x')
        
        # Create canvas and scrollbar for engines
        canvas = tk.Canvas(
            engines_frame,
            bg=self.theme['bg_primary'],
            height=40,
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            engines_frame,
            orient='horizontal',
            command=canvas.xview
        )
        
        # Configure canvas scrolling
        canvas.configure(xscrollcommand=scrollbar.set)
        scrollbar.pack(side='bottom', fill='x')
        canvas.pack(side='top', fill='x', expand=True)
        
        # Create frame for checkbuttons inside canvas
        self.engines_container = tk.Frame(canvas, bg=self.theme['bg_primary'])
        canvas.create_window((0, 0), window=self.engines_container, anchor='nw')
        
        # Configure canvas scrolling
        self.engines_container.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        style = ttk.Style()
        style.configure(
            'Modern.TCheckbutton',
            background=self.theme['bg_primary'],
            foreground=self.theme['fg_primary']
        )
        
        # Add more search engines
        self.engine_vars = {
            'DuckDuckGo': tk.BooleanVar(value=True),
            'Ahmia': tk.BooleanVar(value=True),
            'Torch': tk.BooleanVar(value=True),
            'Kilos': tk.BooleanVar(value=True),
            'Recon': tk.BooleanVar(value=True)
        }
        
        for name, var in self.engine_vars.items():
            cb = ttk.Checkbutton(
                self.engines_container,
                text=name,
                variable=var,
                style='Modern.TCheckbutton'
            )
            cb.pack(side='left', padx=(0, 15))
    
    def _handle_search(self, event=None):
        """Handle search action"""
        if self.on_search:
            query = self.search_var.get().strip()
            engines = {k.lower(): v.get() 
                      for k, v in self.engine_vars.items()}
            self.on_search(query, engines)
    
    def set_enabled(self, enabled):
        """Enable or disable search controls"""
        state = 'normal' if enabled else 'disabled'
        self.search_entry.configure(state=state)
        self.search_button.configure(state=state)

class ResultCard(BaseFrame):
    """Card displaying a search result"""
    def __init__(self, master=None, result=None):
        super().__init__(master)
        self.result = result
        self.configure(
            bg=self.theme['bg_secondary'],
            padx=15,
            pady=15
        )
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the result card UI"""
        # Source badge
        source_badge = tk.Label(
            self,
            text=f" {self.result.get('source', 'Unknown')} ",
            fg=self.theme['bg_primary'],
            bg=self.theme['accent'],
            font=(self.theme['font_family'], 
                  self.theme['font_size']['small']),
            padx=8,
            pady=2
        )
        source_badge.pack(anchor='w', pady=(0, 5))
        
        # Title with link
        title = tk.Label(
            self,
            text=self.result.get('title', 'No Title'),
            fg=self.theme['accent'],
            bg=self.theme['bg_secondary'],
            font=(self.theme['font_family'], 
                  self.theme['font_size']['large'], 
                  'bold'),
            cursor='hand2',
            wraplength=800,
            justify='left'
        )
        title.pack(anchor='w')
        title.bind('<Button-1>', 
                  lambda e: webbrowser.open(self.result.get('url', '')))
        
        # URL
        url = tk.Label(
            self,
            text=self.result.get('url', ''),
            fg=self.theme['fg_secondary'],
            bg=self.theme['bg_secondary'],
            font=(self.theme['font_family'], 
                  self.theme['font_size']['small']),
            wraplength=800,
            justify='left'
        )
        url.pack(anchor='w', pady=(2, 5))
        
        # Description
        desc = tk.Label(
            self,
            text=self.result.get('description', 'No description available'),
            fg=self.theme['fg_primary'],
            bg=self.theme['bg_secondary'],
            wraplength=800,
            justify='left'
        )
        desc.pack(anchor='w')
        
        # Footer
        footer = tk.Frame(self, bg=self.theme['bg_secondary'])
        footer.pack(fill='x', pady=(10, 0))
        
        # Add "Open in Tor" button
        tor_button = ModernButton(
            footer,
            text="Open in Tor",
            command=lambda: self.open_in_tor()
        )
        tor_button.pack(side='left')
        
        timestamp = tk.Label(
            footer,
            text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            fg=self.theme['fg_secondary'],
            bg=self.theme['bg_secondary'],
            font=(self.theme['font_family'], 
                  self.theme['font_size']['small'])
        )
        timestamp.pack(side='right')
    
    def open_in_tor(self):
        """Open the result URL in Tor Browser"""
        url = self.result.get('url', '')
        if url:
            try:
                subprocess.Popen([
                    os.path.expanduser("~\\Desktop\\Tor Browser\\Browser\\firefox.exe"),
                    url
                ])
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Failed to open Tor Browser: {str(e)}"
                )

class ResultsFrame(BaseFrame):
    """Frame displaying search results"""
    def __init__(self, master=None):
        super().__init__(master)
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the results UI"""
        # Create canvas for scrolling
        self.canvas = tk.Canvas(
            self,
            bg=self.theme['bg_secondary'],
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            self,
            orient='vertical',
            command=self.canvas.yview
        )
        
        # Configure canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', expand=True, fill='both')
        
        # Create frame for results
        self.results_container = tk.Frame(
            self.canvas,
            bg=self.theme['bg_secondary']
        )
        self.canvas_frame = self.canvas.create_window(
            (0, 0),
            window=self.results_container,
            anchor='nw'
        )
        
        # Configure scrolling
        self.results_container.bind(
            '<Configure>',
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox('all')
            )
        )
        self.canvas.bind(
            '<Configure>',
            lambda e: self.canvas.itemconfig(
                self.canvas_frame,
                width=e.width
            )
        )
        
        # Mouse wheel scrolling
        self.canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(
                int(-1 * (e.delta / 120)),
                "units"
            )
        )
    
    def clear(self):
        """Clear all results"""
        for widget in self.results_container.winfo_children():
            widget.destroy()
    
    def add_result(self, result):
        """Add a new result card"""
        card = ResultCard(self.results_container, result)
        card.pack(fill='x', padx=10, pady=5)

class StatusBar(BaseFrame):
    """Status bar showing connection and search status"""
    def __init__(self, master=None):
        super().__init__(master)
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the status bar UI"""
        self.connection_label = self.create_label(
            "● Connecting...",
            fg=self.theme['warning']
        )
        self.connection_label.pack(side='left')
        
        self.status_label = self.create_label(
            "Ready",
            fg=self.theme['fg_secondary']
        )
        self.status_label.pack(side='right')
        
        self.progress = ttk.Progressbar(
            self,
            mode='indeterminate',
            length=200
        )
    
    def set_connection_status(self, connected):
        """Update connection status"""
        if connected:
            self.connection_label.configure(
                text="● Connected",
                fg=self.theme['success']
            )
        else:
            self.connection_label.configure(
                text="● Disconnected",
                fg=self.theme['error']
            )
    
    def set_status(self, text, show_progress=False):
        """Update status text and progress bar"""
        self.status_label.configure(text=text)
        
        if show_progress:
            self.progress.pack(side='right', padx=10)
            self.progress.start(15)
        else:
            self.progress.stop()
            self.progress.pack_forget()

class MainWindow:
    """Main application window"""
    def __init__(self):
        self.setup_window()
        self.setup_variables()
        self.setup_ui()
    
    def setup_window(self):
        """Initialize the main window"""
        self.root = tk.Tk()
        self.root.title("DarkSheets - Dark Web Search")
        self.root.state('zoomed')
        self.root.configure(bg=THEME['dark']['bg_primary'])
        
        # Set default font
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(
            family=THEME['dark']['font_family'],
            size=THEME['dark']['font_size']['normal']
        )
        self.root.option_add("*Font", default_font)
    
    def setup_variables(self):
        """Initialize variables and state"""
        self.darksheets = DarkSheets()
        self.results_queue = queue.Queue()
        self.is_searching = False
    
    def setup_ui(self):
        """Initialize the user interface"""
        # Main container
        self.main_container = BaseFrame(self.root)
        self.main_container.pack(
            expand=True,
            fill='both',
            padx=30,
            pady=20
        )
        
        # Header
        header = BaseFrame(self.main_container)
        header.pack(fill='x', pady=(0, 20))
        
        title = header.create_label(
            "🌐 DarkSheets",
            size='title',
            fg=THEME['dark']['accent'],
            bold=True
        )
        title.pack(side='left')
        
        # Search section
        self.search_frame = SearchFrame(
            self.main_container,
            on_search=self.handle_search
        )
        self.search_frame.pack(fill='x', pady=(0, 20))
        
        # Results section
        self.results_frame = ResultsFrame(self.main_container)
        self.results_frame.pack(expand=True, fill='both')
        
        # Status bar
        self.status_bar = StatusBar(self.main_container)
        self.status_bar.pack(fill='x', pady=(10, 0))
    
    def handle_search(self, query, engines):
        """Handle search request"""
        if not query:
            messagebox.showwarning(
                "Warning",
                "Please enter a search query"
            )
            return
        
        if self.is_searching:
            return
        
        # Clear previous results
        self.results_frame.clear()
        
        # Update UI state
        self.is_searching = True
        self.search_frame.set_enabled(False)
        self.status_bar.set_status("Searching...", True)
        
        def search():
            try:
                results = self.darksheets.search_dark_web(query, engines)
                for result in results:
                    self.results_queue.put(result)
                
                self.root.after(0, self.update_results)
            except Exception as e:
                logger.error(f"Search error: {str(e)}")
                self.root.after(
                    0,
                    lambda: messagebox.showerror(
                        "Error",
                        f"Search failed: {str(e)}"
                    )
                )
            finally:
                self.is_searching = False
                self.root.after(0, lambda: (
                    self.search_frame.set_enabled(True),
                    self.status_bar.set_status("Search complete")
                ))
        
        threading.Thread(target=search, daemon=True).start()
    
    def update_results(self):
        """Update results from queue"""
        while not self.results_queue.empty():
            result = self.results_queue.get()
            self.results_frame.add_result(result)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Entry point"""
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        messagebox.showerror(
            "Error",
            f"An error occurred: {str(e)}\n\n"
            "Please check the log file for details."
        )

if __name__ == "__main__":
    main()
