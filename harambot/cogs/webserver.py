from aiohttp import web
from discord.ext import commands
from harambot.config import settings

import logging

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class WebServer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def webserver(self):
        async def handler(request):
            return web.Response(text=f"Harambot v{settings.version}")

        app = web.Application()
        app.router.add_get("/", handler)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", settings.port)
        await self.bot.wait_until_ready()
        await site.start()
        logger.info("Webserver started on port {}".format(settings.port))
