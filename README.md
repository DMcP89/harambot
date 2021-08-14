# Harambot
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-360/)

A Yahoo Fantasy sports bot for Discord.

## Commands
    $ping                           - Gives the latency of harambot
    $RIP                            - Pay respects
    $standings                      - Returns the current standings of the current league
    $roster "Team name"             - Returns the roster of the given team
    $player_details "Player Name"   - Returns the details of the given player
    $trade                          - Create poll for latest trade for league approval
    $matchups                       - Returns the current weeks matchups

## Prerequisites

In order to properly configure your bot you will need the following:

* Discord API Token
* Discord Guild ID
* Yahoo API Client Id & Secret
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

### Yahoo API Client ID & Secret

1. Navigate to https://developer.yahoo.com/apps/ and click the "Create an App" button
   ![yahoo-create-app](/assests/yahoo-create-app.png)
2. Fill out the form as shown below, you can provide your own values for Application Name,  Description, and Homepage URL. Once complete click the "Create App" button
   ![yahoo-app-details](/assests/yahoo-app-details.png)
3. Copy the Client ID and Client Secret values
   ![yahoo-app-secrets](/assests/yahoo-app-secrets.png) 

### Yahoo League ID

You can find your league's ID under the settings page of your league
![yahoo-league-id](/assests/yahoo-league-id.png)

## Install

1. Clone this repository 

        git clone git@github.com:DMcP89/harambot.git
        cd harambot

2. Configure the bot

   * Create a copy of example.secrets.toml named .secrets.toml
      ```
      cd config
      cp example.secrets.toml .secrets.toml
      ```
   * Update .secrets.toml with the values from the prerequisites section
      ```
      [default]
      DISCORD_TOKEN = 'Discord API Token'
      YAHOO_KEY = 'Yahoo Client ID'
      YAHOO_SECRET = 'Yahoo Client Secret'
      ```
   * Run make configure from the root directory
      ```
      cd ..
      make configure
      ```

3. Run the bot. 

    ### On local machine
        make run
    ### With Docker
        make build-docker
        make run-docker

## Support Harambot!
<a href="https://www.buymeacoffee.com/wochstudios" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>
