from discord.ext import commands
from discord import app_commands

import discord
import logging

from harambot.ui.views import ConfigView

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class Meta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="View available commands")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Harambot",
            description="Yahoo Fantasy Sports Bot for Discord",
            color=0xEEE657,
        )
        embed.add_field(
            name="/ping", value="Gives the latency of harambot", inline=False
        )
        embed.add_field(
            name="/rip", value="Pay respects to Harambe", inline=False
        )
        embed.add_field(
            name="/standings",
            value="Returns the current standings of your league",
            inline=False,
        )
        embed.add_field(
            name="/roster team_name",
            value="Returns the roster of the given team",
            inline=False,
        )
        embed.add_field(
            name="/stats player_name",
            value="Returns the details of the given player",
            inline=False,
        )
        embed.add_field(
            name="/trade",
            value="Create poll for latest trade for league approval",
            inline=False,
        )
        embed.add_field(
            name="/matchups",
            value="Returns the current weeks matchups",
            inline=False,
        )
        embed.add_field(
            name="/wavier",
            value="Returns the waiver wire transactions for the last 24 hours",
            inline=False,
        )
        embed.add_field(
            name="/configure",
            value="Configure your guild for Harambot",
            inline=False,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="ping", description="Gives the latency of harambot"
    )
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(self.bot.latency)

    @app_commands.command(
        name="configure", description="Configure your guild for Harambot"
    )
    async def configure(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            """
            Lets setup your guild
            1. Login into Yahoo and copy you authentication token
2. Configure harambot with your league information
            """,
            view=ConfigView(),
            ephemeral=True,
        )
