from concurrent.futures import ThreadPoolExecutor
from harambot.config import settings
from harambot.database.models import Guild

import logging


logger = logging.getLogger("harambot.transaction_polling")
if "LOGLEVEL" in settings:
    logger.setLevel(settings.LOGLEVEL)
else:
    logger.setLevel("DEBUG")


def poll_transactions(guild: Guild):
    print(f"Polling transactions for {guild.guild_id}")


with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(poll_transactions, Guild.select())
