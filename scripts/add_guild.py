from yahoo_oauth import OAuth2
from dynaconf import Dynaconf
import json
import os
import logging

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=['settings.toml', '.secrets.toml'],
    environments=True,
)

oauth_logger = logging.getLogger('yahoo_oauth')
oauth_logger.disabled = True

dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.dirname(dir_path) + '/config/guilds.json', 'r+') as f:
    guilds = json.load(f)

    guild = input("Enter Discord Guild ID:\n")

    if guild in guilds:
        print("configuration for guild:{} already exists".format(guild))
        exit()
    
    league = input("Enter Yahoo League ID:\n")

    league_type = input("Enter Yahoo League Type(nfl, nhl, nba, mlb):\n")

    RIP_text = input("Enter text to use with $RIP command:\n")

    RIP_image_url = input("Enter image url to use with $RIP command:\n")

    print("Follow this url to login to Yahoo and provide the verifer code...")
    oauth = OAuth2(consumer_key=settings.yahoo_key, consumer_secret=settings.yahoo_secret, browser_callback=False)

    guild_details = {
        guild:{
            "access_token": oauth.access_token,
            "guid": oauth.guid,
            "refresh_token": oauth.refresh_token,
            "token_time": oauth.token_time,
            "token_type": oauth.token_type,
            "league_id": league,
            "league_type": league_type,
            "RIP_text": RIP_text,
            "RIP_image_url": RIP_image_url
        }
    }

    guilds.update(guild_details)
    f.seek(0)
    json.dump(guilds, f, indent=4)
    f.close()
