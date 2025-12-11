#!/bin/bash

# pastit setup script
# Detects Linux distribution and installs required packages

set -e

echo "🍝 Setting up pastit dependencies..."

# Function to detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo $ID
    elif type lsb_release >/dev/null 2>&1; then
        lsb_release -si | tr '[:upper:]' '[:lower:]'
    elif [ -f /etc/redhat-release ]; then
        echo "rhel"
    elif [ -f /etc/debian_version ]; then
        echo "debian"
    else
        echo "unknown"
    fi
}

# Function to install packages based on distro
install_packages() {
    local distro=$1
    
    case $distro in
        "arch"|"manjaro"|"endeavouros")
            echo "📦 Detected Arch-based system"
            echo "Installing packages with pacman..."
            sudo pacman -S --needed --overwrite='/usr/lib/python*/site-packages/*' \
                python-rich python-requests python-requests-toolbelt python-dotenv
            ;;
        "ubuntu"|"debian"|"pop"|"mint")
            echo "📦 Detected Debian-based system"
            echo "Installing packages with apt..."
            sudo apt update
            sudo apt install -y python3-pip python3-venv
            # Install via pip since debian packages might be outdated
            pip3 install --break-system-packages rich requests requests-toolbelt python-dotenv
            ;;
        "fedora"|"centos"|"rhel"|"rocky"|"almalinux")
            echo "📦 Detected Red Hat-based system"
            echo "Installing packages with dnf/yum..."
            if command -v dnf >/dev/null 2>&1; then
                sudo dnf install -y python3-pip
            else
                sudo yum install -y python3-pip
            fi
            pip3 install --break-system-packages rich requests requests-toolbelt python-dotenv
            ;;
        "opensuse"|"sles")
            echo "📦 Detected SUSE-based system"
            echo "Installing packages with zypper..."
            sudo zypper install -y python3-pip
            pip3 install --break-system-packages rich requests requests-toolbelt python-dotenv
            ;;
        *)
            echo "⚠️  Unknown distribution: $distro"
            echo "Attempting to install via pip..."
            if command -v pip3 >/dev/null 2>&1; then
                pip3 install --break-system-packages rich requests requests-toolbelt python-dotenv
            elif command -v pip >/dev/null 2>&1; then
                pip install --break-system-packages rich requests requests-toolbelt python-dotenv
            else
                echo "❌ pip not found. Please install Python packages manually:"
                echo "   pip install rich requests requests-toolbelt python-dotenv"
                exit 1
            fi
            ;;
    esac
}

# Function to verify installation
verify_installation() {
    echo "🔍 Verifying installation..."
    
    if python3 -c "import rich, requests, requests_toolbelt, dotenv" 2>/dev/null; then
        echo "✅ All dependencies installed successfully!"
        return 0
    else
        echo "❌ Some dependencies are missing. Trying alternative installation..."
        return 1
    fi
}

# Function to fallback installation
fallback_install() {
    echo "🔄 Attempting fallback installation..."
    
    # Try different pip commands
    for pip_cmd in "pip3" "pip" "python3 -m pip" "python -m pip"; do
        if command -v $pip_cmd >/dev/null 2>&1; then
            echo "Trying $pip_cmd..."
            $pip_cmd install --break-system-packages rich requests requests-toolbelt python-dotenv
            if verify_installation; then
                return 0
            fi
        fi
    done
    
    echo "❌ Failed to install dependencies. Please install manually:"
    echo "   pip install --break-system-packages rich requests requests-toolbelt python-dotenv"
    exit 1
}

# Main installation process
main() {
    echo "🔍 Detecting Linux distribution..."
    
    DISTRO=$(detect_distro)
    echo "Detected: $DISTRO"
    
    # Install packages
    install_packages "$DISTRO"
    
    # Verify installation
    if ! verify_installation; then
        fallback_install
    fi
    
    # Make pasta executable
    if [ -f "pasta.py" ]; then
        chmod +x pasta.py
        echo "✅ Made pasta.py executable"
    fi
    
    # Create symlink to /usr/local/bin/pasta
    if [ -f "pasta.py" ]; then
        PASTA_PATH=$(pwd)/pasta.py
        echo "🔗 Creating symlink to /usr/local/bin/pasta..."
        if sudo ln -sf "$PASTA_PATH" /usr/local/bin/pasta; then
            echo "✅ Created symlink: /usr/local/bin/pasta -> $PASTA_PATH"
            echo "   You can now use 'pasta' from anywhere!"
        else
            echo "⚠️  Failed to create symlink. You may need to run with sudo or create manually:"
            echo "   sudo ln -sf $PASTA_PATH /usr/local/bin/pasta"
        fi
    fi
    
    # Test the installation
    echo "🧪 Testing pasta script..."
    if [ -f "pasta.py" ]; then
        if python3 pasta.py 2>&1 | grep -q "No target file selected"; then
            echo "✅ pasta.py is working correctly!"
            echo ""
            echo "🎉 Setup complete! You can now:"
            echo "   1. Test: ./pasta.py some_file.txt"
            echo "   2. Use globally: pasta some_file.txt"
            echo "   3. Configure .env file for your Zipline server"
        else
            echo "⚠️  pasta.py may have issues. Check your .env configuration."
        fi
    else
        echo "⚠️  pasta.py not found in current directory"
    fi
}

# Run main function
main "$@"
