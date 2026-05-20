from discord.ext import commands
from discord import app_commands

import discord
import logging

from harambot.ui.views import ConfigView
from harambot.database.models import Guild


logger = logging.getLogger("discord.harambot.cogs.meta")
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
            name="/waivers days",
            value="Returns the waiver wire transactions for the previous number of days",
            inline=False,
        )
        embed.add_field(
            name="/configure",
            value="Configure your guild for Harambot",
            inline=False,
        )
        embed.add_field(
            name="/reports",
            value="Configure automatic transaction and matchup reporting",
            inline=False,
        )
        embed.add_field(
            name="/league",
            value="Set which league harambot should use for commands",
            inline=False,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="ping", description="Gives the latency of harambot"
    )
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(self.bot.latency)

    @app_commands.command(
        name="configure",
        description="Configure your guild for Harambot",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def configure(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            """
            Configure your guild on harambot.io
            """,
            view=ConfigView(),
            ephemeral=True,
        )

    @configure.error
    async def configure_check_error(
        self, interaction: discord.Interaction, error
    ):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "You do not have the required permissions to run this command."
            )
        else:
            logger.error(f"Error in configure command: {error}")
            await interaction.response.send_message(
                "An error occurred while running the configure command. Please check the logs.",
                ephemeral=True,
            )
