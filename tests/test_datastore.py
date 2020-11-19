from _pytest.outcomes import fail
import pytest
from datastore import GuildsDatastore


@pytest.fixture
def guilds_datastore():
    return GuildsDatastore("tests/test-guilds.json")

def test_init(guilds_datastore):
    assert guilds_datastore is not None

def test_getGuildDetails(guilds_datastore):
    guild_details = guilds_datastore.getGuildDetails("1234567890")
    assert guild_details is not None
    assert guild_details["access_token"] == "test_access_token"
    assert guild_details["guid"] == "test_guid"
    assert guild_details["refresh_token"] == "test_refresh_token"
    assert guild_details["token_time"] == 0.0
    assert guild_details["token_type"] == "bearer"
    assert guild_details["league_id"] == "123456"


def test_refreshDatastore(guilds_datastore):
    previous_refresh = guilds_datastore.last_refresh_timestamp
    guilds_datastore.refreshDatastore()
    assert guilds_datastore.last_refresh_timestamp > previous_refresh