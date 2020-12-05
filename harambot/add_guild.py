from yahoo_oauth import OAuth2
from config import settings
import json
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
with open(settings.GUILDS_DATASTORE_LOC, 'r+') as f:
    guilds = json.load(f)

    guild = input("Enter Discord Guild ID:\n")
    
    league = input("Enter Yahoo League ID:\n")

    RIP_text = input("Enter text to use with $RIP command:\n")

    RIP_image_url = input("Enter image url to use with $RIP command:\n")

    if guilds[guild]:
        exit()

    oauth = OAuth2(settings.yahoo_key, settings.yahoo_secret)
    os.remove('secrets.json')

    guild_details = {
        guild:{
            "access_token": oauth.access_token,
            "guid": oauth.guid,
            "refresh_token": oauth.refresh_token,
            "token_time": oauth.token_time,
            "token_type": oauth.token_type,
            "league_id": league,
            "RIP_text": RIP_text,
            "RIP_image_url": RIP_image_url
        }
    }

    guilds.update(guild_details)
    f.seek(0)
    json.dump(guilds, f, indent=4)
    f.close()