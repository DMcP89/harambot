import pytest
from aiohttp import web
from harambot.services.webserver import WebServer
from unittest.mock import MagicMock, patch
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
    app = web.Application(middlewares=[server.auth_middleware])
    app["bot"] = mock_bot
    app.router.add_get("/api/scoreboard/{guild_id}", server.scoreboard_handler)
    return await aiohttp_client(app)

@pytest.mark.asyncio
async def test_scoreboard_unauthorized(cli):
    resp = await cli.get("/api/scoreboard/123")
    assert resp.status == 401
    data = await resp.json()
    assert data["error"] == "Unauthorized"

@pytest.mark.asyncio
@patch("harambot.services.webserver.yahoo_api")
async def test_scoreboard_success(mock_yahoo_api, cli):
    mock_yahoo_api.get_matchups.return_value = ("1", [{"name": "Team A vs Team B", "value": "Details"}])
    
    resp = await cli.get("/api/scoreboard/123", headers={"X-API-Key": "test_key"})
    assert resp.status == 200
    data = await resp.json()
    assert data["week"] == "1"
    assert len(data["matchups"]) == 1
    assert data["matchups"][0]["name"] == "Team A vs Team B"

@pytest.mark.asyncio
@patch("harambot.services.webserver.yahoo_api")
async def test_scoreboard_guild_not_found_or_error(mock_yahoo_api, cli):
    mock_yahoo_api.get_matchups.return_value = None
    
    resp = await cli.get("/api/scoreboard/123", headers={"X-API-Key": "test_key"})
    assert resp.status == 404
    data = await resp.json()
    assert "error" in data
