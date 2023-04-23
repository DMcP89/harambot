# Harambot
![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Build](https://img.shields.io/github/actions/workflow/status/DMcP89/harambot/pytest.yml?branch=main) ![Version](https://img.shields.io/badge/version-0.3.0--Beta-red)

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)


A Yahoo Fantasy sports bot for Discord.

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

## Prerequisites

In order to properly configure your bot you will need the following:

* Discord API Token
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

## Deployment

### Heroku

Harambot now supports heroku deployments!

Click the button at the top and fill out the form with your discord token and yahoo api client key and and secret.

![heroku-deployment](/assests/heroku-deployment.png)

Once the deployment is complete enable the dyno

![heroku-dyno](/assests/heroku-dyno.png)

### Install package from PIP

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

### Run from source
1. Clone this repository

        git clone git@github.com:DMcP89/harambot.git
        cd harambot

2. Export the following environment variables

   ```
   export DISCORD_TOKEN='[YOUR DISCORD TOKEN]'
   export YAHOO_KEY='[YOUR YAHOO API CLIENT ID]'
   export YAHOO_SECRET='[YOUR YAHOO API CLIENT SECRET]'
   export DATABASE_URL='[YOUR DATABASE URL]'
   ```

3. Run the bot.

    ### On local machine
        make run
    ### With Docker
        make build-image
        make run-docker

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

![discord-oauth](/assests/discord-oauth-generator.png)

2. Set the gateway intents

In order for the bot to work properly it requires the following intents:

* Sever Members Intent
* Message Content Intent

![discord-intents](/assests/discord-intents.png)

3. Navigate to the generated url in a web browser and authorize the bot for your guild

![discord-oauth-url-1](/assests/discord-oauth-url-authorize-1.png)
![discord-oauth-url-2](/assests/discord-oauth-url-authorize-2.png)

### Configure your guild

* Once your bot is added to your guild you can configure it by sending a direct message to the bot with the following command:


![discord-config-commnd](/assests/harambot_configure_1.png)

* Use the Login with Yahoo button to authenticate with Yahoo and get your Yahoo token


![discord-config-yahoo](/assests/harambot_configure_4.png)

* Use the Configure Guild button to configure your guild for the bot


![discord-config-guild](/assests/harambot_configure_2.png)


* You can reconfigure your guild by running the configure command and clicking the Configure Guild button.


![discord-config-guild](/assests/harambot_configure_3.png)


## Command Examples

### $stats Rashaad Penny

![player-details](/assests/player_details.PNG)


### $roster Lamb Chop's Play-Along

![roster](/assests/roster.PNG)


### $standings

![standings](/assests/standings.PNG)


### $matchups

![matchups](/assests/matchups.PNG)


### $trade

![trade](/assests/trade.PNG)


### $RIP "My Season"

![rip](/assests/rip.PNG)
