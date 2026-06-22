import discord
import logging
import urllib.parse
from harambot.config import settings


logger = logging.getLogger("discord.harambot.views")
logger.setLevel(logging.INFO)

DISCORD_OAUTH_URL = "https://discord.com/api/oauth2/authorize?client_id={}&redirect_uri={}&response_type=token&scope={}"

class ConfigureButton(discord.ui.Button):
    def __init__(self):
        
        super().__init__(
            style=discord.ButtonStyle.link,
            label="Open harambot.io",
            url=f"{DISCORD_OAUTH_URL.format(settings.HARAMBOT_IO_CLIENT_ID, urllib.parse.quote(settings.HARAMBOT_IO_REDIRECT_URI, safe=''), urllib.parse.quote(settings.HARAMBOT_IO_SCOPES))}",
        )


class ConfigView(discord.ui.View):
    def __init__(
        self,
    ):
        super().__init__()
        self.add_item(ConfigureButton())
