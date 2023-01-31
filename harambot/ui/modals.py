import discord

from discord.utils import MISSING
from typing import Optional
from harambot.database.models import Guild


class ConfigModal(discord.ui.Modal, title="Configure Guild"):

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

    def __init__(
        self,
        *,
        title: str = MISSING,
        timeout: Optional[float] = None,
        custom_id: str = MISSING,
        guild: Guild = None,
    ) -> None:
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)
        self.guild = guild
        self.league_id.default = guild.league_id
        self.league_type.default = guild.league_type
        self.RIP_text.default = guild.RIP_text
        self.RIP_image_url.default = guild.RIP_image_url

    async def on_submit(self, interaction: discord.Interaction):
        details = {
            "league_id": self.league_id.value,
            "league_type": self.league_type.value,
            "RIP_text": self.RIP_text.value,
            "RIP_image_url": self.RIP_image_url.value,
        }
        Guild.update(details).where(
            Guild.guild_id == self.guild.guild_id
        ).execute()
        await interaction.response.send_message(
            "Guild settings updated!",
            ephemeral=True,
        )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.response.send_message(
            "Oops! Something went wrong with configuring your guild.\
             Please try again",
            ephemeral=True,
        )
