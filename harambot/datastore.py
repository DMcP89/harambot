import logging
import time
import json

from os.path import exists

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.disable(logging.DEBUG)


class GuildsDatastore():

    def __init__(self, path_to_datastore):
        self.path_to_datastore = path_to_datastore
        if not exists(path_to_datastore):
            with open(path_to_datastore, 'w+') as f:
                f.write("{}")
                f.close
        self.refreshDatastore()

    def getGuildDetails(self,guild_id):
        if guild_id in self.guilds:
            return self.guilds[str(guild_id)]
        else:
            return None

    def refreshDatastore(self):
        with open(self.path_to_datastore, 'r') as f:
            self.guilds = json.load(f)
            f.close()
        self.last_refresh_timestamp = time.time()

    def addGuildToDatastore(self, guild_details):
        with open(self.path_to_datastore, 'r+') as f:
            self.guilds = json.load(f)
            self.guilds.update(guild_details)
            f.seek(0)
            json.dump(self.guilds, f, indent=4)
            f.close
