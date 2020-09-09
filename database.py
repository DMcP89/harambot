import logging
import os
import json


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.disable(logging.DEBUG)


class GuildsDatabase():

    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(dir_path+'/guilds.json', 'r') as f:
            self.guilds = json.load(f)
            f.close()

    def getGuildDetails(self,guild_id):
        return self.guilds[str(guild_id)]

    def refreshGuildDatabase(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(dir_path+'/guilds.json', 'r') as f:
            self.guilds = json.load(f)
            f.close()