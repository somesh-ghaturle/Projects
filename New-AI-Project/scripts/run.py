#!/usr/bin/env python3
"""
Run script for the New AI Project
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_application():
    """Run the main application"""
    print("Starting New AI Project...")
    
    # Change to project directory
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    # Run the application
    result = subprocess.run([sys.executable, "src/main.py"])
    return result.returncode

def run_api_server(host="0.0.0.0", port=8000, reload=False):
    """Run the API server"""
    print(f"Starting API server on {host}:{port}...")
    
    # Change to project directory
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    # Build uvicorn command
    cmd = [
        sys.executable, "-m", "uvicorn",
        "src.api.main:app",
        "--host", host,
        "--port", str(port)
    ]
    
    if reload:
        cmd.append("--reload")
    
    result = subprocess.run(cmd)
    return result.returncode

def run_tests(coverage=False):
    """Run the test suite"""
    print("Running tests...")
    
    # Change to project directory
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html"])
    
    result = subprocess.run(cmd)
    return result.returncode

def main():
    """Main run function"""
    parser = argparse.ArgumentParser(description="Run New AI Project")
    parser.add_argument(
        "command",
        choices=["app", "api", "test"],
        help="Command to run: app (main application), api (API server), test (run tests)"
    )
    parser.add_argument("--host", default="0.0.0.0", help="API server host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="API server port (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for API server")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage report")
    
    args = parser.parse_args()
    
    try:
        if args.command == "app":
            return run_application()
        elif args.command == "api":
            return run_api_server(args.host, args.port, args.reload)
        elif args.command == "test":
            return run_tests(args.coverage)
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
