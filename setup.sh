#!/bin/bash
# setup.sh
cp .env.example .env
# Detect the OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Cannot determine OS. Exiting."
    exit 1
fi
clear
top_stamp(){
    echo "=========================================="
    echo "= PASTA/PASTIT setup by harryeffinpotter ="
    echo "=========================================="
    echo ""
}
top_stamp
echo "Starting Pasta/Pastit setup..."
sleep 2
echo "Determining OS and checking for required packages..."
sleep 3
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

# Zipline configuration section
echo "Zipline Instance Configuration"
read -p "Is Zipline running on this same system? (yes/no) " zipline_local
while true; do
    if [ "$zipline_local" = "yes" ]; then
        # Internal connection configuration
        while true; do
            read -p "Enter Zipline's local port (default 3000): " zipline_port
            zipline_port=${zipline_port:-3000}
            if [[ "$zipline_port" =~ ^[0-9]+$ ]] && [ "$zipline_port" -ge 1 ] && [ "$zipline_port" -le 65535 ]; then
                host="127.0.0.1:$zipline_port"
                break
            else
                echo "Invalid port number. Please enter between 1-65535"
            fi
        done
    elif [ "$zipline_local" = "no" ]; then
        while true; do
            read -p "Enter Zipline instance address (domain/IP:port or URL): " remote_target
            if [[ "$remote_target" =~ ^.+:[0-9]+$ ]] || [[ "$remote_target" =~ ^https?:// ]]; then
                host="$remote_target"
                break
            else
                echo "Invalid format. Use format: domain.com:port, 192.168.1.1:3000, or https://zipline.example.com"
            fi
        done
        break
    else
        echo "Invalid response. Please enter 'yes' or 'no'."
    fi
done
# Update .env file
sed -i "s|^host=.*|host=$host|" .env
sleep 2

clear
top_stamp
echo -e "Paste your Zipline authorization token.\n\nDon't know where to find it?"
printf '\e]8;;https://share.harryeffingpotter.com/u/QHqMKf.mp4\e\\Follow along with this 7 second video guide to get your token\e]8;;\e\\\n'
echo -e "\nThen paste it below:"
read authorization_token
while true; do
    if [ -z "$authorization_token" ]; then
        echo "Incorrect output, relaunch the script if you wish to try again!"
        sleep 3
    else
        break
    fi
done
clear
top_stamp
echo -e "Authorization token:\n${authorization_token}\n\nwas written to .env file in repo directory."
sleep 5
clear
top_stamp
echo -e "OK Great."
echo -e "Now if this system is the same as  for your zipline server if you have one setup, if not just post the IP of your zipline system and the port number (the default is 3000).\n\nExamples:\n69.4.20.69:3000\nhttps://zipline.mysite.com\n\nEnter your zipline url now:"
read target_domain
if [ -z "$target_domain" ]; then
    echo "Incorrect output, relaunch the script if you wish to try again!"
    sleep 10
    exit 1
fi
# Update the .env file in the current directory:
sed -i "s/^authorization_token=.*/authorization_token=${authorization_token}/" .env
sed -i "s|^host=.*|host=${host}|" .env
sed -i "s|^target_domain=.*|target_domain=${target_domain}|" .env
sudo mkdir /etc/pastit
sudo cp -a .env /etc/pastit/.env
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
clear 
top_stamp
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
sleep 5
clear
top_stamp
echo "Pasta/pastit installation complete."
echo -e "\nUsage:"
echo "pasta file.zip # To upload files"
echo -e "pastit script.py\nOR\necho \"Output\" | pastit # To host syntax highlighted code"
echo -e "\nThanks for installing! Hope you find it as useful as I do!\n"
sleep 2
