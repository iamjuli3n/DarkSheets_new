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
import time
from bs4 import BeautifulSoup
import logging
import subprocess

class Console:
    def print(self, message):
        print(message)

class DarkSheets:
    def __init__(self):
        """Initialize DarkSheets with Tor connection"""
        self.console = Console()
        self.session = requests.Session()
        self.session.proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
        
        # Find Tor Browser path
        self.tor_browser_path = self.find_tor_browser()
        if not self.tor_browser_path:
            self.console.print("[red]Warning: Tor Browser not found. Some features may not work.[/red]")
    
    def find_tor_browser(self):
        """Find Tor Browser installation"""
        possible_paths = [
            os.path.expanduser("~\\Desktop\\Tor Browser\\Browser\\firefox.exe"),
            os.path.expanduser("~\\Downloads\\Tor Browser\\Browser\\firefox.exe"),
            "C:\\Program Files\\Tor Browser\\Browser\\firefox.exe",
            "C:\\Program Files (x86)\\Tor Browser\\Browser\\firefox.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def open_in_tor_browser(self, url):
        """Open URL in Tor Browser"""
        if self.tor_browser_path:
            try:
                subprocess.Popen([self.tor_browser_path, url])
                return True
            except Exception as e:
                self.console.print(f"[red]Error opening Tor Browser: {str(e)}[/red]")
                return False
        else:
            self.console.print("[red]Tor Browser not found[/red]")
            return False
    
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

    def check_connection(self):
        """Check Tor connection and get connection details"""
        try:
            # Test connection and measure latency
            start_time = time.time()
            response = requests.get('https://check.torproject.org', proxies=self.session.proxies, timeout=30)
            end_time = time.time()
            latency = round((end_time - start_time) * 1000, 2)  # Convert to ms
            
            if 'Congratulations' in response.text:
                # Get Tor exit node IP
                exit_ip_response = requests.get('https://api.ipify.org?format=json', proxies=self.session.proxies)
                exit_ip = exit_ip_response.json()['ip']
                
                # Get geolocation data
                geo_response = requests.get(f'https://ipapi.co/{exit_ip}/json/')
                geo_data = geo_response.json()
                
                # Get weather data using OpenWeatherMap API
                try:
                    lat = geo_data.get('latitude')
                    lon = geo_data.get('longitude')
                    weather_response = requests.get(
                        f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid=0b79d72688389c43f25475ea0548518e&units=metric'
                    )
                    weather_data = weather_response.json()
                    weather = {
                        'temp': round(weather_data['main']['temp']),
                        'feels_like': round(weather_data['main']['feels_like']),
                        'description': weather_data['weather'][0]['description'],
                        'humidity': weather_data['main']['humidity'],
                        'wind_speed': round(weather_data['wind']['speed']),
                        'clouds': weather_data['clouds']['all']
                    }
                    self.console.print(f"\n[cyan]Weather at exit node location:[/cyan]")
                    self.console.print(f"[cyan]Temperature: {weather['temp']}°C (feels like {weather['feels_like']}°C)[/cyan]")
                    self.console.print(f"[cyan]Conditions: {weather['description'].title()}[/cyan]")
                    self.console.print(f"[cyan]Humidity: {weather['humidity']}%[/cyan]")
                    self.console.print(f"[cyan]Wind Speed: {weather['wind_speed']} m/s[/cyan]")
                    self.console.print(f"[cyan]Cloud Cover: {weather['clouds']}%[/cyan]")
                except Exception as e:
                    self.console.print(f"[yellow]Could not fetch weather data: {str(e)}[/yellow]")
                    weather = None
                
                self.connection_info = {
                    'status': 'connected',
                    'ip': exit_ip,
                    'country': geo_data.get('country_name'),
                    'city': geo_data.get('city'),
                    'region': geo_data.get('region'),
                    'postal': geo_data.get('postal'),
                    'latitude': geo_data.get('latitude'),
                    'longitude': geo_data.get('longitude'),
                    'latency': latency,
                    'exit_node': exit_ip,
                    'weather': weather,
                    'circuit': self.get_circuit_info()
                }
                return True, self.connection_info
            return False, "Not connected to Tor"
        except Exception as e:
            return False, str(e)

    def get_circuit_info(self):
        """Get Tor circuit information"""
        try:
            with stem.control.Controller.from_port(port=9051) as controller:
                controller.authenticate()
                circuit_info = []
                for circ in controller.get_circuits():
                    if circ.status == stem.CircuitStatus.BUILT:
                        path = []
                        for i, entry in enumerate(circ.path):
                            try:
                                finger = entry[0]
                                router = controller.get_network_status(finger)
                                if router:
                                    path.append({
                                        'nickname': router.nickname,
                                        'country': router.country,
                                        'flags': list(router.flags),
                                        'ip': router.address
                                    })
                            except Exception:
                                continue
                        circuit_info.append(path)
                return circuit_info
        except Exception as e:
            return []

    def connect_tor(self):
        """Connect to the Tor network"""
        try:
            # Test connection
            success, info = self.check_connection()
            if success:
                self.console.print("[green]Successfully connected to Tor![/green]")
                self.console.print(f"[blue]Exit Node:[/blue] {info['ip']}")
                self.console.print(f"[blue]Location:[/blue] {info['city']}, {info['country']}")
                self.console.print(f"[blue]Region:[/blue] {info['region']}")
                self.console.print(f"[blue]Postal:[/blue] {info['postal']}")
                self.console.print(f"[blue]Latitude:[/blue] {info['latitude']}")
                self.console.print(f"[blue]Longitude:[/blue] {info['longitude']}")
                self.console.print(f"[blue]Latency:[/blue] {info['latency']}ms")
                if info['weather']:
                    self.console.print(f"[blue]Weather:[/blue] {info['weather']['temp']}°C, {info['weather']['description']}")
                    self.console.print(f"[blue]Humidity:[/blue] {info['weather']['humidity']}%")
                if info['circuit']:
                    self.console.print("\n[blue]Circuit Information:[/blue]")
                    for i, path in enumerate(info['circuit'], 1):
                        self.console.print(f"\nCircuit {i}:")
                        for node in path:
                            self.console.print(f"  → {node['nickname']} ({node['country']}) - {node['ip']}")
                return True
            else:
                self.console.print("[red]Failed to connect to Tor.[/red]")
                return False
        except Exception as e:
            self.console.print(f"[red]Error connecting to Tor: {str(e)}[/red]")
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

    def search_dark_web(self, query, engines=None):
        """
        Search the dark web using multiple search engines
        
        Args:
            query (str): Search query
            engines (dict): Dictionary of enabled search engines {name: bool}
        """
        results = []
        errors = []
        
        # Debug logging
        self.console.print(f"\n[yellow]Starting search for: {query}[/yellow]")
        self.console.print(f"[yellow]Enabled engines: {engines}[/yellow]")
        
        # Check if Tor Browser is available
        if not self.tor_browser_path:
            self.console.print("[red]Warning: Tor Browser not found. Search results may be limited.[/red]")
        
        try:
            # DuckDuckGo Onion search
            if not engines or engines.get('duckduckgo', True):
                self.console.print("\n[blue]Searching DuckDuckGo...[/blue]")
                ddg_url = f'http://duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion/lite/?q={query}'
                
                try:
                    response = self.session.get(ddg_url, timeout=30, verify=False)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        for result in soup.find_all(['div', 'tr'], class_=['result-default', 'result']):
                            try:
                                link = result.find('a')
                                if not link:
                                    continue
                                    
                                url = link.get('href', '')
                                title = link.text.strip()
                                desc = result.find_next_sibling('tr')
                                description = desc.text.strip() if desc else "No description available"
                                
                                if '.onion' in url:
                                    results.append({
                                        'title': title,
                                        'url': url,
                                        'description': description,
                                        'source': 'DuckDuckGo'
                                    })
                            except Exception as e:
                                self.console.print(f"[yellow]Error parsing DuckDuckGo result: {str(e)}[/yellow]")
                                
                        # Open in Tor Browser as well
                        self.open_in_tor_browser(ddg_url)
                except Exception as e:
                    self.console.print(f"[red]DuckDuckGo error: {str(e)}[/red]")
                    # Fallback to Tor Browser
                    self.open_in_tor_browser(ddg_url)
            
            # Ahmia search
            if not engines or engines.get('ahmia', True):
                self.console.print("\n[blue]Searching Ahmia...[/blue]")
                ahmia_url = f'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/search/?q={query}'
                
                try:
                    response = self.session.get(ahmia_url, timeout=30, verify=False)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        for result in soup.find_all(['div', 'li'], class_=['result', 'ahmia-result']):
                            try:
                                title = result.find(['h4', 'h3']).text.strip()
                                url = result.find('cite').text.strip() if result.find('cite') else result.find('a')['href']
                                description = result.find('p').text.strip()
                                
                                if '.onion' in url:
                                    results.append({
                                        'title': title,
                                        'url': url,
                                        'description': description,
                                        'source': 'Ahmia'
                                    })
                            except Exception as e:
                                self.console.print(f"[yellow]Error parsing Ahmia result: {str(e)}[/yellow]")
                                
                        # Open in Tor Browser as well
                        self.open_in_tor_browser(ahmia_url)
                except Exception as e:
                    self.console.print(f"[red]Ahmia error: {str(e)}[/red]")
                    # Fallback to Tor Browser
                    self.open_in_tor_browser(ahmia_url)
            
            # NotEvil search
            if not engines or engines.get('notevil', True):
                self.console.print("\n[blue]Searching NotEvil...[/blue]")
                notevil_url = f'http://notevilmtxf25uw7tskqxj6njlpebyrmlrerfv5hc4tuq7c7hilbyiqd.onion/index.php?q={query}'
                
                try:
                    response = self.session.get(notevil_url, timeout=30, verify=False)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        for result in soup.find_all('div', class_='search-result'):
                            try:
                                title = result.find('h5').text.strip()
                                url = result.find('a')['href']
                                description = result.find('p').text.strip()
                                
                                if '.onion' in url:
                                    results.append({
                                        'title': title,
                                        'url': url,
                                        'description': description,
                                        'source': 'NotEvil'
                                    })
                            except Exception as e:
                                self.console.print(f"[yellow]Error parsing NotEvil result: {str(e)}[/yellow]")
                                
                        # Open in Tor Browser as well
                        self.open_in_tor_browser(notevil_url)
                except Exception as e:
                    self.console.print(f"[red]NotEvil error: {str(e)}[/red]")
                    # Fallback to Tor Browser
                    self.open_in_tor_browser(notevil_url)
            
            # Torch search
            if not engines or engines.get('torch', True):
                self.console.print("\n[blue]Searching Torch...[/blue]")
                torch_url = f'http://torchqsxkllrj2eqaitp5xvcgfeg3g5dr3hr2wnuvnj76bbxkxfiwxqd.onion/search?query={query}'
                
                try:
                    response = self.session.get(torch_url, timeout=30, verify=False)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        for result in soup.find_all(['div', 'li'], class_=['result', 'search-result']):
                            try:
                                title = result.find(['h3', 'h4']).text.strip()
                                url = result.find('a')['href']
                                description = result.find('p').text.strip()
                                
                                if '.onion' in url:
                                    results.append({
                                        'title': title,
                                        'url': url,
                                        'description': description,
                                        'source': 'Torch'
                                    })
                            except Exception as e:
                                self.console.print(f"[yellow]Error parsing Torch result: {str(e)}[/yellow]")
                                
                        # Open in Tor Browser as well
                        self.open_in_tor_browser(torch_url)
                except Exception as e:
                    self.console.print(f"[red]Torch error: {str(e)}[/red]")
                    # Fallback to Tor Browser
                    self.open_in_tor_browser(torch_url)
            
            # Filter out duplicate URLs
            seen_urls = set()
            filtered_results = []
            for result in results:
                url = result['url']
                if url not in seen_urls and '.onion' in url:
                    seen_urls.add(url)
                    filtered_results.append(result)
            
            self.console.print(f"\n[green]Total results found: {len(filtered_results)}[/green]")
            return filtered_results
            
        except Exception as e:
            error_msg = f"Search error: {str(e)}"
            errors.append(error_msg)
            self.console.print(f"[red]{error_msg}[/red]")
            return []
    
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
