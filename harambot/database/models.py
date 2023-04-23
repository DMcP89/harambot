from peewee import SqliteDatabase
from peewee import Model
from peewee import TextField, IntegerField, BigIntegerField, TimestampField
from playhouse.db_url import connect
from harambot.config import settings

if "DATABASE_URL" in settings:
    database = connect(settings.database_url)
else:
    database = SqliteDatabase(":memory:")


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
    RIP_text = TextField()
    RIP_image_url = TextField()
    last_transaction_check = TimestampField()
