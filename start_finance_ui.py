#!/usr/bin/env python3
"""
    print(f"🔗 Direct link: http://localhost:{PORT}/web_interface.html")imple UI server for Finance Workflow
"""
import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 3001
DIRECTORY = "/Users/somesh/Library/CloudStorage/OneDrive-PaceUniversity/github/Projects/agentic-finance-workflow"

os.chdir(DIRECTORY)

class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

print(f"🏦 Starting Finance Workflow UI on http://localhost:{PORT}")
print(f"📁 Serving files from: {DIRECTORY}")
print("🚀 Opening Finance Analytics Interface...")

# Start server
with socketserver.TCPServer(("", PORT), HTTPRequestHandler) as httpd:
    print(f"\n💡 Make sure your Docker API is running on http://localhost:8001")
    print("   To start it: docker-compose up -d")
    print(f"\n🔗 Direct link: http://localhost:{PORT}/finance_web_interface.html")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        webbrowser.open(f"http://localhost:{PORT}/web_interface.html")
    except:
        pass
        
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
