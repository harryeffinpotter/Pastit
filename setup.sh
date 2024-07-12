#!/bin/bash

mainscript="pastit"

cat ./pastit | grep "ENTER_YOUR_ZIPLINE"
if [[ "$?" == 1 ]] || [[ -f '/usr/local/bin/pastit' ]]; then
    echo "Already configured, exiting!"
    exit 0
fi
clear

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

# Check if zipline.sxcu file exists in the same directory
zipline_file="zipline.sxcu"
if [ ! -f "$zipline_file" ]; then
    echo "ERROR: No reference file found."
    echo -e "\nYou can either -\n1. Paste your details manually into this script in the following prompt.\n2. Put your generated zipline.sxcu file in the same directory as this script and run it again.\n3. Manually edit the main script yourself and supply the necessary infomation, then move it to /usr/local/bin and make it executable.\n\n"
    sleep 3
    echo -e "If you chose 2 or 3, press CTRL+C to exit. If you want to paste in the data, CTRL-Left click this link:"
    printf '\e]8;;https://share.harryeffingpotter.com/u/QHqMKf.mp4\e\\Follow along with this 7 second video guide\e]8;;\e\\\n'
    echo -e "- then paste in the result:"
    read authorizationtoken
    if [ -z "$authorizationtoken" ]; then
        echo "Incorrect output, relaunch the script if you wish to try again!"
        sleep 10
        exit 1
    fi
    echo -e "\nOK Great now post the url of your zipline server!\n"
    echo -e "\nExamples:\nhttps://share.harryeffingpotter.com\n69.42.0.69:3000\nhttp://mySSLinsecure.website.com\nhttps://cool.diccpics.net\netc.\n\nYour zipline base url:"
    read URL
    if [ -z "$URL" ]; then
        echo "Incorrect output, relaunch the script if you wish to try again!"
        sleep 10
        exit 1
    fi
    URL=$(format_url "$URL")
else
    # Read the values from the zipline.sxcu file
    URL=$(jq -r '.RequestURL' "$zipline_file")
    authorizationtoken=$(jq -r '.Headers.Authorization' "$zipline_file")
fi
clear
echo -e "\nHere is what you entered:\n\nAPI url:\n${URL}\n\nAuthorization token:\n${authorizationtoken}\n\nIF THIS IS INCORRECT - PRESS CTRL+C and start over, otherwise PRESS ENTER."
read NOTHING
echo "Now editing pastit script with your information!"
# Replace placeholders in the main script
sed -i "s|ENTER_YOUR_ZIPLINE_URL_HERE/api/upload|$URL|g" "$mainscript"
sed -i "s|ENTER_YOUR_ZIPLINE_AUTHORIZATION_TOKEN_HERE|$authorizationtoken|g" "$mainscript"

echo "Main script updated with URL and Authorization token."

echo -e "\n\nFinalizing!\n\nRIP SPRUNGE, YOU WERE IMMEDIATELY MISSED. WHY DID YOU LEAVE US LIKE THIS, NOT ONCE, BUT TWICE!\n\nEven though you most definitely already know about them if you're here, it still is worth saying:\n\nBIG THANKS TO ZIPLINE DEVS FOR THIS INCREDIBLE, FREE, AMAZING REPO, SHOW THEM SOME LOVE PLEASE\n\n https://github.com/diced/zipline\n\nBUY THOSE BOYS A COFFEE FOR FUCKS SAKE!"
sleep 8
echo -e "\n\nHOW TO USE PASTIT:\n\nSTDOUT:\necho \"pastitties\" | pastit\n\nPASTE FILE:\npastit ~/.zshrc\n\nFINISHED! COPYING EXECUTABLE..."

chmod +x ./pastit
sudo cp ./pastit /usr/local/bin/pastit

check_path() {
    echo $PATH | grep -q "/usr/local/bin"
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
