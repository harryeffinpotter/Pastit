#!/bin/bash

# Path to the main script
main_script="pastit"


cat ./pastit | grep "ENTER_YOUR_ZIPLINE"
if [[ "$?" == 1 ]] || [[ -z "/usr/local/bin/pastit" ]]; then
echo "Already configured, exiting!"
exit 0
fi
clear
# Check if zipline.sxcu file exists in the same directory
zipline_file="zipline.sxcu"
if [ ! -f "$zipline_file" ]; then
    echo "ERROR: No reference file found."
    echo -e "\nYou can either -\n1. Paste your details manually into this script in the following prompt.\n2. Put your generated zipline.sxcu file in the same directory as this script and run it again.\n3. Manually edit the main script yourself and supply the necessary infomation, then move it to /usr/local/bin and make it executable.\n\n"
    sleep 10
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
else
    # Read the values from the zipline.sxcu file
    URL=$(jq -r '.RequestURL' "$zipline_file")
    authorizationtoken=$(jq -r '.Headers.Authorization' "$zipline_file")
fi
clear
echo -e "Awesome! Looks like we have all we need!\n"
sleep 2
echo -e "\nHere is the gathered information:\n\nAPI url:\n${URL}/api/upload\n\nAuthorization token:\n${authorizationtoken}\n\n...please verify that it is correct.\n\nAfter this point if this info is wrong - you must correct your pastit file at /usr/local/bin/pastit.\nYou can press CTRL+C now and try again to avoid this right now.\n\nScript will now pause while you verify this information, press ENTER when done to write your changes."
read NOTHING
echo "Now editing pastit script with your information!"
# Replace placeholders in the main script
sed -i "s|ENTER_YOUR_ZIPLINE_URL_HERE/api/upload|$request_url|g" "$main_script"
sed -i "s|ENTER_YOUR_ZIPLINE_AUTHORIZATION_TOKEN_HERE|$authorization_token|g" "$main_script"

echo "Main script updated with URL and Authorization token."


echo -e "\n\nIf you wish to change the default extension replacement for extensionless files you can find that on LINE 15, and a setting to decide whether or not to count hidden files (files that start with a \'.\' like .zshrc, .config files, etc) as extensionless on LINE 18\n\nThe default settings are .sh and true, this is so files like .zshrc have proper bash syntax highlighting, but ultimately - it's up to you."


echo -e "\n\nFinalizing - copying script to /usr/local/bin, if this is not on your $PATH variable, I would add it to your path in your .bashrc or .zshrc, its the typical spot for user scripts/binaries in my experience. Thanks and enjoy!\n\nRIP SPRUNGE, YOU WERE IMMEDIATELY MISSED. WHY DID YOU LEAVE US LIKE THIS, NOT ONCE, BUT TWICE, MY HEART CAN NO LONGER TAKE IT. I HAVE MOVED ON.\n\nand even though you most definitely already know about them if you're here, it still is worth saying:\n\nBIG THANKS TO ZIPLINE DEVS FOR THIS INCREDIBLE, FREE, AMAZING REPO, SHOW THEM SOME LOVE PLEASE https://github.com/diced/zipline, BUY THOSE BOYS A COFFEE FOR FUCKS SAKE!"

echo -e "\n\nHOW TO USE PASTIT:\n\nSTDOUT:\necho "pastitties" | pastit\n\nPASTE FILE:\npastit ~/.zshrc\n\nFINISHED! COPYING EXECUTABLE..."
 
chmod +x ./pastit
cp pastit /usr/local/bin/pastit

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
    echo "/usr/local/bin is already in your PATH."
fi
