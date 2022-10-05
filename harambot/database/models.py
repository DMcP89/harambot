from peewee import *
from playhouse.db_url import connect
from config import settings
from database.databasetype import DatabaseType

if settings.guilds_datastore_type == DatabaseType.POSTGRES.value:
    database = PostgresqlDatabase(settings.guild_db,user=settings.guild_db_user, password=settings.guild_db_pass,
                                    host=settings.guild_db_host, port=settings.guild_db_port)
elif settings.guilds_datastore_type == DatabaseType.MYSQL.value:
    database = MySQLDatabase(settings.guild_db,user=settings.guild_db_user, password=settings.guild_db_pass,
                                    host=settings.guild_db_host, port=settings.guild_db_port)
elif settings.guilds_datastore_type == DatabaseType.SQLITE.value:
    database = SqliteDatabase(settings.guilds_datastore_loc)
else:
    database = SqliteDatabase(':memory:')

if settings.database_url:
    database = connect(settings.database_url)

class BaseModel(Model):
    class Meta:
        database = database


class Guild(BaseModel):
    guild_id = TextField(unique=True)
    access_token = TextField()
    refresh_token = TextField()
    expires_in = IntegerField()
    token_type = TextField()
    xoauth_yahoo_guid = TextField(null=True)
    token_time = BigIntegerField()
    league_id = TextField()
    league_type = TextField()
    RIP_text   = TextField()
    RIP_image_url = TextField()

