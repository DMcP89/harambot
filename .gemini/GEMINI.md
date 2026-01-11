# Gemini Code Understanding

This document provides a high-level overview of the `harambot` codebase, its structure, and how to work with it.

## Project Overview

Harambot is a Python-based Discord bot that provides slash commands to interact with Yahoo Fantasy Sports leagues. It allows users to query for league standings, team rosters, player stats, trades, and more, directly from a Discord server.

The bot uses the `discord.py` library for its Discord integration and the `yahoo-fantasy-api` library to communicate with the Yahoo Fantasy Sports API. It requires API credentials for both Discord and Yahoo.

Configuration is handled by `dynaconf`, allowing settings to be managed through a `config/settings.toml` file, a `.secrets.toml` file (for sensitive data), and environment variables.

The bot persists guild-specific configurations in a database, using `peewee` as the ORM. The database connection is specified via a `DATABASE_URL`. The schema includes encrypted fields for storing sensitive authentication tokens securely.

A small `aiohttp` web server is run in the background to handle the OAuth2 callback from Yahoo during the authentication process.

## Tech Stack

-   **Language:** Python 3.10+
-   **Discord API:** `discord.py`
-   **Yahoo Fantasy API:** `yahoo-fantasy-api`, `yahoo-oauth`
-   **Database ORM:** `peewee` (supports SQLite, PostgreSQL, MySQL)
-   **Configuration:** `dynaconf`
-   **Web Server (for OAuth):** `aiohttp`
-   **Dependency Management:** `poetry`
-   **Testing:** `pytest`
-   **Code Style:** `black`, `flake8`
-   **CI/CD:** GitHub Actions, Docker

## Project Structure

-   `harambot/bot.py`: The main entry point for the bot. It initializes the bot, loads cogs, starts the web server, and connects to Discord.
-   `harambot/cogs/`: Contains the different command groups (cogs) for the bot.
    -   `yahoo.py`: The largest and most important cog, containing all commands related to Yahoo Fantasy Sports.
    -   `meta.py`: Contains meta-commands like `ping`.
    -   `misc.py`: Contains miscellaneous commands like `RIP`.
-   `harambot/yahoo_api.py`: A client class that wraps the `yahoo-fantasy-api` library, providing a simplified interface for the bot's needs.
-   `harambot/database/models.py`: Defines the Peewee database models used to store guild configurations and authentication tokens.
-   `harambot/config.py`: Sets up the `dynaconf` configuration loader.
-   `harambot/services/webserver.py`: The `aiohttp` web server used for the Yahoo OAuth2 callback.
-   `config/settings.toml`: Contains default, non-sensitive configuration values.
-   `config/example.secrets.toml`: An example file for the required secrets. A `.secrets.toml` file should be created based on this.
-   `pyproject.toml`: Defines project metadata, dependencies, and entry points (`harambot` and `harambot_reports`).
-   `Makefile`: Provides convenient commands for common development tasks like testing, running, building, and publishing.
-   `tests/`: Contains unit and integration tests.

## Configuration

The application is configured through a combination of `config/settings.toml`, `.secrets.toml`, and environment variables. The following secrets are required to run the bot:

-   `DISCORD_TOKEN`: The Discord bot token.
-   `YAHOO_KEY`: The client ID for the Yahoo API application.
-   `YAHOO_SECRET`: The client secret for the Yahoo API application.
-   `HARAMBOT_KEY`: A Fernet encryption key for the database.
-   `DATABASE_URL`: The connection string for the database (e.g., `sqlite:///harambot.db`).

## Local Development

### Running the Bot

You can run the bot locally for development using the `Makefile`.

1.  **Install dependencies:**
    ```bash
    poetry install
    ```
2.  **Set up configuration:** Create a `.secrets.toml` file in the `config/` directory or export the required environment variables (see `run-docker` in the `Makefile` for a list).
3.  **Run the bot:**
    ```bash
    make run
    ```

### Running Tests

Tests are located in the `tests/` directory and can be run with `pytest`.

```bash
make test
```

### Code Style

The project uses `black` for code formatting and `flake8` for linting, enforced by a `pre-commit` hook.

-   **Check formatting:** `black --check .`
-   **Apply formatting:** `black .`
-   **Check linting:** `flake8 .`

The `pre-commit` configuration is in `.pre-commit-config.yaml`. To install the hooks:

```bash
pre-commit install
```
