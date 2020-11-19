import logging
import time
import json


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.disable(logging.DEBUG)


class GuildsDatastore():

    def __init__(self, path_to_datastore):
        self.path_to_datastore = path_to_datastore
        self.refreshDatastore()

    def getGuildDetails(self,guild_id):
        return self.guilds[str(guild_id)]

    def refreshDatastore(self):
        with open(self.path_to_datastore, 'r') as f:
            self.guilds = json.load(f)
            f.close()
        self.last_refresh_timestamp = time.time()