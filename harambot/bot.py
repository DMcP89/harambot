import logging
import discord


from discord.ext import commands
from harambot.cogs.meta import Meta
from harambot.cogs.misc import Misc
from harambot.cogs.yahoo import YahooCog
from harambot.config import settings
from harambot.database.models import Guild
from harambot.database.migrations import migrations

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("harambot.py")
if "LOGLEVEL" in settings:
    logger.setLevel(settings.loglevel)
else:
    logger.setLevel("INFO")

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="$", description="", intents=intents)
bot.remove_command("help")


@bot.event
async def on_ready():
    await bot.add_cog(Meta(bot))
    await bot.add_cog(YahooCog(bot, settings.yahoo_key, settings.yahoo_secret))
    await bot.add_cog(Misc(bot))
    if not Guild.table_exists():
        Guild.create_table()
    if "RUN_MIGRATIONS" in settings and settings.run_migrations:
        migrations[settings.version]()
    for guild in bot.guilds:
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
    logger.info("Everything's all ready to go~")


@bot.event
async def on_guild_join(guild):
    logger.info("Joined {}".format(guild.name))
    if not Guild.select().where(Guild.guild_id == str(guild.id)).exists():
        logger.info("Guild not configured!")
        await guild.owner.send(
            """Thank you for adding Harambot to your server!
        Please complete your setup by running the /configure command!"""
        )


def run():
    bot.run(settings.discord_token, reconnect=True)


run()
