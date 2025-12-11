#!/usr/bin/env python3
"""
Pasta Fast - Chunked parallel file uploader for maximum bandwidth usage

This version splits large files into chunks and uploads them in parallel,
similar to how IDM works, to saturate high-bandwidth connections.
"""

import os
import sys
import json
import requests
import threading
import hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple
from dataclasses import dataclass

# Try importing required packages with helpful error messages
try:
    from rich.console import Console
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TransferSpeedColumn, FileSizeColumn
    from rich.live import Live
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

@dataclass
class ChunkInfo:
    chunk_id: int
    start: int
    end: int
    size: int
    uploaded: int = 0
    url: str = ""
    error: str = ""

class ChunkedUploader:
    def __init__(self, file_path: str, max_views: int = 0, chunk_size: int = 10*1024*1024, max_workers: int = 8):
        self.file_path = Path(file_path)
        self.max_views = max_views
        self.chunk_size = chunk_size  # 10MB chunks by default
        self.max_workers = max_workers
        self.console = Console()
        self.chunks: List[ChunkInfo] = []
        self.progress = None
        self.task_ids = {}
        
    def load_config(self):
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
    
    def create_chunks(self) -> List[ChunkInfo]:
        """Split file into chunks"""
        file_size = self.file_path.stat().st_size
        chunks = []
        
        chunk_id = 0
        start = 0
        
        while start < file_size:
            end = min(start + self.chunk_size, file_size)
            chunk = ChunkInfo(
                chunk_id=chunk_id,
                start=start,
                end=end,
                size=end - start
            )
            chunks.append(chunk)
            
            start = end
            chunk_id += 1
        
        return chunks
    
    def upload_chunk(self, chunk: ChunkInfo, host: str, auth_token: str) -> ChunkInfo:
        """Upload a single chunk"""
        url = f"{host}/api/upload"
        
        # Create headers for this chunk
        headers = {
            "Authorization": auth_token,
            "x-zipline-format": "gfycat",
            "x-zipline-chunk-id": str(chunk.chunk_id),
            "x-zipline-chunk-total": str(len(self.chunks)),
            "x-zipline-original-name": self.file_path.name,
        }
        
        if self.max_views > 0:
            headers["x-zipline-max-views"] = str(self.max_views)
        
        try:
            # Read chunk data
            with open(self.file_path, 'rb') as f:
                f.seek(chunk.start)
                chunk_data = f.read(chunk.size)
            
            # Create filename for this chunk
            chunk_filename = f"{self.file_path.name}.part{chunk.chunk_id:03d}"
            
            # Upload chunk
            files = {'file': (chunk_filename, chunk_data, 'application/octet-stream')}
            
            response = requests.post(url, files=files, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                chunk.url = result['files'][0]['url']
                chunk.uploaded = chunk.size
                
                # Update progress
                if self.progress and chunk.chunk_id in self.task_ids:
                    self.progress.update(self.task_ids[chunk.chunk_id], advance=chunk.size)
                
                return chunk
            else:
                chunk.error = f"HTTP {response.status_code}: {response.text}"
                return chunk
                
        except Exception as e:
            chunk.error = str(e)
            return chunk
    
    def upload_parallel(self, interactive: bool = True):
        """Upload file using parallel chunks"""
        host, auth_token = self.load_config()
        
        if not self.file_path.exists():
            print(f"Error: File '{self.file_path}' not found")
            sys.exit(1)
        
        file_size = self.file_path.stat().st_size
        self.chunks = self.create_chunks()
        
        if interactive:
            self.console.print(f"🚀 [bold green]Fast uploading file:[/bold green] {self.file_path.name}")
            if self.max_views > 0:
                self.console.print(f"📊 [bold blue]Max views:[/bold blue] {self.max_views}")
            
            # Human readable file size
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            elif file_size < 1024 * 1024 * 1024:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            else:
                size_str = f"{file_size / (1024 * 1024 * 1024):.1f} GB"
            
            self.console.print(f"📦 [bold cyan]File size:[/bold cyan] {size_str}")
            self.console.print(f"🔀 [bold yellow]Chunks:[/bold yellow] {len(self.chunks)} × {self.chunk_size // (1024*1024)}MB")
            self.console.print(f"🧵 [bold magenta]Parallel connections:[/bold magenta] {self.max_workers}")
            self.console.print()
            
            # Create progress bars for each chunk
            self.progress = Progress(
                TextColumn("[bold blue]Chunk {task.description}", justify="left"),
                BarColumn(bar_width=20),
                "[progress.percentage]{task.percentage:>3.1f}%",
                console=self.console,
                transient=False
            )
            
            with self.progress:
                # Add task for each chunk
                for chunk in self.chunks:
                    task_id = self.progress.add_task(f"{chunk.chunk_id}", total=chunk.size)
                    self.task_ids[chunk.chunk_id] = task_id
                
                # Upload chunks in parallel
                completed_chunks = []
                failed_chunks = []
                
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    # Submit all chunk uploads
                    future_to_chunk = {
                        executor.submit(self.upload_chunk, chunk, host, auth_token): chunk
                        for chunk in self.chunks
                    }
                    
                    # Collect results
                    for future in as_completed(future_to_chunk):
                        chunk = future.result()
                        if chunk.error:
                            failed_chunks.append(chunk)
                        else:
                            completed_chunks.append(chunk)
        
        else:
            # Silent mode - just upload without progress
            completed_chunks = []
            failed_chunks = []
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_chunk = {
                    executor.submit(self.upload_chunk, chunk, host, auth_token): chunk
                    for chunk in self.chunks
                }
                
                for future in as_completed(future_to_chunk):
                    chunk = future.result()
                    if chunk.error:
                        failed_chunks.append(chunk)
                    else:
                        completed_chunks.append(chunk)
        
        # Handle results
        if failed_chunks:
            if interactive:
                self.console.print("\n❌ [bold red]Some chunks failed:[/bold red]")
                for chunk in failed_chunks:
                    self.console.print(f"  Chunk {chunk.chunk_id}: {chunk.error}")
            print(f"Error: {len(failed_chunks)} chunks failed to upload")
            sys.exit(1)
        
        if interactive:
            self.console.print("\n✅ [bold green]All chunks uploaded successfully![/bold green]")
            self.console.print(f"🔗 [bold yellow]URLs:[/bold yellow]")
            for chunk in sorted(completed_chunks, key=lambda c: c.chunk_id):
                self.console.print(f"  Part {chunk.chunk_id}: {chunk.url}")
        else:
            # Silent mode - just print URLs
            for chunk in sorted(completed_chunks, key=lambda c: c.chunk_id):
                print(chunk.url)

def main():
    if len(sys.argv) < 2:
        print("Usage: ./pasta_fast.py <file> [max_views] [chunk_size_mb] [max_workers]")
        print("  file: File to upload")
        print("  max_views: Maximum number of views (optional, default: 0)")
        print("  chunk_size_mb: Chunk size in MB (optional, default: 10)")
        print("  max_workers: Number of parallel uploads (optional, default: 8)")
        sys.exit(1)
    
    file_path = sys.argv[1]
    max_views = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    chunk_size_mb = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    max_workers = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    
    # Convert MB to bytes
    chunk_size = chunk_size_mb * 1024 * 1024
    
    # Check if running in interactive mode
    interactive = sys.stdout.isatty()
    
    uploader = ChunkedUploader(file_path, max_views, chunk_size, max_workers)
    uploader.upload_parallel(interactive)

if __name__ == "__main__":
    main() 