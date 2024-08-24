import logging

from playhouse.migrate import SqliteMigrator, MySQLMigrator, PostgresqlMigrator
from playhouse.migrate import migrate
from playhouse.dataset import DataSet
from peewee import PostgresqlDatabase, MySQLDatabase, SqliteDatabase
from peewee import TimestampField, IntegerField, TextField
from playhouse.db_url import connect
from cryptography.fernet import Fernet


from harambot.config import settings

logger = logging.getLogger("discord")
logger.setLevel(settings.LOGLEVEL)


if "DATABASE_URL" in settings:
    database = connect(settings.database_url)
else:
    database = SqliteDatabase(":memory:")

# Get migrator
migrator = None
if isinstance(database, MySQLDatabase):
    migrator = MySQLMigrator(database)
elif isinstance(database, PostgresqlDatabase):
    migrator = PostgresqlMigrator(database)
else:
    migrator = SqliteMigrator(database)


# Migration Functions
def beta003_migrations():
    last_transaction_check = TimestampField()
    migrate(
        migrator.add_column(
            "guild", "last_transaction_check", last_transaction_check
        )
    )


def beta040_migrations():
    # Encrypt token fields
    f = Fernet(settings.HARAMBOT_KEY)
    if "DATABASE_URL" in settings:
        dataSet = DataSet(settings.database_url)
    else:
        dataSet = DataSet(":memory:")
    guilds = dataSet["guild"]
    for guild in guilds.all():
        logger.info(
            "Encrypted token: "
            + "'{}'".format(f.encrypt(guild["access_token"].encode()).decode())
        )
        logger.info("Guild ID:")
        logger.info(guild["id"])
        with dataSet.transaction() as txn:
            guilds.update(
                id=guild["id"],
                access_token=f.encrypt(
                    guild["access_token"].encode()
                ).decode(),
                columns=["id"],
            )
            guilds.update(
                id=guild["id"],
                refresh_token=f.encrypt(
                    guild["refresh_token"].encode()
                ).decode(),
                columns=["id"],
            )
            txn.commit()
    # Add new fields for transaction polling
    transaction_polling_service_enabled = IntegerField(default=0)
    transaction_polling_webhook = TextField(null=True)
    migrate(
        migrator.add_column(
            "guild",
            "transaction_polling_service_enabled",
            transaction_polling_service_enabled,
        ),
        migrator.add_column(
            "guild",
            "transaction_polling_webhook",
            transaction_polling_webhook,
        ),
    )


# Migration dictionary
migrations = {}
migrations["0.0.3-Beta"] = beta003_migrations
migrations["0.4.0-Beta"] = beta040_migrations
