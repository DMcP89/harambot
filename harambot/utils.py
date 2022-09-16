import base64
import requests
import time

from config import settings
from database.models import Guild

async def configure_guild(bot,owner, id):

    def check(m):
        return m.author == owner

    await owner.send("Thank you for adding Harambot to your server!")
    await owner.send("Please open the following link to authorize with Yahoo, respond with the code given after authorization")
    await owner.send("https://api.login.yahoo.com/oauth2/request_auth?redirect_uri=oob&response_type=code&client_id={}".format(settings.yahoo_key))
    code = await bot.wait_for('message', timeout=60, check=check)
    encoded_creds = base64.b64encode(('{0}:{1}'.format(settings.yahoo_key, settings.yahoo_secret )).encode('utf-8'))
    details = requests.post(
        url='https://api.login.yahoo.com/oauth2/get_token',
        data={"code": code.clean_content, 'redirect_uri': 'oob', 'grant_type': 'authorization_code'},
        headers = {
            'Authorization': 'Basic {0}'.format(encoded_creds.decode('utf-8')),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    ).json()
    details['token_time'] = time.time()
    await owner.send("Enter Yahoo League ID")
    leauge_id = await bot.wait_for('message', timeout=60, check=check)
    await owner.send("Enter Yahoo League Type(nfl, nhl, nba, mlb)")
    leauge_type = await bot.wait_for('message', timeout=60, check=check)
    await owner.send("Enter text to use with $RIP command")
    RIP_text = await bot.wait_for('message', timeout=60, check=check)
    await owner.send("Enter image url to use with $RIP command")
    RIP_image_url = await bot.wait_for('message', timeout=60, check=check)
    details["league_id"] = leauge_id.clean_content
    details["league_type"] = leauge_type.clean_content
    details["RIP_text"] = RIP_text.clean_content
    details["RIP_image_url"] = RIP_image_url.clean_content
    Guild.create(guild_id=id,**details)
    return