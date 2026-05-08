from harambot.handlers.yahoo_api import Yahoo
from harambot.database.models import Guild

handlers = {
    "yahoo": Yahoo(),
}


def get_handler(guild_id):
    guild = Guild.get_or_none(Guild.guild_id == str(guild_id))
    if guild:
        return handlers.get(guild.league_provider)
    return None
