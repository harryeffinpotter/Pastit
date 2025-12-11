#!/usr/bin/env python3
"""
Pasta - File uploader with Rich progress bar

Installation:
1. Try system packages first (cleanest):
   sudo pacman -S python-rich python-requests python-requests-toolbelt python-dotenv

2. If system packages aren't available, use pip with --break-system-packages:
   pip install --break-system-packages rich requests requests-toolbelt python-dotenv

Usage:
   ./pasta file.txt        # Upload file
   ./pasta file.txt 10     # Upload file with 10 view limit
   ./pasta -s file.txt     # Silent mode - output only the URL
"""

import os
import sys
import json
import requests
import argparse
from pathlib import Path

# Try importing required packages with helpful error messages
try:
    from rich.console import Console
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TransferSpeedColumn, FileSizeColumn
    from rich.text import Text
except ImportError:
    print("Error: Rich library not found. Please install with:")
    print("  sudo pacman -S python-rich  # OR")
    print("  pip install --break-system-packages rich")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("Error: python-dotenv not found. Please install with:")
    print("  sudo pacman -S python-dotenv  # OR") 
    print("  pip install --break-system-packages python-dotenv")
    sys.exit(1)

try:
    from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
except ImportError:
    print("Error: requests-toolbelt not found. Please install with:")
    print("  sudo pacman -S python-requests-toolbelt  # OR")
    print("  pip install --break-system-packages requests-toolbelt")
    sys.exit(1)

def load_config():
    """Load configuration from .env file"""
    env_path = Path("/etc/pastit/.env")
    if not env_path.exists():
        print(".env file not found! Edit /etc/pastit/.env.example and rename it to /etc/pastit/.env to configure.")
        sys.exit(1)
    
    load_dotenv(env_path)
    
    host = os.getenv("host")
    auth_token = os.getenv("authorization_token")
    
    if not host or not auth_token:
        print("Error: host or authorization_token not found in .env file")
        sys.exit(1)
    
    return host, auth_token

def upload_file(file_path, max_views=0, interactive=True):
    """Upload file with progress bar"""
    host, auth_token = load_config()
    url = f"{host}/api/upload"
    
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    
    file_size = file_path.stat().st_size
    
    # Headers
    headers = {
        "Authorization": auth_token,
        "x-zipline-format": "gfycat",
        "x-zipline-original-name": "true",
    }
    
    if max_views > 0:
        headers["x-zipline-max-views"] = str(max_views)
    
    console = Console()
    
    if interactive:
        # Show file info
        console.print(f"🍝 [bold green]Uploading file:[/bold green] {file_path.name}")
        if max_views > 0:
            console.print(f"📊 [bold blue]Max views:[/bold blue] {max_views}")
        
        # Human readable file size
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        elif file_size < 1024 * 1024 * 1024:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"
        else:
            size_str = f"{file_size / (1024 * 1024 * 1024):.1f} GB"
        
        console.print(f"📦 [bold cyan]File size:[/bold cyan] {size_str}")
        console.print()
        
        # Create progress bar
        progress = Progress(
            TextColumn("[bold blue]Uploading...", justify="right"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            FileSizeColumn(),
            "•",
            TransferSpeedColumn(),
            "•",
            TimeRemainingColumn(),
            console=console,
            transient=False
        )
        
        with progress:
            task = progress.add_task("upload", total=file_size)
            
            def upload_callback(monitor):
                progress.update(task, advance=monitor.bytes_read - progress.tasks[task].completed)
            
            with open(file_path, 'rb') as f:
                encoder = MultipartEncoder(
                    fields={'file': (file_path.name, f, 'application/octet-stream')}
                )
                monitor = MultipartEncoderMonitor(encoder, upload_callback)
                
                response = requests.post(
                    url,
                    data=monitor,
                    headers={**headers, 'Content-Type': monitor.content_type}
                )
        
        console.print()
        console.print("✅ [bold green]Upload complete![/bold green]")
        
    else:
        # Silent mode for automation
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/octet-stream')}
            response = requests.post(url, files=files, headers=headers)
    
    if response.status_code != 200:
        print(response.text)
        print(f"Error: Upload failed with status {response.status_code}")
        sys.exit(1)
    
    try:
        result = response.json()
        file_url = result['files'][0]['url']
        
        if interactive:
            console.print(f"🔗 [bold yellow]URL:[/bold yellow] {file_url}")
        else:
            print(file_url)
            
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Error: Invalid response format: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Upload files to Zipline server')
    parser.add_argument('file', help='File to upload')
    parser.add_argument('max_views', nargs='?', type=int, default=0, help='Maximum number of views (optional)')
    parser.add_argument('-s', '--silent', action='store_true', help='Silent mode - output only the URL')
    
    args = parser.parse_args()
    
    if not args.file:
        print("No target file selected")
        sys.exit(1)
    
    # Determine if interactive mode
    interactive = not args.silent and sys.stdout.isatty()
    
    upload_file(args.file, args.max_views, interactive)

if __name__ == "__main__":
    main() 