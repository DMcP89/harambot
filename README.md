# Harambot
A Yahoo Fantasy sports bot for Discord.

## Commands
    $ping                           - Gives the latency of harambot
    $RIP                            - Pay respects
    $standings                      - Returns the current standings of HML
    $roster "Team name"             - Returns the roster of the given team
    $player_details "Player Name"   - Returns the details of the given player
    $trade                          - Create poll for latest trade for league approval
    $matchups                       - Returns the current weeks matchups

## Setup

1. Clone this repository and install requirements

        git clone git@github.com:DMcP89/harambot.git
        pip install -r requirements.txt

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