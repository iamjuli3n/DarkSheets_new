#!/usr/bin/env python3
"""
DarkSheets Core Functionality
"""
import os
import sys
import requests
import time
import subprocess
import psutil
from rich.console import Console
from rich.progress import Progress
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
import socks
import socket

class DarkSheets:
    def __init__(self):
        """Initialize DarkSheets with console for rich output"""
        self.console = Console()
        self.tor_process = None
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
        panel = Panel(banner, title="[bold blue]DarkSheets[/bold blue]", 
                     subtitle="[bold red]Dark Web Research Tool[/bold red]")
        self.console.print(panel)
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
        """Connect to Tor network"""
        # Instead of starting Tor ourselves, we'll check if it's already running
        # This assumes Tor Browser is running, which handles Tor process
        try:
            if self._is_tor_running():
                self.console.print("[green]Successfully connected to Tor![/green]")
                return True
            else:
                self.console.print("[yellow]Please start Tor Browser to use DarkSheets[/yellow]")
                return False
        except Exception as e:
            self.console.print(f"[red]Error connecting to Tor: {e}[/red]")
            return False

    def disconnect_tor(self):
        """Disconnect from Tor network"""
        # We don't need to disconnect since we're not managing the Tor process
        return True

    def search_dark_web(self, query, engines=None):
        """
        Search the dark web using specified search engines
        Returns list of results with title and URL
        """
        if not engines:
            engines = ["ahmia", "torch", "haystak"]

        results = []
        
        with Progress() as progress:
            search_task = progress.add_task("[cyan]Searching...", total=len(engines))
            
            for engine in engines:
                if engine == "ahmia":
                    try:
                        url = f"https://ahmia.fi/search/?q={query}"
                        response = requests.get(url)
                        if response.status_code == 200:
                            # Extract results (simplified for example)
                            results.append({
                                "engine": "Ahmia",
                                "title": "Sample Result",
                                "url": "http://example.onion"
                            })
                    except Exception as e:
                        self.console.print(f"[red]Error searching Ahmia: {e}[/red]")
                
                elif engine == "torch":
                    try:
                        # Torch search implementation
                        results.append({
                            "engine": "Torch",
                            "title": "Sample Result",
                            "url": "http://example.onion"
                        })
                    except Exception as e:
                        self.console.print(f"[red]Error searching Torch: {e}[/red]")
                
                elif engine == "haystak":
                    try:
                        # Haystak search implementation
                        results.append({
                            "engine": "Haystak",
                            "title": "Sample Result",
                            "url": "http://example.onion"
                        })
                    except Exception as e:
                        self.console.print(f"[red]Error searching Haystak: {e}[/red]")
                
                progress.update(search_task, advance=1)
        
        return results

    def run_cli(self):
        """Run the CLI interface"""
        self.display_banner()
        
        if not self.connect_tor():
            self.console.print("[red]Failed to connect to Tor. Exiting...[/red]")
            sys.exit(1)
        
        while True:
            command = Prompt.ask(
                "[bold blue]DarkSheets[/bold blue]",
                choices=["search", "status", "clear", "exit"]
            )
            
            if command == "search":
                query = Prompt.ask("[yellow]Enter search query[/yellow]")
                results = self.search_dark_web(query)
                
                for result in results:
                    self.console.print(Panel(
                        f"[cyan]Engine:[/cyan] {result['engine']}\n"
                        f"[cyan]Title:[/cyan] {result['title']}\n"
                        f"[cyan]URL:[/cyan] {result['url']}",
                        title="[green]Search Result[/green]"
                    ))
            
            elif command == "status":
                self.console.print(Panel(
                    f"[cyan]Local IP:[/cyan] {self._get_local_ip()}\n"
                    f"[cyan]External IP:[/cyan] {self._get_external_ip()}\n"
                    f"[cyan]City:[/cyan] {self._get_city()}\n"
                    f"[cyan]Tor Status:[/cyan] {'Connected' if self._is_tor_running() else 'Disconnected'}",
                    title="[green]System Status[/green]"
                ))
            
            elif command == "clear":
                os.system('cls' if os.name == 'nt' else 'clear')
                self.display_banner()
            
            elif command == "exit":
                if Confirm.ask("[yellow]Are you sure you want to exit?[/yellow]"):
                    self.disconnect_tor()
                    self.console.print("[green]Goodbye![/green]")
                    sys.exit(0)

if __name__ == "__main__":
    darksheets = DarkSheets()
    darksheets.run_cli()
