@echo off
:: Prompt for Client ID and Client Secret
set /p CLIENT_ID=Enter your Twitch Client ID: 
set /p CLIENT_SECRET=Enter your Twitch Client Secret: 

:: Replace placeholders in the Python script with the provided credentials
powershell -Command "(Get-Content 'Twitch_TTS.py') -replace 'ADD YOUR CLIENT ID HERE', '%CLIENT_ID%' -replace 'ADD YOUR CLIENT SECRET HERE PLEASE', '%CLIENT_SECRET%' | Set-Content 'Twitch_TTS.py'"

:: Run the Python script
python Twitch_TTS.py
