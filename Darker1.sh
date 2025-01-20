#!/usr/bin/env bash

#######################################################
# Made for doing security research on the Dark Deep Web
# Intended to be used on Kali Linux
# eye -q "ransomeware" | grep .onion > results+onions.txt
# torghost -a -c us,mx,ca 
# libreoffice --calc results+onions.txt
# Tested on Kali 2024.3
# Last updated 09/21/2024, minor evil updates, pay me later
# https://github.com/aryanguenthner
# The future is now
# https://dark.fail/
# https://addons.mozilla.org/en-US/firefox/addon/noscript/
# https://addons.mozilla.org/en-US/firefox/addon/adblock-plus/
# https://chrome.google.com/webstore/detail/noscript/doojmbjmlfjjnbmnoijecmcbfeoakpjm/related?hl=en
# http://guideeedvgbpkthetphncab5aqj7dp5t74y7vxsoonnvmaeamq74vuqd.onion/
######################################################

echo
echo "
██████╗░░█████╗░██████╗░██╗░░██╗░██████╗██╗░░██╗███████╗███████╗████████╗░██████╗
██╔══██╗██╔══██╗██╔══██╗██║░██╔╝██╔════╝██║░░██║██╔════╝██╔════╝╚══██╔══╝██╔════╝
██║░░██║███████║██████╔╝█████═╝░╚█████╗░███████║█████╗░░█████╗░░░░░██║░░░╚█████╗░
██║░░██║██╔══██║██╔══██╗██╔═██╗░░╚═══██╗██╔══██║██╔══╝░░██╔══╝░░░░░██║░░░░╚═══██╗
██████╔╝██║░░██║██║░░██║██║░╚██╗██████╔╝██║░░██║███████╗███████╗░░░██║░░░██████╔╝
╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚═╝╚═════╝░╚═╝░░╚═╝╚══════╝╚══════╝░░░╚═╝░░░╚═════╝░"
echo "v1.1"
echo

# Setting Variables
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
NC='\033[0m' # No Color
KALI=$(hostname -I)
CITY=$(curl -s http://ip-api.com/line?fields=timezone | cut -d "/" -f 2)
EXT=$(curl -s api.ipify.org)
PWD=$(pwd)

echo -e "${YELLOW}[+] Current Working Directory:${NC} $PWD"
echo -e "${YELLOW}[+] Internal IP Address:${NC} $KALI"
echo -e "${YELLOW}[+] External IP Address:${NC} $EXT"
echo -e "${YELLOW}[+] Current City:${NC} $CITY"
echo

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

# Check for required packages
check_package() {
    if ! command -v "$1" &> /dev/null; then
        echo "Installing $1..."
        apt-get install -y "$1"
    fi
}

# Install required packages
required_packages=(
    "tor"
    "proxychains"
    "curl"
    "libreoffice"
)

for package in "${required_packages[@]}"; do
    check_package "$package"
done

# Configure Tor
echo "Configuring Tor..."
systemctl start tor
systemctl enable tor

# Check Tor status
tor_status=$(systemctl is-active tor)
if [ "$tor_status" = "active" ]; then
    echo -e "${BLUE}[+] Tor is running${NC}"
else
    echo "Error: Tor is not running"
    exit 1
fi

# Download and install browser addons
echo "Downloading and Installing Addons"
echo "Please manually install the following addons:"
echo "1. NoScript: https://addons.mozilla.org/en-US/firefox/addon/noscript/"
echo "2. AdBlock Plus: https://addons.mozilla.org/en-US/firefox/addon/adblock-plus/"

echo -e "${BLUE}[+] Setup complete${NC}"
