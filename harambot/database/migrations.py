from playhouse.migrate import SqliteMigrator, MySQLMigrator, PostgresqlMigrator
from playhouse.migrate import migrate
from peewee import PostgresqlDatabase, MySQLDatabase, SqliteDatabase
from peewee import TimestampField
from playhouse.db_url import connect
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


# Migration dictionary
migrations = {}
migrations["0.0.3-Beta"] = beta003_migrations
