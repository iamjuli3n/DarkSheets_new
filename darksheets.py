import customtkinter as ctk
import socket
import requests
import subprocess
import threading
import platform
import os
from datetime import datetime
from PIL import Image
import json
from bs4 import BeautifulSoup
import webbrowser
import socks
import stem.process
from stem.control import Controller
import time
import re

class TorConnection:
    def __init__(self):
        self.tor_process = None
        self.tor_port = 9050
        self.control_port = 9051
        self.tor_path = os.path.join(os.getcwd(), "tor", "Tor", "tor.exe")
        
    def start_tor(self):
        try:
            if not os.path.exists(self.tor_path):
                raise Exception("Tor executable not found. Please run install_tor.ps1 first")
                
            # Configuration for Tor
            tor_config = {
                'SocksPort': str(self.tor_port),
                'ControlPort': str(self.control_port),
                'DataDirectory': os.path.join(os.getcwd(), 'tor_data'),
                'GeoIPFile': os.path.join(os.path.dirname(self.tor_path), 'geoip'),
                'GeoIPv6File': os.path.join(os.path.dirname(self.tor_path), 'geoip6'),
            }
            
            # Start Tor process
            self.tor_process = stem.process.launch_tor_with_config(
                config=tor_config,
                init_msg_handler=lambda line: print(line) if re.search("Bootstrapped", line) else False,
                tor_cmd=self.tor_path,
                take_ownership=True
            )
            
            # Configure requests to use Tor
            session = requests.Session()
            session.proxies = {
                'http': f'socks5h://127.0.0.1:{self.tor_port}',
                'https': f'socks5h://127.0.0.1:{self.tor_port}'
            }
            
            return session
            
        except Exception as e:
            raise Exception(f"Failed to start Tor: {str(e)}")
            
    def stop_tor(self):
        if self.tor_process:
            self.tor_process.kill()
            self.tor_process = None

class DarkSheetsApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.root = ctk.CTk()
        self.root.title("DarkSheets Research Tool")
        self.root.geometry("1200x800")
        
        # Initialize Tor connection
        self.tor = TorConnection()
        self.tor_session = None
        
        # Create main container with two columns
        self.create_layout()
        self.create_left_panel()
        self.create_right_panel()
        
        # Initialize results storage
        self.search_results = []
        
    def create_layout(self):
        # Configure grid layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=2)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create main frames
        self.left_frame = ctk.CTkFrame(self.root)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.right_frame = ctk.CTkFrame(self.root)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
    def create_left_panel(self):
        # Title
        title_label = ctk.CTkLabel(
            self.left_frame,
            text="DarkSheets",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # System Info
        info_frame = ctk.CTkFrame(self.left_frame)
        info_frame.pack(fill="x", padx=10, pady=10)
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="System Information",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        info_label.pack(pady=5)
        
        self.info_text = ctk.CTkTextbox(
            info_frame,
            height=150,
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.info_text.pack(padx=10, pady=5, fill="x")
        
        # Control buttons
        buttons_frame = ctk.CTkFrame(self.left_frame)
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        buttons = [
            ("Refresh Info", self.update_system_info),
            ("Check Tor", self.check_tor_status),
            ("Connect to Tor", self.configure_tor),
            ("Search Ahmia.fi", self.perform_search),
        ]
        
        for text, command in buttons:
            btn = ctk.CTkButton(
                buttons_frame,
                text=text,
                command=command,
                height=35
            )
            btn.pack(pady=5, fill="x")
        
        # Search frame
        search_frame = ctk.CTkFrame(self.left_frame)
        search_frame.pack(fill="x", padx=10, pady=10)
        
        search_label = ctk.CTkLabel(
            search_frame,
            text="Search Query",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        search_label.pack(pady=5)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Enter search term..."
        )
        self.search_entry.pack(pady=5, fill="x")
        
    def create_right_panel(self):
        # Configure grid
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(1, weight=1)
        
        # Results label
        results_label = ctk.CTkLabel(
            self.right_frame,
            text="Search Results",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        results_label.grid(row=0, column=0, pady=10)
        
        # Results text
        self.results_text = ctk.CTkTextbox(
            self.right_frame,
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.results_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        # Action buttons frame
        action_frame = ctk.CTkFrame(self.right_frame)
        action_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        # Export button
        export_btn = ctk.CTkButton(
            action_frame,
            text="Export Results",
            command=self.export_results,
            height=35
        )
        export_btn.pack(side="left", padx=5)
        
        # Clear button
        clear_btn = ctk.CTkButton(
            action_frame,
            text="Clear Results",
            command=self.clear_results,
            height=35
        )
        clear_btn.pack(side="left", padx=5)
        
    def update_system_info(self):
        try:
            hostname = socket.gethostname()
            internal_ip = socket.gethostbyname(hostname)
            
            # Get IP through Tor if connected
            if self.tor_session:
                try:
                    external_ip = self.tor_session.get('https://api.ipify.org').text
                    self.add_to_results("Successfully retrieved IP through Tor")
                except:
                    external_ip = "Unable to get IP through Tor"
                    self.add_to_results("Failed to get IP through Tor", error=True)
            else:
                external_ip = "Tor not connected"
            
            os_info = platform.platform()
            
            info = f"""System Information:
━━━━━━━━━━━━━━━━━━━━━━━━
• Hostname: {hostname}
• Internal IP: {internal_ip}
• Tor IP: {external_ip}
• OS: {os_info}
• Directory: {os.getcwd()}
• Tor Status: {"Connected" if self.tor_session else "Not Connected"}
━━━━━━━━━━━━━━━━━━━━━━━━"""
            
            self.info_text.delete("0.0", "end")
            self.info_text.insert("0.0", info)
            self.add_to_results("System information updated successfully")
            
        except Exception as e:
            self.add_to_results(f"Error updating system info: {str(e)}", error=True)
    
    def check_tor_status(self):
        def check():
            try:
                if not self.tor_session:
                    self.add_to_results("Tor is not connected")
                    return
                
                # Try to access a .onion site through Tor
                test_url = "http://ahmiafy74jm3uk2vupq2ekn7y7eqk4jc7n24lwxnwxs3s6maw6nk2qd.onion"
                response = self.tor_session.get(test_url, timeout=30)
                
                if response.status_code == 200:
                    self.add_to_results("Tor connection successful - able to access .onion sites")
                else:
                    self.add_to_results("Tor connection issues - unable to access .onion sites", error=True)
                    
            except Exception as e:
                self.add_to_results(f"Error checking Tor status: {str(e)}", error=True)
        
        threading.Thread(target=check, daemon=True).start()
    
    def perform_search(self):
        query = self.search_entry.get()
        if not query:
            self.add_to_results("Please enter a search query", error=True)
            return
            
        def search():
            try:
                if not self.tor_session:
                    self.add_to_results("Please connect to Tor first", error=True)
                    return
                    
                self.add_to_results(f"Searching for: {query}")
                
                # Try both Ahmia addresses (clearnet and .onion)
                urls = [
                    f"https://ahmia.fi/search?q={query}",
                    f"http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/search?q={query}"
                ]
                
                results = []
                success = False
                
                for url in urls:
                    try:
                        self.add_to_results(f"Trying {url}...")
                        response = self.tor_session.get(url, timeout=30)
                        self.add_to_results(f"Response status: {response.status_code}")
                        
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            
                            # Debug info
                            self.add_to_results(f"Page title: {soup.title.string if soup.title else 'No title'}")
                            
                            # Try different result selectors
                            search_results = (
                                soup.select('.result') or 
                                soup.select('.searchresults') or
                                soup.select('.search-result') or
                                soup.select('div[class*="result"]')
                            )
                            
                            self.add_to_results(f"Found {len(search_results)} potential results")
                            
                            for result in search_results:
                                try:
                                    # Try different ways to extract title
                                    title_elem = (
                                        result.select_one('h4') or
                                        result.select_one('h3') or
                                        result.select_one('.title') or
                                        result.select_one('a')
                                    )
                                    
                                    # Try different ways to extract URL
                                    url_elem = result.select_one('a')
                                    
                                    # Try different ways to extract description
                                    desc_elem = (
                                        result.select_one('.description') or
                                        result.select_one('.content') or
                                        result.select_one('p')
                                    )
                                    
                                    if title_elem and url_elem:
                                        title = title_elem.get_text(strip=True)
                                        url = url_elem.get('href', '')
                                        description = desc_elem.get_text(strip=True) if desc_elem else "No description available"
                                        
                                        if title and url:
                                            result_data = {
                                                "title": title,
                                                "url": url,
                                                "description": description
                                            }
                                            results.append(result_data)
                                            
                                except Exception as e:
                                    self.add_to_results(f"Error parsing result: {str(e)}", error=True)
                                    continue
                            
                            if results:
                                success = True
                                break
                            
                    except Exception as e:
                        self.add_to_results(f"Error with {url}: {str(e)}", error=True)
                        continue
                
                if success and results:
                    self.search_results.extend(results)
                    self.add_to_results(f"\nFound {len(results)} results:")
                    for result in results:
                        self.add_to_results(f"\n• {result['title']}")
                        self.add_to_results(f"  URL: {result['url']}")
                        self.add_to_results(f"  Description: {result['description']}\n")
                else:
                    self.add_to_results("No results found or unable to parse results. Try a different search term.", error=True)
                    
            except Exception as e:
                self.add_to_results(f"Error performing search: {str(e)}", error=True)
                self.add_to_results("Try connecting to Tor again if the connection failed.", error=True)
        
        threading.Thread(target=search, daemon=True).start()
    
    def configure_tor(self):
        def configure():
            try:
                self.add_to_results("Starting Tor connection...")
                self.tor_session = self.tor.start_tor()
                self.add_to_results("Tor connection established successfully")
                self.update_system_info()
                
            except Exception as e:
                self.add_to_results(f"Error configuring Tor: {str(e)}", error=True)
        
        threading.Thread(target=configure, daemon=True).start()
    
    def export_results(self):
        if not self.search_results:
            self.add_to_results("No results to export", error=True)
            return
            
        try:
            filename = f"darksheets_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(self.search_results, f, indent=2)
            self.add_to_results(f"Results exported to {filename}")
        except Exception as e:
            self.add_to_results(f"Error exporting results: {str(e)}", error=True)
    
    def clear_results(self):
        self.results_text.delete("0.0", "end")
        self.search_results = []
        self.add_to_results("Results cleared")
    
    def add_to_results(self, message, error=False):
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = "ERROR" if error else "INFO"
        formatted_message = f"[{timestamp}] {prefix}: {message}\n"
        
        self.results_text.insert("end", formatted_message)
        self.results_text.see("end")
        
        # Color error messages in red
        if error:
            end_index = self.results_text.index("end-1c")
            start_index = f"{float(end_index) - len(formatted_message)}"
            self.results_text.tag_add("error", start_index, end_index)
            self.results_text.tag_config("error", foreground="red")
    
    def run(self):
        self.update_system_info()
        try:
            self.root.mainloop()
        finally:
            # Cleanup Tor process when application closes
            if self.tor:
                self.tor.stop_tor()

def main():
    app = DarkSheetsApp()
    app.run()

if __name__ == "__main__":
    main()
