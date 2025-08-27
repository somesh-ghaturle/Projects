#!/usr/bin/env python3
"""
Simple HTTP server to serve the web interface for Multi-Agent Content Analytics
This avoids CORS issues when accessing the API from the web interface.
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

# Configuration
PORT = 3000
DIRECTORY = Path(__file__).parent

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add CORS headers to allow API access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    """Start the web server and open the interface"""
    
    # Check if the web interface file exists
    web_interface = DIRECTORY / "web_interface.html"
    if not web_interface.exists():
        print("❌ Error: web_interface.html not found in current directory")
        print(f"   Looking in: {DIRECTORY}")
        return
    
    # Start the server
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"🌐 Starting web server on http://localhost:{PORT}")
        print(f"📁 Serving files from: {DIRECTORY}")
        print(f"🚀 Opening Multi-Agent Content Analytics Interface...")
        print(f"")
        print(f"💡 Make sure your Docker API is running on http://localhost:8000")
        print(f"   To start it: docker-compose up -d")
        print(f"")
        print(f"🔗 Direct link: http://localhost:{PORT}/web_interface.html")
        print(f"")
        print("Press Ctrl+C to stop the server")
        
        # Open web browser
        try:
            webbrowser.open(f"http://localhost:{PORT}/web_interface.html")
        except Exception as e:
            print(f"Could not auto-open browser: {e}")
            print(f"Please manually open: http://localhost:{PORT}/web_interface.html")
        
        # Start serving
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n🛑 Server stopped")

if __name__ == "__main__":
    main()
