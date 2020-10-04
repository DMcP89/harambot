# Harambot
A Yahoo Fantasy sports bot for Discord.

## Commands
    $ping                           - Gives the latency of harambot
    $RIP                            - Pay respects
    $standings                      - Returns the current standings of HML
    $roster "Team name"             - Returns the roster of the given team
    $player_details "Player Name"   - Returns the details of the given player
    $trade                          - Propose a trade for league approval
    $matchups                       - Returns the current weeks matchups

## Setup

1. Clone this repository and install requirements

        git clone git@github.com:DMcP89/harambot.git
        pip install -r requirements.txt

2. Create configuration files.

    - Rename the sample.guilds.json & sample.harambot.config files to guilds.json and harmabot.config respectively.
    - Update the values with your own values
        - harambot.config - Used for connecting to Discord and Yahoo APIs

                {
                    "AUTH": {
                        "_comment": "Discord bot token (via app > bot account).",
                        "TOKEN": "DISCORD_TOKEN",
                        "CONSUMER_KEY": "YAHOO_CONSUMER_KEY",
                        "CONSUMER_SECRET": "YAHOO_CONSUMER_SECRET"
                    }
                }
        - guilds.json - Used for Authenticating with the Yahoo API

                {
                    "GUILD_ID": {
                        "access_token": "ACCESS_TOKEN",
                        "guid": "GUID",
                        "refresh_token": "REFRESH_TOKEN",
                        "token_time": 0.0,
                        "token_type": "bearer",
                        "league_id": "YAHOO_LEAGUE_ID"
                    }
                }
    - Run scripts/get_yahoo_configs.py to get the values for guilds.json 

3. Run the bot. 

    ### With Python
        python harambot.py
    ### With Docker
        docker build -t harambot:1.0 .
        docker run harambot:1.0