#!/bin/bash


rm config/.secrets.toml
echo 'Creating .secrets.toml file...'
echo '[default]' > config/.secrets.toml
echo 'Enter Discord token:' 
read DISCORD_TOKEN; echo "DISCORD_TOKEN = '$DISCORD_TOKEN'" >> config/.secrets.toml;
echo 'Enter Yahoo Consumer key:' 
read YAHOO_KEY; echo "YAHOO_KEY = '$YAHOO_KEY'" >> config/.secrets.toml;
echo 'Enter Yahoo Consumer secrect:' 
read YAHOO_SECRET; echo "YAHOO_SECRET = '$YAHOO_SECRET'" >> config/.secrets.toml;
echo 'Creating guild datastore...'
test -f config/guilds.json || echo '{}' > config/guilds.json
python harambot/add_guild.py
rm secrets.json