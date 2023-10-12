# Harambot
_An interactive Yahoo Fantasy sports bot for Discord._

![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Build](https://img.shields.io/github/actions/workflow/status/DMcP89/harambot/pytest.yml?branch=main) ![Version](https://img.shields.io/badge/version-0.3.3--Beta-red)

![harambot-logo](https://raw.githubusercontent.com/DMcP89/harambot/main/assests/harambot-1.jpg)



[![Discord](https://img.shields.io/badge/Add_Harambot_To_Your_Server-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)](http://harambot.io)





## Commands
    /ping                           - Gives the latency of harambot
    /RIP                            - Pay respects
    /standings                      - Returns the current standings of the current league
    /roster "Team name"             - Returns the roster of the given team
    /stats "Player Name"            - Returns the details of the given player
    /trade                          - Create poll for latest trade for league approval
    /matchups                       - Returns the current weeks matchups
    /waiver                         - Returns the waiver wire tranasactions from the previous 24 hours
    /configure                      - Configure the bot for your guild

You can find example output of these commands [here](https://github.com/DMcP89/harambot/wiki#command-examples)


## Roll your own instance

### Prerequisites

In order to properly configure your bot you will need the following:

* [Discord API Token](https://github.com/DMcP89/harambot/wiki/Prerequisites#discord-api-token)
* [Yahoo API Client Id & Secret](https://github.com/DMcP89/harambot/wiki/Prerequisites#yahoo-api-client-id--secret)
* [Yahoo League ID](https://github.com/DMcP89/harambot/wiki/Prerequisites#yahoo-league-id)

_Visit our [wiki](https://github.com/DMcP89/harambot/wiki) for a step by step guide on how to obtain these values._

### Run the bot in the cloud

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/DMcP89/harambot)

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)


### Run the bot locally using pip package

1. Install the harambot package using pip

        pip install harambot

2. Export the following environment variables

   ```
   export DISCORD_TOKEN='[YOUR DISCORD TOKEN]'
   export YAHOO_KEY='[YOUR YAHOO API CLIENT ID]'
   export YAHOO_SECRET='[YOUR YAHOO API CLIENT SECRET]'
   export DATABASE_URL='[YOUR DATABASE URL]'
   ```

3. Run the bot

        harambot

### Run the bot locally using docker

1. Pull the latest image from docker hub

        docker pull dmcp89/harambot

2. Export the following environment variables

   ```
   export DISCORD_TOKEN='[YOUR DISCORD TOKEN]'
   export YAHOO_KEY='[YOUR YAHOO API CLIENT ID]'
   export YAHOO_SECRET='[YOUR YAHOO API CLIENT SECRET]'
   export DATABASE_URL='[YOUR DATABASE URL]'
   ```

3. Run the bot

        docker run --name harambot \
        -e DISCORD_TOKEN=$DISCORD_TOKEN \
        -e YAHOO_KEY=$YAHOO_KEY \
        -e YAHOO_SECRET=$YAHOO_SECRET \
        -e DATABASE_URL=$DATABASE_URL \
        --rm dmcp89/harambot


## Setup

### Add the bot to your guild
1. Generate a OAuth url from the discord developer portal using the bot scope and the following permissions:

* Send Messages
* Send Messages in Threads
* Embed Links
* Attach Files
* Read Message History
* Add Reactions
* Use Slash Commands

The permission value should be 277025507392

![discord-oauth](https://raw.githubusercontent.com/DMcP89/harambot/main/assests/discord-oauth-generator.png)

2. Set the gateway intents

In order for the bot to work properly it requires the following intents:

* Sever Members Intent
* Message Content Intent

![discord-intents](https://raw.githubusercontent.com/DMcP89/harambot/main/assests/discord-intents.png)

3. Navigate to the generated url in a web browser and authorize the bot for your guild

![discord-oauth-url-1](https://raw.githubusercontent.com/DMcP89/harambot/main/assests/discord-oauth-url-authorize-1.png)
![discord-oauth-url-2](https://raw.githubusercontent.com/DMcP89/harambot/main/assests/discord-oauth-url-authorize-2.png)

### Configure your guild

* Once your bot is added to your guild you can configure it by using the /configure command:


![discord-config-commnd](https://raw.githubusercontent.com/DMcP89/harambot/main/assests/harambot_configure_1.png)

* Use the Login with Yahoo button to authenticate with Yahoo and get your Yahoo token


![discord-config-yahoo](https://raw.githubusercontent.com/DMcP89/harambot/main/assests/harambot_configure_4.png)

* Use the Configure Guild button to configure your guild for the bot


![discord-config-guild](https://raw.githubusercontent.com/DMcP89/harambot/main/assests/harambot_configure_2.png)


* You can reconfigure your guild by running the configure command and clicking the Configure Guild button.


![discord-config-guild](https://raw.githubusercontent.com/DMcP89/harambot/main/assests/harambot_configure_3.png)
