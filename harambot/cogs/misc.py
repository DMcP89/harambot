import discord
import logging

from discord.ext import commands
from discord import app_commands
from typing import Optional
from harambot.database.models import Guild

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rip", description="Pay respects to Harambe")
    @app_commands.describe(deceased="Who you are paying respects to")
    async def rip(
        self, interaction: discord.Interaction, deceased: Optional[str] = None
    ):

        logger.info("RIP called")
        guild = Guild.get(Guild.guild_id == str(interaction.guild_id))
        message = guild.RIP_text + " " + (deceased if deceased else "Harambe")
        embed = discord.Embed(title="", description="", color=0xEEE657)
        embed.set_image(url=guild.RIP_image_url)
        await interaction.response.send_message(content=message, embed=embed)
