#!/usr/bin/env python3
"""
DarkSheets Core Functionality
"""
import requests
import stem
import stem.process
import stem.control
import socket
import socks
import os
import sys
from bs4 import BeautifulSoup
import logging

class Console:
    def print(self, message):
        print(message)

class DarkSheets:
    def __init__(self):
        """Initialize DarkSheets with console for rich output"""
        self.console = Console()
        self.tor_process = None
        self.tor_controller = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.ext_ip = None

    def _get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def _get_external_ip(self):
        """Get external IP address"""
        try:
            response = requests.get('https://api.ipify.org?format=json')
            self.ext_ip = response.json()['ip']
            return self.ext_ip
        except:
            return "Unknown"

    def _get_city(self):
        """Get city based on IP"""
        try:
            response = requests.get('https://ipapi.co/json/')
            return response.json()['city']
        except:
            return "Unknown"

    def display_banner(self):
        """Display DarkSheets banner"""
        banner = """
██████╗  █████╗ ██████╗ ██╗  ██╗███████╗██╗  ██╗███████╗███████╗████████╗███████╗
██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝██╔════╝██║  ██║██╔════╝██╔════╝╚══██╔══╝██╔════╝
██║  ██║███████║██████╔╝█████╔╝ ███████╗███████║█████╗  █████╗     ██║   ███████╗
██║  ██║██╔══██║██╔══██╗██╔═██╗ ╚════██║██╔══██║██╔══╝  ██╔══╝     ██║   ╚════██║
██████╔╝██║  ██║██║  ██║██║  ██╗███████║██║  ██║███████╗███████╗   ██║   ███████║
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝   ╚══════╝
        """
        self.console.print(banner)
        self.console.print(f"[bold green]Local IP:[/bold green] {self._get_local_ip()}")
        self.console.print(f"[bold green]External IP:[/bold green] {self._get_external_ip()}")
        self.console.print(f"[bold green]City:[/bold green] {self._get_city()}")
        self.console.print(f"[bold green]Working Directory:[/bold green] {os.getcwd()}\n")

    def _is_tor_running(self):
        """Check if Tor is running"""
        try:
            sock = socks.socksocket()
            sock.settimeout(6)
            sock.connect(('127.0.0.1', 9050))
            return True
        except:
            return False
        finally:
            if 'sock' in locals():
                sock.close()

    def connect_tor(self):
        """Connect to the Tor network"""
        try:
            # Configure SOCKS proxy
            socks.set_default_proxy(socks.SOCKS5, "localhost", 9050)
            socket.socket = socks.socksocket
            
            # Test connection
            response = requests.get('https://check.torproject.org')
            if 'Congratulations' in response.text:
                return True
            return False
        except Exception as e:
            self.console.print(f"Error connecting to Tor: {str(e)}")
            return False
            
    def disconnect_tor(self):
        """Disconnect from the Tor network"""
        try:
            if self.tor_process:
                self.tor_process.kill()
                self.tor_process = None
            if self.tor_controller:
                self.tor_controller.close()
                self.tor_controller = None
            return True
        except:
            return False
            
    def search_dark_web(self, query):
        """Search the dark web using multiple search engines"""
        results = []
        
        try:
            # Ahmia search
            ahmia_url = f'https://ahmia.fi/search/?q={query}'
            response = self.session.get(ahmia_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            for result in soup.find_all('li', class_='result'):
                title = result.find('h4').text.strip()
                url = result.find('a')['href']
                description = result.find('p').text.strip()
                results.append({
                    'title': title,
                    'url': url,
                    'description': description,
                    'source': 'Ahmia'
                })
                
            # Torch search
            torch_url = f'http://xmh57jrzrnw6insl.onion/4a1f6b371c/search.cgi?q={query}'
            response = self.session.get(torch_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            for result in soup.find_all('dl'):
                title = result.find('dt').text.strip()
                url = result.find('dd').text.strip()
                results.append({
                    'title': title,
                    'url': url,
                    'description': '',
                    'source': 'Torch'
                })
                
        except Exception as e:
            self.console.print(f"Search error: {str(e)}")
            
        return results

    def run_cli(self):
        """Run the CLI interface"""
        self.display_banner()
        
        if not self.connect_tor():
            self.console.print("[red]Failed to connect to Tor. Exiting...[/red]")
            sys.exit(1)
        
        while True:
            command = input("[bold blue]DarkSheets[/bold blue] ")
            
            if command == "search":
                query = input("[yellow]Enter search query[/yellow]")
                results = self.search_dark_web(query)
                
                for result in results:
                    self.console.print(f"[cyan]Source:[/cyan] {result['source']}\n"
                        f"[cyan]Title:[/cyan] {result['title']}\n"
                        f"[cyan]URL:[/cyan] {result['url']}\n"
                        f"[cyan]Description:[/cyan] {result['description']}")
            
            elif command == "status":
                self.console.print(f"[cyan]Local IP:[/cyan] {self._get_local_ip()}\n"
                    f"[cyan]External IP:[/cyan] {self._get_external_ip()}\n"
                    f"[cyan]City:[/cyan] {self._get_city()}\n"
                    f"[cyan]Tor Status:[/cyan] {'Connected' if self._is_tor_running() else 'Disconnected'}")
            
            elif command == "clear":
                os.system('cls' if os.name == 'nt' else 'clear')
                self.display_banner()
            
            elif command == "exit":
                if input("[yellow]Are you sure you want to exit?[/yellow]"):
                    self.disconnect_tor()
                    self.console.print("[green]Goodbye![/green]")
                    sys.exit(0)

if __name__ == "__main__":
    darksheets = DarkSheets()
    darksheets.run_cli()
