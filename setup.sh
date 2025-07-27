#!/bin/bash

# Prompt for Twitch credentials
read -p "Enter your Twitch Client ID: " CLIENT_ID
read -p "Enter your Twitch Client Secret: " CLIENT_SECRET

# Replace placeholders in the Python script
sed -i.bak "s|ADD YOUR CLIENT ID HERE|$CLIENT_ID|g" Twitch_TTS.py
sed -i.bak "s|ADD YOUR CLIENT SECRET HERE PLEASE|$CLIENT_SECRET|g" Twitch_TTS.py

# Run the Python script
python3 Twitch_TTS.py
