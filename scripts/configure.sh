#!/bin/bash

echo 'Creating guild datastore...'
test -f config/guilds.json || echo '{}' > config/guilds.json
python ./scripts/add_guild.py
rm secrets.json