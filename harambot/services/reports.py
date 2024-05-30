from multiprocessing import Pool
from playhouse.shortcuts import model_to_dict
from yahoo_oauth import OAuth2
from discord import SyncWebhook

from harambot.config import settings
from harambot.database.models import Guild
from harambot.yahoo_api import Yahoo
from harambot import utils

import logging
from datetime import datetime, timedelta


logger = logging.getLogger("harambot.transaction_polling")
if "LOGLEVEL" in settings:
    logger.setLevel(settings.LOGLEVEL)
    logging.getLogger("discord").setLevel(settings.LOGLEVEL)
else:
    logger.setLevel("DEBUG")
    logging.getLogger("discord").setLevel("DEBUG")

logging.getLogger("yahoo_oauth").disabled = True


embed_functions_dict = {
    "add/drop": utils.create_add_drop_embed,
    "add": utils.create_add_embed,
    "drop": utils.create_drop_embed,
}


def poll_transactions(guild: Guild):
    logger.info("Polling transactions for {}".format(guild.guild_id))
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
    ts = datetime.now() - timedelta(days=160)
    transactions = YahooAPI.get_transactions(timestamp=ts.timestamp())
    if transactions:
        for transaction in transactions:
            embed = embed_functions_dict[transaction["type"]](transaction)
            webhook = SyncWebhook.from_url(guild.transaction_polling_webhook)
            webhook.send(embed=embed)


def report_service():
    logger.info("Starting transaction polling service")
    with Pool(settings.REPORT_EXECUTORS) as executor:
        executor.map(
            poll_transactions,
            Guild.select().where(
                Guild.transaction_polling_service_enabled == 1
            ),
        )


if __name__ == "__main__":
    report_service()
