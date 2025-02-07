# **Pastit! (Paste-it) & Pasta**
> _Self-hosted, CLI-based code & file sharing powered by [Zipline](https://github.com/diced/zipline)!_

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Using Pastit (for code/text)](#using-pastit-for-codetext)
  - [Using Pasta (for large-files)](#using-pasta-for-files)

---

## Overview
**Pastit** is your self-hosted alternative to Pastebin-like services—quickly share text snippets or code with syntax highlighting.  
**Pasta** is a companion script for uploading large files (archives, images, etc.) just as easily. 

Both scripts leverage your **Zipline** server as the backend. If you’re familiar with [sprunge.us](http://sprunge.us) (now often down) or [pastebin.com](https://pastebin.com/), this is a self-hosted replacement so you never rely on third-party services.  

---

## Features
- **Command-line** interface: Send text/files directly from your terminal.
- **Syntax Highlighting**: Zipline automatically highlights code if it recognizes the file extension.
- **Large File Uploads**: `pasta` can handle archives, logs, images, etc.
- **Self-hosted**: Keep total control over your data & domain—no sign-ups required!
- **Easy Setup**: `setup.sh` installs dependencies (like `jq`, `curl`, `wget`) and configures everything.

---

## Requirements
1. **Zipline** – a running, configured instance ([GitHub Repo](https://github.com/diced/zipline)).
2. A modern Linux environment with:
   - `bash`
   - `curl`
3. (Optional) **sudo** privileges if you want to symlink `pastit` and `pasta` into `/usr/local/bin`.

---

## Installation
1. **Clone** this repository and run setup.sh:
```
git clone https://github.com/harryeffinpotter/pastit
cd pastit
./setup.sh
```
2. Follow the on-screen instructions.

## Usage
This repository includes 2 main scripts, pasta and pastit. Pastit is basically a pastebin alternative that utilizes your self-hosted zipline backend. It has built-in syntax highlighting making it ideal for sharing scripts and/or code. 
Pasta also utilizes the Zipline backend but is instead for hosting files.

## Using Pastit (for code/text)
`pastit <script/code file name>` OR `command | pastit`

**Examples:**  
echo "Hello world" | **pastit**  
**pastit** .zshrc  
**pastit** ~/.ssh/authorized_keys

## Using Pasta (for files)  
`pasta <relative or absolute filepath>`  

**Examples:**  
**pasta** myfeetpics.zip  
**pasta** localjabronis.mp4