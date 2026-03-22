import pytest
import aiohttp_cors
from aiohttp import web
from harambot.services.webserver import WebServer
from unittest.mock import MagicMock
from harambot.config import settings

@pytest.fixture
def mock_bot():
    bot = MagicMock()
    bot.status = "online"
    bot.latency = 0.05
    return bot

@pytest.fixture
async def cli(aiohttp_client, mock_bot):
    settings.set("API_KEY", "test_key")
    server = WebServer(mock_bot)
    app = web.Application(
        middlewares=[server.auth_middleware]
    )
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods=("GET", "POST", "OPTIONS"),
        )
    })
    app["bot"] = mock_bot
    status_route = app.router.add_get("/status", server.status_handler)
    config_get_route = app.router.add_get("/api/config/{guild_id}", server.config_get_handler)
    
    cors.add(status_route)
    cors.add(config_get_route)
    return await aiohttp_client(app)

@pytest.mark.asyncio
async def test_cors_options(cli):
    resp = await cli.options(
        "/api/config/123",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-API-Key",
        },
    )
    assert resp.status == 200
    assert "Access-Control-Allow-Origin" in resp.headers
    assert "Access-Control-Allow-Methods" in resp.headers
    assert "Access-Control-Allow-Headers" in resp.headers


@pytest.mark.asyncio
async def test_cors_get_with_auth(cli):
    from unittest.mock import patch

    with patch("harambot.services.webserver.Guild") as mock_guild:
        mock_guild_instance = MagicMock()
        mock_guild_instance.league_id = "12345"
        mock_guild_instance.league_type = "nfl"
        mock_guild_instance.RIP_text = "RIP"
        mock_guild_instance.RIP_image_url = "http://image.com"
        mock_guild.get_or_none.return_value = mock_guild_instance

        resp = await cli.get(
            "/api/config/123",
            headers={"X-API-Key": "test_key", "Origin": "http://example.com"},
        )
        assert resp.status == 200
        assert resp.headers["Access-Control-Allow-Origin"] == "http://example.com"
        data = await resp.json()
        assert data["league_id"] == "12345"
