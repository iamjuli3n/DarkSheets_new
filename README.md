# DarkSheets - Dark Web Research Tool

A Python-based tool for security research on the Dark Web, featuring a user-friendly graphical interface.

## Prerequisites

1. **Python 3.8 or higher**
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Tor Browser**
   - Download from [torproject.org](https://www.torproject.org/download/)
   - Install and run before using DarkSheets

## Installation & Running

### Easy Method (Recommended)
1. Download DarkSheets
2. Start Tor Browser
3. Double-click `start_darksheets.bat`

### Manual Method
1. Open a terminal in the DarkSheets directory
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Start Tor Browser
4. Run the application:
   ```bash
   python run_darksheets.py
   ```

## Usage

1. Make sure Tor Browser is running
2. Launch DarkSheets using one of the methods above
3. The application will automatically connect through Tor
4. Enter your search query and select search engines
5. Click "Search" to begin
6. Results will appear in the main window
7. Click links to open them in Tor Browser
8. Right-click links to copy them

## Features

- Modern, eye-friendly interface
- Real-time connection monitoring
- Multiple dark web search engines
- Secure Tor integration
- Search history tracking
- System log with detailed information

## Troubleshooting

1. **"Python is not installed" error**
   - Install Python from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Connection errors**
   - Make sure Tor Browser is running
   - Click "Check Connection" in DarkSheets
   - Check the system log for detailed error information

3. **Missing dependencies**
   - Run `pip install -r requirements.txt`
   - If pip is not found, reinstall Python with PATH option checked

## Support

For issues and feature requests, please create an issue in the GitHub repository.
