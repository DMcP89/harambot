from dynaconf import Dynaconf
import os

# Define the path to your configuration directory
config_path = os.path.join(os.path.dirname(__file__), '..', 'config')

settings = Dynaconf(
    envvar_prefix=False,
    settings_files=[
        os.path.join(config_path, "settings.toml"),
        os.path.join(config_path, ".secrets.toml")
    ],
    environments=True,
)
