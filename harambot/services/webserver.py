from aiohttp import web, ClientSession
import aiohttp_cors
from yahoo_fantasy_api import oauth2_logger
from harambot.config import settings
from harambot.database.models import Guild
from harambot.utils import yahoo_auth
from harambot.yahoo_api import Yahoo

import logging


oauth2_logger.cleanup()

logger = logging.getLogger("discord.harambot.services.webserver")
logger.setLevel(logging.INFO)

yahoo_api = Yahoo()

DISCORD_API_BASE_URL = "https://discord.com/api/v10"
DISCORD_USER_GUILDS_ENDPOINT = f"{DISCORD_API_BASE_URL}/users/@me/guilds"

class WebServer:
    def __init__(self, bot):
        self.bot = bot

    async def status_handler(self, request):
        bot = request.config_dict["bot"]
        status = (
            f"Harambot\n"
            f"Harambot v{settings.version} is running!\n"
            f"Bot status: {bot.status}\n"
            f"Latency: {round(bot.latency * 1000)}ms"
        )
        return web.Response(text=status)


    async def config_get_handler(self, request):
        logger.info(f"Received config GET request for guild_id: {request.match_info.get('guild_id')}")
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

    async def scoreboard_handler(self, request):
        guild_id = request.match_info.get("guild_id")
        matchups = yahoo_api.get_matchups(guild_id=guild_id)
        if matchups is None:
            return web.json_response(
                {"error": "Guild not found or Yahoo API error"}, status=404
            )
        return web.json_response({"matchups": matchups})

    @web.middleware
    async def auth_middleware(self, request, handler):
        if request.method == "OPTIONS":
            return await handler(request)
        if request.path.startswith("/api/"):
            api_key = request.headers.get("X-Api-Key")
            if not api_key or api_key != settings.api_key:
                return web.json_response({"error": "Unauthorized"}, status=401)
        return await handler(request)

    @web.middleware
    async def guild_auth_middleware(self, request, handler):
        if request.method == "OPTIONS":
            return await handler(request)
        if request.path.startswith("/api/"):
            discord_user_token = request.headers.get("Discord-Token")
            guild_id = request.match_info.get("guild_id")
            if not discord_user_token:
                return web.json_response({"error": "Unauthorized"}, status=403)
            if not guild_id:
                return web.json_response({"error": "Guild ID is required"}, status=400)

            # Make a request to Discord API to get the user's guilds and check if they are an admin in the guild specified by guild_id
            aiohttp_client = ClientSession() 
            async with aiohttp_client.get(
                DISCORD_USER_GUILDS_ENDPOINT,
                headers={"Authorization": f"Bearer {discord_user_token}"},
            ) as resp:
                if resp.status != 200:
                    return web.json_response({"error": "Unauthorized"}, status=403)
                guilds = await resp.json()
                if not any(
                    guild["id"] == guild_id and (int(guild["permissions"]) & 0x20 == 0x20)
                    for guild in guilds
                ):
                    return web.json_response({"error": "Forbidden: Admins only"}, status=403)
        return await handler(request)

    async def webserver(self):
        app = web.Application(middlewares=[self.auth_middleware, self.guild_auth_middleware])
        cors = aiohttp_cors.setup(
            app,
            defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                    allow_methods=("GET", "POST", "OPTIONS"),
                )
            },
        )

        routes = [
            app.router.add_get("/status", self.status_handler),
            app.router.add_get(
                "/api/config/{guild_id}", self.config_get_handler
            ),
            app.router.add_post(
                "/api/config/{guild_id}", self.config_post_handler
            ),
            app.router.add_get(
                "/api/scoreboard/{guild_id}", self.scoreboard_handler
            ),
        ]

        for route in routes:
            cors.add(route)

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
