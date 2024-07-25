from discord.ext import commands
from discord import app_commands

import discord
import logging

from harambot.ui.views import ConfigView, ReportConfigView
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
            Lets setup your guild
            1. Login into Yahoo and copy you authentication token
2. Configure harambot with your league information
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

    def webhook_permissions(interaction: discord.Interaction):
        return interaction.guild.me.guild_permissions.manage_webhooks

    def guild_is_configured(interaction: discord.Interaction):
        return (
            Guild.select()
            .where(Guild.guild_id == str(interaction.guild_id))
            .exists()
        )

    @app_commands.command(
        name="reports",
        description="Configure automatic transaction and matchup reporting",
    )
    @app_commands.check(webhook_permissions)
    @app_commands.check(guild_is_configured)
    async def reports(
        self,
        interaction: discord.Interaction,
    ):
        message = "Set what channel transaction reports should be sent to."
        await interaction.response.send_message(
            message, view=ReportConfigView(), ephemeral=True
        )

    @reports.error
    async def reports_check_error(
        self, interaction: discord.Interaction, error
    ):
        await interaction.response.send_message(
            "Grant Harambot the Manage Webhooks permission to use this command"
        )
