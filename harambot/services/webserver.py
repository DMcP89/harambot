from aiohttp import web
from yahoo_fantasy_api import oauth2_logger
from harambot.config import settings
from harambot.database.models import Guild
from harambot.utils import yahoo_auth

import logging


oauth2_logger.cleanup()

logger = logging.getLogger("discord.harambot.services.webserver")
logger.setLevel(logging.INFO)


class WebServer:
    def __init__(self, bot):
        self.bot = bot

    async def handler(self, request):
        bot = request.config_dict["bot"]
        status = (
            f"Harambot\n"
            f"Harambot v{settings.version} is running!\n"
            f"Bot status: {bot.status}\n"
            f"Latency: {round(bot.latency * 1000)}ms"
        )
        return web.Response(text=status)

    async def guilds_handler(self, request):
        bot = request.config_dict["bot"]
        guilds = "\n".join([guild.name for guild in bot.guilds])
        return web.Response(text=guilds)

    async def config_get_handler(self, request):
        guild_id = request.match_info.get("guild_id")
        guild = Guild.get_or_none(Guild.guild_id == str(guild_id))
        if not guild:
            return web.json_response({"error": "Guild not found"}, status=404)

        return web.json_response(
            {
                "league_id": guild.league_id,
                "league_type": guild.league_type,
                "RIP_text": guild.RIP_text,
                "RIP_image_url": guild.RIP_image_url,
            }
        )

    async def config_post_handler(self, request):
        guild_id = request.match_info.get("guild_id")
        data = await request.json()
        guild = Guild.get_or_none(Guild.guild_id == str(guild_id))

        details = {
            "league_id": data.get("league_id"),
            "league_type": data.get("league_type", "").lower(),
            "RIP_text": data.get("RIP_text"),
            "RIP_image_url": data.get("RIP_image_url"),
        }

        if guild:
            Guild.update(details).where(
                Guild.guild_id == guild.guild_id
            ).execute()
            return web.json_response(
                {"message": "Configuration updated successfully."}
            )
        else:
            yahoo_token = data.get("yahoo_token")
            if not yahoo_token:
                return web.json_response(
                    {
                        "error": "Guild not found and no yahoo_token provided for creation"
                    },
                    status=404,
                )

            oauth_details = yahoo_auth(yahoo_token)
            if not oauth_details:
                return web.json_response(
                    {"error": "Failed to authenticate with Yahoo API"},
                    status=400,
                )

            details.update(oauth_details)
            guild = Guild(guild_id=str(guild_id), **details)
            guild.save()
            return web.json_response(
                {"message": "Guild created and configured successfully."}
            )

    async def webserver(self):
        app = web.Application()
        app.router.add_get("/", self.handler)
        app.router.add_get("/guilds", self.guilds_handler)
        app.router.add_get("/api/config/{guild_id}", self.config_get_handler)
        app.router.add_post("/api/config/{guild_id}", self.config_post_handler)
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
