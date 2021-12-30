#!/bin/bash
echo "On/Off Monitor: Checking for updates..."
git pull
echo "On/Off Monitor will start in 5 seconds. Press Ctrl-C to exit"
sleep 5
sudo python3 .
