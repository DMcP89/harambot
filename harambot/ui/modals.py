import discord
import logging

from discord.utils import MISSING
from typing import Optional
from harambot.database.models import Guild
from harambot.utils import yahoo_auth

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class ConfigModal(discord.ui.Modal, title="Configure Guild"):

    yahoo_token = discord.ui.TextInput(
        label="Yahoo Token",
        placeholder="Enter the token from the Yahoo login link",
    )

    league_id = discord.ui.TextInput(
        label="Yahoo League ID", placeholder="Enter Yahoo League ID"
    )
    league_type = discord.ui.TextInput(
        label="Yahoo League Type",
        placeholder="Enter Yahoo League Type(nfl, nhl, nba, mlb)",
    )
    RIP_text = discord.ui.TextInput(
        label="RIP command text",
        placeholder="Enter text to use with $RIP command",
    )
    RIP_image_url = discord.ui.TextInput(
        label="RIP Image",
        placeholder="Enter image url to use with $RIP command",
    )

    guild = None
    view = None

    def __init__(
        self,
        *,
        title: str = MISSING,
        timeout: Optional[float] = None,
        custom_id: str = MISSING,
        guild_id: str = None,
        view: discord.ui.View = None,
    ) -> None:
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)
        self.view = view
        self.guild = Guild.get_or_none(Guild.guild_id == str(guild_id))
        if self.guild:
            self.remove_item(self.yahoo_token)
            self.league_id.default = self.guild.league_id
            self.league_type.default = self.guild.league_type
            self.RIP_text.default = self.guild.RIP_text
            self.RIP_image_url.default = self.guild.RIP_image_url

    async def on_submit(self, interaction: discord.Interaction):
        details = {
            "league_id": self.league_id.value,
            "league_type": self.league_type.value,
            "RIP_text": self.RIP_text.value,
            "RIP_image_url": self.RIP_image_url.value,
        }
        if self.guild:
            Guild.update(details).where(
                Guild.guild_id == self.guild.guild_id
            ).execute()
        else:
            details.update(yahoo_auth(self.yahoo_token.value))
            self.guild = Guild(guild_id=str(interaction.guild_id), **details)
            self.guild.save()
        await interaction.response.send_message(
            "Guild settings updated!",
            ephemeral=True,
        )
        self.view.stop()

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        logger.exception(error)
        await interaction.response.send_message(
            "Oops! Something went wrong with configuring your guild.\
             Please try again",
            ephemeral=True,
        )
