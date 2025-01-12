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

# Configure logging
log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'darksheets.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file, encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class Console:
    def print(self, message):
        print(message)

class DarkSheets:
    def __init__(self):
        """Initialize DarkSheets with Tor connection"""
        self.console = Console()
        self.session = requests.Session()
        
        # Configure Tor SOCKS proxy
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
        socket.socket = socks.socksocket
        
        self.session.proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
        
        # Request timeout in seconds
        self.timeout = 30
        
        # Find Tor Browser path
        self.tor_browser_path = self.find_tor_browser()
        if not self.tor_browser_path:
            logger.warning("Tor Browser not found. Some features may not work.")
    
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

    def _is_tor_running(self):
        """Check if Tor is running by attempting to connect to the SOCKS proxy"""
        try:
            # Try to connect to the SOCKS proxy
            sock = socks.socksocket()
            sock.set_proxy(socks.SOCKS5, "127.0.0.1", 9050)
            sock.settimeout(5)
            sock.connect(("check.torproject.org", 443))
            sock.close()
            return True
        except Exception as e:
            logger.error(f"Tor connection check failed: {str(e)}")
            return False
    
    def ensure_tor_connection(self):
        """Ensure Tor connection is active"""
        if not self._is_tor_running():
            # Try to start Tor Browser in background mode
            if self.tor_browser_path:
                try:
                    logger.info("Attempting to start Tor Browser in background mode...")
                    tor_dir = os.path.dirname(os.path.dirname(self.tor_browser_path))
                    subprocess.Popen([
                        self.tor_browser_path,
                        "--headless"
                    ], cwd=tor_dir)
                    
                    # Wait for Tor to start
                    for _ in range(30):  # Wait up to 30 seconds
                        time.sleep(1)
                        if self._is_tor_running():
                            logger.info("Tor connection established!")
                            return True
                    
                    logger.error("Timeout waiting for Tor to start")
                    return False
                except Exception as e:
                    logger.error(f"Failed to start Tor Browser: {str(e)}")
                    return False
            else:
                logger.error("Tor Browser not found and Tor is not running")
                return False
        return True
    
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
        logger.info(f"Starting search for: {query}")
        logger.info(f"Enabled engines: {engines}")
        
        # Mock results for each engine
        if not engines or engines.get('duckduckgo', True):
            results.append({
                'title': 'DuckDuckGo Search Result',
                'url': 'http://example.onion/result1',
                'description': f'Sample result for query: {query}',
                'source': 'DuckDuckGo'
            })
            
        if not engines or engines.get('ahmia', True):
            results.append({
                'title': 'Ahmia Search Result',
                'url': 'http://example.onion/result2',
                'description': f'Sample result for query: {query}',
                'source': 'Ahmia'
            })
            
        if not engines or engines.get('torch', True):
            results.append({
                'title': 'Torch Search Result',
                'url': 'http://example.onion/result3',
                'description': f'Sample result for query: {query}',
                'source': 'Torch'
            })
            
        if not engines or engines.get('kilos', True):
            results.append({
                'title': 'Kilos Search Result',
                'url': 'http://example.onion/result4',
                'description': f'Sample result for query: {query}',
                'source': 'Kilos'
            })
            
        if not engines or engines.get('recon', True):
            results.append({
                'title': 'Recon Search Result',
                'url': 'http://example.onion/result5',
                'description': f'Sample result for query: {query}',
                'source': 'Recon'
            })
        
        return results
    
    def connect_tor(self):
        """Connect to the Tor network"""
        try:
            if self.ensure_tor_connection():
                # Test connection through Tor
                response = self.session.get('https://check.torproject.org', timeout=self.timeout)
                if 'Congratulations' in response.text:
                    logger.info("Successfully connected to Tor!")
                    return True
                else:
                    logger.error("Connected to network but not through Tor")
                    return False
            return False
        except Exception as e:
            logger.error(f"Error connecting to Tor: {str(e)}")
            return False
    
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
