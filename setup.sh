#!/bin/bash
# setup.sh

# Detect the OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Cannot determine OS. Exiting."
    exit 1
fi

# Install jq based on detected OS
case $OS in
    ubuntu|debian)
        echo "Detected $OS. Installing jq using apt..."
        sudo apt update && sudo apt install -y jq curl wget
        ;;
    arch)
        echo "Detected Arch Linux. Installing jq using pacman..."
        sudo pacman -Sy --noconfirm jq curl wget
        ;;
    fedora)
        echo "Detected Fedora. Installing jq using dnf..."
        sudo dnf install -y jq curl wget
        ;;
    centos|rhel)
        echo "Detected $OS. Installing jq using yum..."
        sudo yum install -y jq curl wget
        ;;
    *)
        echo "Unsupported OS: $OS. Exiting."
        exit 1
        ;;
esac

# Verify installation
if command -v jq &> /dev/null; then
    echo "jq successfully installed."
else
    echo "jq installation failed."
    exit 1
fi

# Function to format the URL correctly
format_url() {
    local input_url=$1
    # Remove existing /api/upload if it appears
    formatted_url=$(echo "$input_url" | sed 's#/api/upload##g')

    # Add https:// if not present
    if [[ ! $formatted_url =~ ^http ]]; then
        formatted_url="https://$formatted_url"
    fi

    # Ensure there's only one forward slash at the end before appending /api/upload
    formatted_url=$(echo "$formatted_url" | sed 's#/*$##')
    formatted_url="$formatted_url/api/upload"

    echo "$formatted_url"
}

echo "Please paste your Zipline authorization token now."
printf '\e]8;;https://share.harryeffingpotter.com/u/QHqMKf.mp4\e\\Follow along with this 7 second video guide\e]8;;\e\\\n'
echo -e "- then paste in the result:"
read authorizationtoken
if [ -z "$authorizationtoken" ]; then
    echo "Incorrect output, relaunch the script if you wish to try again!"
    sleep 10
    exit 1
fi
echo -e "\nOK Great now post the domain for your zipline server if you have one setup, if not just post the IP of your zipline system and the port number (the default is 3000).\n\nExamples:\n69.4.20.69:3000\nhttps://zipline.mysite.com"
read URL
if [ -z "$URL" ]; then
    echo "Incorrect output, relaunch the script if you wish to try again!"
    sleep 10
    exit 1
fi
URL=$(format_url "$URL")
# Update the .env file in the current directory:
sed -i "s/^authtoken=.*/authtoken=${authorizationtoken}/" .env
sed -i "s|^url=.*|url=${URL}|" .env

echo "Making script executable..."
chmod +x "$(pwd)/pastit"
chmod +x "$(pwd)/pasta"

###################
# SYMLINK CREATION
###################

# Using /usr/local/bin is best practice for user-installed executables.
pastit_path="/usr/local/bin/pastit"
pasta_path="/usr/local/bin/pasta"

# Remove any existing file or symlink at the target location
if [ -e "$pastit_path" ] || [ -L "$pastit_path" ]; then
    echo "Removing existing file or symlink at $link_path"
    sudo rm -f "$pastit_path"
fi
if [ -e "$pasta_path" ] || [ -L "$pasta_path" ]; then
    echo "Removing existing file or symlink at $pasta_path"
    sudo rm -f "$pasta_path"
fi

# Make symlinks
echo "Creating pastit symlink: $link_path -> $(pwd)/pastit"
sudo ln -s "$(pwd)/pastit" "$pastit_path"
echo "Pastit symlink created successfully."

echo "Creating pasta symlink: $pasta_path -> $(pwd)/pasta"
sudo ln -s "$(pwd)/pasta" "$pasta_path"
echo "Pasta symlink created successfully!"

check_path() {
    echo "$PATH" | grep -q "/usr/local/bin"
    return $?
}

# Function to append /usr/local/bin to .bashrc and .zshrc
append_to_files() {
    echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
    echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc
    echo "/usr/local/bin has been added to your PATH in .bashrc and .zshrc"
}

check_path
if [ $? -ne 0 ]; then
    echo "/usr/local/bin is not in your PATH."
    read -p "Would you like to add /usr/local/bin to your PATH in .bashrc and .zshrc so that pastit can be usable at launch? (yes/no) " response
    if [ "$response" == "yes" ]; then
        append_to_files
    else
        echo "No changes made to your PATH."
    fi
else
    echo "Good news! /usr/local/bin is already in your PATH."
fi
