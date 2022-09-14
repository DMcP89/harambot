from os.path import exists

from peewee import *
from config import settings


if settings.guilds_datastore_type == "postgres":
    database = PostgresqlDatabase()
else:
    database = SqliteDatabase(settings.guilds_datastore_loc)


class BaseModel(Model):
    class Meta:
        database = database


class Guild(BaseModel):
    guild_id = TextField(unique=True)
    access_token = TextField()
    refresh_token = TextField()
    expires_in = IntegerField()
    token_type = TextField()
    xoauth_yahoo_guid = TextField()
    token_time = BigIntegerField()
    league_id = TextField()
    league_type = TextField()
    RIP_text   = TextField()
    RIP_image_url = TextField()

