from aiohttp import web
from discord.ext import commands
from yahoo_fantasy_api import oauth2_logger
from harambot.config import settings

import logging

oauth2_logger.cleanup()

logger = logging.getLogger("discord.harambot.cogs.webserver")
logger.setLevel(logging.INFO)


class WebServer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def webserver(self):
        async def handler(request):
            status = f"""
            Harambot
            Harambot v{settings.version} is running!
            Bot status: {request.config_dict["bot"].status}
            Latency: {round(request.config_dict["bot"].latency * 1000)}ms
            """
            return web.Response(text=status)

        app = web.Application()
        app.router.add_get("/", handler)
        app["bot"] = self.bot
        runner = web.AppRunner(app)
        await runner.setup()
        if "PORT" in settings:
            site = web.TCPSite(runner, "0.0.0.0", settings.port)
        else:
            site = web.TCPSite(runner, "0.0.0.0", 10000)
        await self.bot.wait_until_ready()
        await site.start()
        logger.info("Webserver started on port {}".format(settings.port))
