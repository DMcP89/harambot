from dynaconf import Dynaconf
from cachetools import TTLCache

settings = Dynaconf(
    envvar_prefix=False,
    settings_files=["settings.toml", ".secrets.toml"],
    environments=True,
)

cache = TTLCache(maxsize=1024, ttl=600)
