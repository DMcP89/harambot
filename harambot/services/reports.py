import logging
import time

from discord import SyncWebhook
from discord.errors import NotFound

from harambot.config import settings
from harambot.database.models import Guild
from harambot.yahoo_api import Yahoo
from harambot import utils


from datetime import datetime, timedelta

logging.basicConfig()
logger = logging.getLogger("harambot.transaction_polling")
if "LOGLEVEL" in settings:
    logger.setLevel(settings.LOGLEVEL)
    logging.getLogger("discord").setLevel(settings.LOGLEVEL)
    logging.getLogger("peewee").setLevel(settings.LOGLEVEL)
else:
    logger.setLevel("DEBUG")
    logging.getLogger("discord").setLevel("DEBUG")
    logging.getLogger("peewee").setLevel("DEBUG")

logging.getLogger("yahoo_oauth").disabled = True


embed_functions_dict = {
    "add/drop": utils.create_add_drop_embed,
    "add": utils.create_add_embed,
    "drop": utils.create_drop_embed,
}


def poll_transactions(guild: Guild):
    logger.info("Polling transactions for {}".format(guild.guild_id))
    YahooAPI = Yahoo()
    ts = datetime.now() - timedelta(minutes=5)
    try:
        transactions = YahooAPI.get_transactions(
            timestamp=ts.timestamp(), guild_id=guild.guild_id
        )
        logger.info(
            "Found {} transactions for guild {}".format(
                str(len(transactions)), guild.guild_id
            )
        )
        if transactions:

            for transaction in transactions:
                embed = embed_functions_dict[transaction["type"]](transaction)
                webhook = SyncWebhook.from_url(
                    guild.transaction_polling_webhook
                )
                try:
                    webhook.send(embed=embed)
                except NotFound:
                    logger.exception(
                        "Webhook not found for {}".format(guild.guild_id)
                    )
                time.sleep(
                    1
                )  # sleep for 1 second between transactions to avoid rate limits
    except Exception:
        logger.info(
            "Error fetching transactions for {}".format(guild.guild_id)
        )


def report_service():
    logger.info("Starting transaction polling service")
    for guild in Guild.select().where(
        Guild.transaction_polling_service_enabled == 1
    ):
        poll_transactions(guild=guild)
        time.sleep(
            5
        )  # sleep for 5 seconds between each guild to avoid rate limits


if __name__ == "__main__":
    logger.info("Running Report Service")
    report_service()
    logger.info("Report Service Finished")
