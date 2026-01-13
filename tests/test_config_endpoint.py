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
    bot.guilds = [MagicMock(name="Guild1"), MagicMock(name="Guild2")]
    bot.guilds[0].name = "Guild1"
    bot.guilds[1].name = "Guild2"
    return bot


@pytest.fixture
async def cli(aiohttp_client, mock_bot):
    settings.set("API_KEY", "test_key")
    server = WebServer(mock_bot)
    app = web.Application(middlewares=[server.auth_middleware])
    app["bot"] = mock_bot
    app.router.add_get("/", server.handler)
    app.router.add_get("/guilds", server.guilds_handler)
    app.router.add_get("/api/config/{guild_id}", server.config_get_handler)
    app.router.add_post("/api/config/{guild_id}", server.config_post_handler)
    return await aiohttp_client(app)


@pytest.mark.asyncio
async def test_get_status(cli):
    resp = await cli.get("/")
    assert resp.status == 200
    text = await resp.text()
    assert "Harambot" in text
    assert "online" in text


@pytest.mark.asyncio
async def test_get_guilds(cli):
    resp = await cli.get("/guilds")
    assert resp.status == 200
    text = await resp.text()
    assert "Guild1" in text
    assert "Guild2" in text


@pytest.mark.asyncio
async def test_api_unauthorized(cli):
    resp = await cli.get("/api/config/123")
    assert resp.status == 401
    data = await resp.json()
    assert data["error"] == "Unauthorized"


@pytest.mark.asyncio
@patch("harambot.services.webserver.Guild")
async def test_config_get_handler_success(mock_guild, cli):
    mock_guild_instance = MagicMock()
    mock_guild_instance.league_id = "12345"
    mock_guild_instance.league_type = "nfl"
    mock_guild_instance.RIP_text = "RIP"
    mock_guild_instance.RIP_image_url = "http://image.com"
    mock_guild.get_or_none.return_value = mock_guild_instance

    resp = await cli.get("/api/config/123", headers={"X-API-Key": "test_key"})
    assert resp.status == 200
    data = await resp.json()
    assert data["league_id"] == "12345"
    assert data["league_type"] == "nfl"


@pytest.mark.asyncio
@patch("harambot.services.webserver.Guild")
async def test_config_get_handler_not_found(mock_guild, cli):
    mock_guild.get_or_none.return_value = None

    resp = await cli.get("/api/config/123", headers={"X-API-Key": "test_key"})
    assert resp.status == 404
    data = await resp.json()
    assert data["error"] == "Guild not found"


@pytest.mark.asyncio
@patch("harambot.services.webserver.Guild")
async def test_config_post_handler_update_success(mock_guild, cli):
    mock_guild_instance = MagicMock()
    mock_guild_instance.guild_id = "123"
    mock_guild.get_or_none.return_value = mock_guild_instance

    resp = await cli.post(
        "/api/config/123",
        json={
            "league_id": "67890",
            "league_type": "nba",
            "RIP_text": "Updated RIP",
            "RIP_image_url": "http://newimage.com",
        },
        headers={"X-API-Key": "test_key"},
    )
    assert resp.status == 200
    data = await resp.json()
    assert data["message"] == "Configuration updated successfully."
    mock_guild.update.assert_called_once()


@pytest.mark.asyncio
@patch("harambot.services.webserver.yahoo_auth")
@patch("harambot.services.webserver.Guild")
async def test_config_post_handler_create_success(
    mock_guild, mock_yahoo_auth, cli
):
    mock_guild.get_or_none.return_value = None
    mock_yahoo_auth.return_value = {
        "access_token": "token",
        "refresh_token": "refresh",
    }

    resp = await cli.post(
        "/api/config/123",
        json={
            "league_id": "67890",
            "league_type": "nba",
            "RIP_text": "New RIP",
            "RIP_image_url": "http://newimage.com",
            "yahoo_token": "valid_token",
        },
        headers={"X-API-Key": "test_key"},
    )
    assert resp.status == 200
    data = await resp.json()
    assert data["message"] == "Guild created and configured successfully."
    mock_guild.assert_called_once()


@pytest.mark.asyncio
@patch("harambot.services.webserver.Guild")
async def test_config_post_handler_create_missing_token(mock_guild, cli):
    mock_guild.get_or_none.return_value = None

    resp = await cli.post(
        "/api/config/123",
        json={"league_id": "67890"},
        headers={"X-API-Key": "test_key"},
    )
    assert resp.status == 404
    data = await resp.json()
    assert "no yahoo_token provided" in data["error"]


@pytest.mark.asyncio
@patch("harambot.services.webserver.yahoo_auth")
@patch("harambot.services.webserver.Guild")
async def test_config_post_handler_create_auth_fail(
    mock_guild, mock_yahoo_auth, cli
):
    mock_guild.get_or_none.return_value = None
    mock_yahoo_auth.return_value = None

    resp = await cli.post(
        "/api/config/123",
        json={"league_id": "67890", "yahoo_token": "invalid_token"},
        headers={"X-API-Key": "test_key"},
    )
    assert resp.status == 400
    data = await resp.json()
    assert "Failed to authenticate" in data["error"]
