#!/usr/bin/env python3
"""
Pasta Optimized - High-performance single file uploader with chunked streaming
Optimized for same-server/LAN uploads to maximize throughput
"""

import os
import sys
import json
import requests
import argparse
from pathlib import Path
from io import BytesIO
import threading
from queue import Queue

try:
    from rich.console import Console
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TransferSpeedColumn, FileSizeColumn
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

class StreamingFileUpload:
    def __init__(self, file_path, chunk_size=8*1024*1024):  # 8MB chunks
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.file = open(file_path, 'rb')
        self.file_size = Path(file_path).stat().st_size
        self.bytes_read = 0
        self.callback = None

    def read(self, size=-1):
        """Read method for requests to call"""
        if size == -1:
            size = self.chunk_size

        data = self.file.read(size)
        if data:
            self.bytes_read += len(data)
            if self.callback:
                self.callback(len(data))
        return data

    def seek(self, offset, whence=0):
        """Seek method for requests compatibility"""
        return self.file.seek(offset, whence)

    def tell(self):
        """Tell method for requests compatibility"""
        return self.file.tell()

    def close(self):
        """Close the file"""
        self.file.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

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

def upload_file(file_path, max_views=0, interactive=True, permanent=False):
    """Upload file with optimized streaming"""
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

    if permanent:
        headers["x-zipline-deletes-at"] = "100y"
        headers["x-zipline-max-views"] = "0"

    console = Console()

    if interactive:
        # Show file info
        console.print(f"⚡ [bold green]Optimized upload:[/bold green] {file_path.name}")
        if permanent:
            console.print(f"♾️  [bold magenta]Permanent upload[/bold magenta] (100 years, unlimited views)")
        elif max_views > 0:
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

            def progress_callback(bytes_uploaded):
                progress.update(task, advance=bytes_uploaded)

            # Use streaming upload with large chunks
            with StreamingFileUpload(file_path, chunk_size=16*1024*1024) as stream_file:  # 16MB chunks
                stream_file.callback = progress_callback

                # Disable request's own chunking and use our streaming
                files = {'file': (file_path.name, stream_file, 'application/octet-stream')}

                # Use a session with connection pooling for better performance
                with requests.Session() as session:
                    # Optimize TCP settings
                    adapter = requests.adapters.HTTPAdapter(
                        pool_connections=1,
                        pool_maxsize=1,
                        max_retries=0
                    )
                    session.mount('http://', adapter)
                    session.mount('https://', adapter)

                    response = session.post(
                        url,
                        files=files,
                        headers=headers,
                        stream=False,  # Don't stream response
                        timeout=(10, None)  # 10 second connection timeout, no read timeout
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

        # Convert /u/ to /view/
        file_url = file_url.replace('/u/', '/view/')

        if interactive:
            console.print(f"🔗 [bold yellow]URL:[/bold yellow] {file_url}")
        else:
            print(file_url)

    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Error: Invalid response format: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Optimized file uploader for Zipline server')
    parser.add_argument('file', help='File to upload')
    parser.add_argument('max_views', nargs='?', type=int, default=0, help='Maximum number of views (optional)')
    parser.add_argument('-s', '--silent', action='store_true', help='Silent mode - output only the URL')
    parser.add_argument('-p', '--perm', '--permanent', action='store_true', help='Permanent upload (100 years, unlimited views)')

    args = parser.parse_args()

    if not args.file:
        print("No target file selected")
        sys.exit(1)

    # Determine if interactive mode
    interactive = not args.silent and sys.stdout.isatty()

    upload_file(args.file, args.max_views, interactive, args.perm)

if __name__ == "__main__":
    main()