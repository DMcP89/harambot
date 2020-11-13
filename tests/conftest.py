import pytest
from database import GuildsDatabase

@pytest.fixture()
def mock_guilds_database():
    yield  GuildsDatabase()
