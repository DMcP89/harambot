import logging
import discord
import queue

from logging.handlers import QueueHandler, QueueListener
from discord.ext import commands

from harambot.cogs.meta import Meta
from harambot.cogs.misc import Misc
from harambot.cogs.yahoo import YahooCog
from harambot.cogs.webserver import WebServer
from harambot.config import settings
from harambot.database.models import Guild
from harambot.database.migrations import migrations


que = queue.Queue(-1)  # no limit on size
queue_handler = QueueHandler(que)
handler = logging.StreamHandler()
listener = QueueListener(que, handler)
listener.start()

logger = logging.getLogger("discord.harambot")
if "LOGLEVEL" in settings:
    logger.setLevel(settings.LOGLEVEL)
else:
    logger.setLevel("DEBUG")


intents = discord.Intents.default()


bot = commands.Bot(
    command_prefix="$",
    description="",
    intents=intents,
)
bot.remove_command("help")


@bot.event
async def on_ready():
    await bot.add_cog(Meta(bot))
    await bot.add_cog(YahooCog(bot, settings.yahoo_key, settings.yahoo_secret))
    await bot.add_cog(Misc(bot))
    server = WebServer(bot)
    await bot.add_cog(server)
    bot.loop.create_task(server.webserver())

    if not Guild.table_exists():
        Guild.create_table()
    if "RUN_MIGRATIONS" in settings and settings.run_migrations:
        migrations[settings.version]()
    await bot.tree.sync()
    logger.info("Everything's all ready to go~")


@bot.event
async def on_guild_join(guild):
    logger.info("Joined {}".format(guild.name))
    if not Guild.select().where(Guild.guild_id == str(guild.id)).exists():
        logger.info("Guild not configured!")


def run():
    bot.run(settings.discord_token, reconnect=True, log_handler=queue_handler)


run()
