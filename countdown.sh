#!/bin/bash
echo "On/Off Monitor: Checking for updates..."
git pull
if test -f "ExtraLogFolder.txt"; then
    folder=$PWD
    extralogfolder=$(<ExtraLogFolder.txt)
    cd "$extralogfolder"
    echo "On/Off Monitor: Checking for extra log conditions updates..."
    git pull
    cd "$folder"
fi
echo "On/Off Monitor will start in 5 seconds. Press Ctrl-C to exit"
sleep 5
sudo python3 .
