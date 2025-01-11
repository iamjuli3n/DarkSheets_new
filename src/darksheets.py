#!/usr/bin/env python3
"""
DarkSheets - Dark Web Research Tool
A tool for security research on the Dark Web with enhanced safety features
and user-friendly interface.
"""

import os
import sys
import time
import json
import subprocess
import requests
import socket
import psutil
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.prompt import Prompt, Confirm
from rich import print as rprint

class DarkSheets:
    def __init__(self):
        self.console = Console()
        self.kali_ip = self._get_local_ip()
        self.ext_ip = self._get_external_ip()
        self.city = self._get_city()
        self.work_dir = os.getcwd()
        self.tor_process = None

    def _get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            self.console.print(f"[red]Error getting local IP: {e}[/red]")
            return "Unknown"

    def _get_external_ip(self):
        """Get external IP address"""
        try:
            response = requests.get("https://api.ipify.org?format=json")
            return response.json()["ip"]
        except Exception as e:
            self.console.print(f"[red]Error getting external IP: {e}[/red]")
            return "Unknown"

    def _get_city(self):
        """Get city from IP"""
        try:
            response = requests.get(f"https://ipapi.co/{self.ext_ip}/city/")
            return response.text
        except Exception as e:
            self.console.print(f"[red]Error getting city: {e}[/red]")
            return "Unknown"

    def display_banner(self):
        """Display the DarkSheets banner"""
        banner = """
██████╗  █████╗ ██████╗ ██╗  ██╗███████╗██╗  ██╗███████╗███████╗████████╗███████╗
██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝██╔════╝██║  ██║██╔════╝██╔════╝╚══██╔══╝██╔════╝
██║  ██║███████║██████╔╝█████╔╝ ███████╗███████║█████╗  █████╗     ██║   ███████╗
██║  ██║██╔══██║██╔══██╗██╔═██╗ ╚════██║██╔══██║██╔══╝  ██╔══╝     ██║   ╚════██║
██████╔╝██║  ██║██║  ██║██║  ██╗███████║██║  ██║███████╗███████╗   ██║   ███████║
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝   ╚══════╝
        """
        panel = Panel(banner, title="[bold blue]DarkSheets[/bold blue]", subtitle="[bold red]Dark Web Research Tool[/bold red]")
        self.console.print(panel)
        self.console.print(f"[bold green]Local IP:[/bold green] {self.kali_ip}")
        self.console.print(f"[bold green]External IP:[/bold green] {self.ext_ip}")
        self.console.print(f"[bold green]City:[/bold green] {self.city}")
        self.console.print(f"[bold green]Working Directory:[/bold green] {self.work_dir}\n")

    def _is_tor_running(self):
        """Check if Tor is running"""
        for proc in psutil.process_iter(['name']):
            if 'tor' in proc.info['name'].lower():
                return True
        return False

    def setup_tor(self):
        """Install and configure Tor if not already installed"""
        if not self._is_tor_running():
            self.console.print("[yellow]Setting up Tor...[/yellow]")
            try:
                subprocess.run(['tor'], check=True)
                self.console.print("[green]Tor setup complete![/green]")
            except subprocess.CalledProcessError:
                self.console.print("[red]Error setting up Tor[/red]")
                sys.exit(1)

    def check_tor(self):
        """Check Tor connectivity"""
        try:
            response = requests.get('https://check.torproject.org/api/ip')
            data = response.json()
            if data['IsTor']:
                self.console.print("[green]Successfully connected to Tor![/green]")
                return True
            else:
                self.console.print("[red]Not connected to Tor![/red]")
                return False
        except Exception as e:
            self.console.print(f"[red]Error checking Tor connection: {e}[/red]")
            return False

    def connect_tor(self):
        """Connect to Tor network"""
        if not self._is_tor_running():
            try:
                self.tor_process = subprocess.Popen(['tor'])
                time.sleep(5)  # Wait for Tor to establish connection
                if self.check_tor():
                    return True
            except Exception as e:
                self.console.print(f"[red]Error connecting to Tor: {e}[/red]")
                return False
        return True

    def disconnect_tor(self):
        """Disconnect from Tor network"""
        if self.tor_process:
            try:
                self.tor_process.terminate()
                self.tor_process = None
                self.console.print("[green]Disconnected from Tor[/green]")
                return True
            except Exception as e:
                self.console.print(f"[red]Error disconnecting from Tor: {e}[/red]")
                return False
        return True

    def search_dark_web(self, query, engines=None):
        """Perform dark web search"""
        if engines is None:
            engines = ['ahmia', 'torch', 'haystak']
        
        results = []
        
        with Progress() as progress:
            search_task = progress.add_task("[cyan]Searching Dark Web...", total=len(engines))
            
            if 'ahmia' in engines:
                try:
                    response = requests.get(f'https://ahmia.fi/search/?q={query}')
                    # Parse results here
                    results.append({"engine": "Ahmia", "url": response.url, "title": f"Results for {query}"})
                except Exception as e:
                    self.console.print(f"[red]Error searching Ahmia: {e}[/red]")
                progress.update(search_task, advance=1)
            
            if 'torch' in engines:
                try:
                    response = requests.get(f'http://xmh57jrzrnw6insl.onion/4a1f6b371c/search.cgi?q={query}')
                    # Parse results here
                    results.append({"engine": "Torch", "url": response.url, "title": f"Results for {query}"})
                except Exception as e:
                    self.console.print(f"[red]Error searching Torch: {e}[/red]")
                progress.update(search_task, advance=1)
            
            if 'haystak' in engines:
                try:
                    response = requests.get(f'http://haystakvxad7wbk5.onion/?q={query}')
                    # Parse results here
                    results.append({"engine": "Haystak", "url": response.url, "title": f"Results for {query}"})
                except Exception as e:
                    self.console.print(f"[red]Error searching Haystak: {e}[/red]")
                progress.update(search_task, advance=1)

        return results

    def run(self):
        """Main execution flow"""
        self.display_banner()
        
        if not self.connect_tor():
            self.console.print("[red]Failed to connect to Tor. Exiting...[/red]")
            sys.exit(1)
        
        while True:
            command = Prompt.ask("\n[bold blue]DarkSheets[/bold blue]", choices=["search", "status", "exit"])
            
            if command == "search":
                query = Prompt.ask("[yellow]Enter search query[/yellow]")
                results = self.search_dark_web(query)
                
                for result in results:
                    self.console.print(Panel(
                        f"[cyan]Engine:[/cyan] {result['engine']}\n"
                        f"[cyan]URL:[/cyan] {result['url']}\n"
                        f"[cyan]Title:[/cyan] {result['title']}",
                        title=f"[green]Search Result[/green]"
                    ))
            
            elif command == "status":
                self.console.print(Panel(
                    f"[cyan]Local IP:[/cyan] {self.kali_ip}\n"
                    f"[cyan]External IP:[/cyan] {self.ext_ip}\n"
                    f"[cyan]City:[/cyan] {self.city}\n"
                    f"[cyan]Tor Status:[/cyan] {'Connected' if self._is_tor_running() else 'Disconnected'}",
                    title="[green]System Status[/green]"
                ))
            
            elif command == "exit":
                if Confirm.ask("[yellow]Are you sure you want to exit?[/yellow]"):
                    self.disconnect_tor()
                    self.console.print("[green]Goodbye![/green]")
                    break

if __name__ == "__main__":
    try:
        darksheets = DarkSheets()
        darksheets.run()
    except KeyboardInterrupt:
        print("\nExiting...")
        if hasattr(darksheets, 'disconnect_tor'):
            darksheets.disconnect_tor()
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
