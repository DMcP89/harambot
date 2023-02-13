import discord

from harambot.config import settings
from harambot.utils import YAHOO_API_URL, YAHOO_AUTH_URI
from harambot.ui.modals import ConfigModal


class YahooAuthButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.link,
            label="Login to Yahoo",
            url=f"{YAHOO_API_URL}{YAHOO_AUTH_URI}{settings.yahoo_key}",
        )


class ConfigGuildButton(discord.ui.Button):

    parent_view: None

    def __init__(self, parent_view: discord.ui.View):
        super().__init__(
            label="Configure Guild", style=discord.ButtonStyle.blurple
        )
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(
            ConfigModal(
                guild_id=str(interaction.guild_id), view=self.parent_view
            )
        )


class ConfigView(discord.ui.View):
    def __init__(
        self,
    ):
        super().__init__()
        self.add_item(YahooAuthButton())
        self.add_item(ConfigGuildButton(parent_view=self))
