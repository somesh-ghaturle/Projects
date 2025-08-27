#!/usr/bin/env python3
"""
Web UI Server for Agentic Finance Workflow
Serves the HTML interface for interacting with the finance API
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

# Configuration
PORT = 3001
INTERFACE_FILE = "finance_web_interface.html"

class FinanceUIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def start_finance_ui():
    """Start the finance web interface server"""
    
    # Check if interface file exists
    if not Path(INTERFACE_FILE).exists():
        print(f"❌ Error: {INTERFACE_FILE} not found!")
        print(f"📁 Current directory: {os.getcwd()}")
        print(f"📋 Available files: {list(Path('.').glob('*.html'))}")
        return False
    
    try:
        with socketserver.TCPServer(("", PORT), FinanceUIHandler) as httpd:
            print(f"🏦 Starting Agentic Finance Workflow UI on http://localhost:{PORT}")
            print(f"📁 Serving files from: {os.getcwd()}")
            print(f"🚀 Opening Finance Analytics Interface...")
            print()
            print(f"💡 Make sure your Docker API is running on http://localhost:8001")
            print(f"   To start it: docker-compose -f docker-compose.simple.yml up -d")
            print()
            print(f"🔗 Direct link: http://localhost:{PORT}/{INTERFACE_FILE}")
            print()
            print("Press Ctrl+C to stop the server")
            
            # Try to open browser
            try:
                webbrowser.open(f"http://localhost:{PORT}/{INTERFACE_FILE}")
            except Exception as e:
                print(f"⚠️  Could not open browser automatically: {e}")
                print(f"   Please manually open: http://localhost:{PORT}/{INTERFACE_FILE}")
            
            # Start serving
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        return True
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {PORT} is already in use!")
            print(f"   Try: lsof -ti:{PORT} | xargs kill -9")
            print(f"   Or use a different port")
        else:
            print(f"❌ Error starting server: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    start_finance_ui()
