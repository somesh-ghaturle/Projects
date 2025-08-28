#!/usr/bin/env python3
"""
Simple HTTP server that directly serves index.html
"""
import http.server
import socketserver
import webbrowser
import os

# Configuration
PORT = 7000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def do_GET(self):
        # Serve index.html for root requests
        if self.path == '/':
            self.path = '/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

# Start the server
with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    print(f"🌐 Starting web server on http://localhost:{PORT}")
    print(f"📁 Serving files from: {DIRECTORY}")
    print(f"🚀 Opening Multi-Agent Content Analytics Interface...")
    print(f"")
    print(f"💡 Direct link: http://localhost:{PORT}/index.html")
    print(f"")
    print("Press Ctrl+C to stop the server")
    
    try:
        webbrowser.open(f"http://localhost:{PORT}/index.html")
    except:
        pass
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
