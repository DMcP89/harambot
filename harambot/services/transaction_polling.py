from concurrent.futures import ThreadPoolExecutor
from playhouse.shortcuts import model_to_dict
from yahoo_oauth import OAuth2
from discord import SyncWebhook

from harambot.config import settings
from harambot.database.models import Guild
from harambot.yahoo_api import Yahoo
from harambot import utils

import logging
import random
import time


logger = logging.getLogger("harambot.transaction_polling")
if "LOGLEVEL" in settings:
    logger.setLevel(settings.LOGLEVEL)
else:
    logger.setLevel("DEBUG")

logging.getLogger("yahoo_oauth").disabled = True

embed_functions_dict = {
    "add/drop": utils.create_add_drop_embed,
    "add": utils.create_add_embed,
    "drop": utils.create_drop_embed,
}


def poll_transactions(guild: Guild):
    random_int = random.randint(1, 20)
    YahooAPI = Yahoo(
        OAuth2(
            settings.yahoo_key,
            settings.yahoo_secret,
            store_file=False,
            **model_to_dict(guild),
        ),
        guild.league_id,
        guild.league_type,
    )
    transactions = YahooAPI.get_latest_waiver_transactions()
    if transactions:
        for transaction in transactions:
            embed = embed_functions_dict[transaction["type"]](transaction)
            webhook = SyncWebhook.from_url(guild.webhook_url)
            webhook.send(embed=embed)
    time.sleep(random_int)
    print(len(transactions))


with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(poll_transactions, Guild.select()))
