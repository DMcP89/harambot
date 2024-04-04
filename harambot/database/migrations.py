from playhouse.migrate import SqliteMigrator, MySQLMigrator, PostgresqlMigrator
from playhouse.migrate import migrate
from playhouse.dataset import DataSet
from peewee import PostgresqlDatabase, MySQLDatabase, SqliteDatabase
from peewee import TimestampField
from playhouse.db_url import connect
from cryptography.fernet import Fernet


from harambot.config import settings

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
    print("Running beta040 migrations")
    f = Fernet(settings.HARAMBOT_KEY)
    if "DATABASE_URL" in settings:
        dataSet = DataSet(settings.database_url)
    else:
        dataSet = DataSet(":memory:")
    guilds = dataSet["guild"]
    for guild in guilds.all():
        print(guild["id"])
        dataSet.query(
            sql="UPDATE guild SET access_token = ? WHERE id = ?",
            params=[
                f.encrypt(guild["access_token"].encode()).decode(),
                guild["id"],
            ],
        )
        dataSet.query(
            sql="UPDATE guild SET refresh_token = ? WHERE id = ?",
            params=[
                f.encrypt(guild["refresh_token"].encode()).decode(),
                guild["id"],
            ],
        )


# Migration dictionary
migrations = {}
migrations["0.0.3-Beta"] = beta003_migrations
migrations["0.4.0-Beta"] = beta040_migrations
