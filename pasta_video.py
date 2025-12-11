#!/usr/bin/env python3
"""
Pasta Video - Timeless video uploader for tutorials
No view limits, no time limits, permanent hosting

Usage:
   ./pasta_video video.mp4           # Upload video with no limits
   ./pasta_video -d "Tutorial" vid.mp4  # Upload with description
   ./pasta_video -p password vid.mp4    # Password protected video
"""

import os
import sys
import json
import requests
import argparse
from pathlib import Path

try:
    from rich.console import Console
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TransferSpeedColumn, FileSizeColumn
    from rich.panel import Panel
    from rich.table import Table
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

def format_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def upload_video(file_path, password=None, description=None, folder=None):
    """Upload video with permanent hosting (no limits)"""
    host, auth_token = load_config()
    url = f"{host}/api/upload"
    
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    
    # Check if it's a video file
    video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg', '.3gp'}
    if file_path.suffix.lower() not in video_extensions:
        console = Console()
        console.print(f"⚠️  [yellow]Warning: '{file_path.suffix}' may not be a video format[/yellow]")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    file_size = file_path.stat().st_size
    
    # Headers - NO view limits, NO expiration
    headers = {
        "Authorization": auth_token,
        "x-zipline-format": "gfycat",
        "x-zipline-original-name": "true",
        # Explicitly NOT setting:
        # - x-zipline-max-views (no view limit)
        # - x-zipline-expires-at (no expiration)
    }
    
    # Add password protection if specified
    if password:
        headers["x-zipline-password"] = password
    
    # Add to folder if specified
    if folder:
        headers["x-zipline-folder"] = folder
    
    console = Console()
    
    # Show upload info
    info_table = Table(show_header=False, box=None)
    info_table.add_column("Property", style="cyan")
    info_table.add_column("Value", style="white")
    
    info_table.add_row("📹 File", file_path.name)
    info_table.add_row("📦 Size", format_size(file_size))
    info_table.add_row("♾️  View Limit", "UNLIMITED")
    info_table.add_row("⏰ Time Limit", "PERMANENT")
    
    if password:
        info_table.add_row("🔒 Password", "Protected")
    if description:
        info_table.add_row("📝 Description", description[:50] + "..." if len(description) > 50 else description)
    if folder:
        info_table.add_row("📁 Folder", folder)
    
    console.print(Panel(info_table, title="[bold green]Video Upload Details[/bold green]", border_style="green"))
    console.print()
    
    # Create progress bar
    progress = Progress(
        TextColumn("[bold blue]Uploading video...", justify="right"),
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
            # Determine MIME type for video
            mime_type = 'video/mp4' if file_path.suffix.lower() == '.mp4' else 'application/octet-stream'
            
            encoder = MultipartEncoder(
                fields={'file': (file_path.name, f, mime_type)}
            )
            monitor = MultipartEncoderMonitor(encoder, upload_callback)
            
            response = requests.post(
                url,
                data=monitor,
                headers={**headers, 'Content-Type': monitor.content_type}
            )
    
    console.print()
    
    if response.status_code != 200:
        console.print(f"[red]Error: Upload failed with status {response.status_code}[/red]")
        console.print(response.text)
        sys.exit(1)
    
    try:
        result = response.json()
        file_info = result['files'][0]
        file_url = file_info['url']
        
        # Success message
        console.print("[bold green]✅ Video uploaded successfully![/bold green]")
        console.print()
        
        # Display result in a nice table
        result_table = Table(title="[bold]Upload Results[/bold]", show_header=False, box=None)
        result_table.add_column("Property", style="cyan")
        result_table.add_column("Value", style="yellow")
        
        result_table.add_row("🔗 URL", file_url)
        result_table.add_row("♾️  Status", "Permanent (No limits)")
        
        if 'views' in file_info:
            result_table.add_row("👁️  Views", str(file_info.get('views', 0)))
        
        if password:
            result_table.add_row("🔒 Access", "Password Protected")
        
        console.print(Panel(result_table, border_style="green"))
        
        # Provide embed code for HTML
        console.print("\n[bold cyan]HTML Embed Code:[/bold cyan]")
        embed_code = f'<video controls width="100%">\n  <source src="{file_url}" type="video/mp4">\n  Your browser does not support the video tag.\n</video>'
        console.print(Panel(embed_code, border_style="cyan"))
        
        # Copy URL to clipboard if possible
        try:
            import subprocess
            subprocess.run(['xclip', '-selection', 'clipboard'], input=file_url.encode(), check=True)
            console.print("\n[green]✅ URL copied to clipboard![/green]")
        except:
            pass
            
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        console.print(f"[red]Error: Invalid response format: {e}[/red]")
        console.print(response.text)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Upload videos to Zipline with permanent hosting (no view/time limits)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s video.mp4                    # Upload video with no limits
  %(prog)s -d "Python Tutorial" tut.mp4 # Upload with description
  %(prog)s -p mypassword video.mp4      # Password protected video
  %(prog)s -f tutorials lesson1.mp4     # Upload to 'tutorials' folder
        """
    )
    
    parser.add_argument('file', help='Video file to upload')
    parser.add_argument('-p', '--password', help='Password protect the video')
    parser.add_argument('-d', '--description', help='Description for the video')
    parser.add_argument('-f', '--folder', help='Folder to organize the video in')
    
    args = parser.parse_args()
    
    if not args.file:
        parser.print_help()
        sys.exit(1)
    
    upload_video(args.file, args.password, args.description, args.folder)

if __name__ == "__main__":
    main()