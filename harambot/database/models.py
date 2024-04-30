import logging

from peewee import SqliteDatabase
from peewee import Model
from peewee import TextField, IntegerField, BigIntegerField, TimestampField
from playhouse.db_url import connect
from harambot.config import settings
from harambot.database.fields import EncryptedField

logger = logging.getLogger("peewee")
logger.setLevel(settings.LOGLEVEL)

if "DATABASE_URL" in settings:
    database = connect(settings.database_url)
else:
    logger.info("Using in-memory database")
    database = SqliteDatabase(":memory:")


class BaseModel(Model):
    class Meta:
        database = database


class Guild(BaseModel):
    guild_id = TextField(unique=True)
    access_token = EncryptedField(key=settings.HARAMBOT_KEY)
    refresh_token = EncryptedField(key=settings.HARAMBOT_KEY)
    expires_in = IntegerField()
    token_type = TextField()
    xoauth_yahoo_guid = TextField(null=True)
    token_time = BigIntegerField()
    league_id = TextField()
    league_type = TextField()
    RIP_text = TextField()
    RIP_image_url = TextField()
    transaction_polling_service_enabled = IntegerField(default=0)
    transaction_polling_webhook = TextField(null=True)
    last_transaction_check = TimestampField()
