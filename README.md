# Harambot
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-360/)

A Yahoo Fantasy sports bot for Discord.

## Commands
    $ping                           - Gives the latency of harambot
    $RIP                            - Pay respects
    $standings                      - Returns the current standings of HML
    $roster "Team name"             - Returns the roster of the given team
    $player_details "Player Name"   - Returns the details of the given player
    $trade                          - Create poll for latest trade for league approval
    $matchups                       - Returns the current weeks matchups

## Prerequisites

In order to properly configure your bot you will need the following:

* Discord API Token
* Discord Guild ID
* Yahoo API Consumer key & secret
* Yahoo League ID

### Discord API Token

1. Navigate to https://discord.com/developers/applications and click the "New Application" button
   ![discord-new-application](/assests/discord-new-application.png)
2. Give your bot a name
3. Navigate to the bot section of your application and click the "Add Bot" button
   ![discord-add-bot](/assests/discord-add-bot.png)
4. Click the "Copy" button under token to copy your bots API token to your clipboard
   ![discord-copy-token](/assests/discord-copy-token.png)

### Discord Guild ID
1. Open the discord web app  - https://discord.com/app
2. Navigate to your guild
3. Copy the guild ID from the url
   ``` 
   https://discord.com/channels/[guild-id-is-here]/12345678910
   ```

### Yahoo API Consumer Key & Secret

### Yahoo League ID

## Install

1. Clone this repository 

        git clone git@github.com:DMcP89/harambot.git

2. Configure the bot

        make configure

3. Run the bot. 

    ### With Python
        python harambot.py
        or
        make run
    ### With Docker
        make build-docker
        make run-docker