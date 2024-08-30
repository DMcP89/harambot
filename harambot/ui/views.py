import discord
import logging

from harambot.config import settings
from harambot.utils import YAHOO_API_URL, YAHOO_AUTH_URI, get_avatar_bytes
from harambot.ui.modals import ConfigModal
from harambot.database.models import Guild

logger = logging.getLogger("discord.harambot.views")
logger.setLevel(logging.INFO)


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


class ResetButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.danger, label="Reset")

    async def callback(self, interaction: discord.Interaction):
        if (
            Guild.select()
            .where(Guild.guild_id == str(interaction.guild.id))
            .exists()
        ):
            guild = Guild.get(Guild.guild_id == str(interaction.guild.id))
            guild.delete_instance()
            await interaction.response.send_message(
                "Guild configuration reset!"
            )
        else:
            await interaction.response.send_message("Guild not configured!")


class ConfigView(discord.ui.View):
    def __init__(
        self,
    ):
        super().__init__()
        self.add_item(YahooAuthButton())
        self.add_item(ConfigGuildButton(parent_view=self))
        self.add_item(ResetButton())


class ReportConfigView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.select(
        cls=discord.ui.ChannelSelect, channel_types=[discord.ChannelType.text]
    )
    async def select_channels(
        self,
        interaction: discord.Interaction,
        select: discord.ui.ChannelSelect,
    ):

        guild = Guild.get(Guild.guild_id == str(interaction.guild.id))

        channel = select.values[0].resolve()
        if not channel:
            channel = select.values[0].fetch()

        for webhook in await channel.webhooks():
            if webhook.user == interaction.guild.me:
                guild.transaction_polling_webhook = webhook.url
                guild.save()
                return await interaction.response.send_message(
                    f"Reports configured to go to {select.values[0].mention}"
                )

        if guild.transaction_polling_service_enabled == 0:
            guild.transaction_polling_service_enabled = 1
        else:
            try:
                webhook = discord.SyncWebhook.from_url(
                    guild.transaction_polling_webhook
                )
                webhook.delete()
            except discord.errors.NotFound:
                logger.info("Webhook not found")
            guild.transaction_polling_webhook = None

        if not guild.transaction_polling_webhook:
            webhook = await channel.create_webhook(
                name="Harambot Reports", avatar=get_avatar_bytes()
            )
            guild.transaction_polling_webhook = webhook.url

        guild.save()

        return await interaction.response.send_message(
            f"Reports configured to go to {select.values[0].mention}"
        )
