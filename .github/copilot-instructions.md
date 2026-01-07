# Harambot - GitHub Copilot Instructions

## Project Overview
Harambot is an interactive Yahoo Fantasy Sports Discord bot that allows users to interact with their Yahoo Fantasy leagues directly from Discord. The bot supports multiple fantasy sports (football, basketball, baseball, hockey) and provides real-time updates, statistics, and league management features.

## Technology Stack
- **Language**: Python 3.10+
- **Framework**: discord.py 2.5.2+ (Discord bot framework)
- **API Integration**: yahoo-fantasy-api, yahoo-oauth
- **Database**: Peewee ORM (supports SQLite, PostgreSQL, MySQL)
- **Configuration**: Dynaconf (settings.toml, .secrets.toml)
- **Encryption**: cryptography (Fernet) for storing sensitive tokens
- **Web Server**: aiohttp (for OAuth callbacks)
- **Async**: asyncio for concurrent operations

## Project Structure

### Core Modules
- **harambot/bot.py**: Main bot initialization, event handlers, cog loading
- **harambot/config.py**: Configuration management using Dynaconf
- **harambot/yahoo_api.py**: Yahoo Fantasy API wrapper and interaction layer
- **harambot/utils.py**: Shared utility functions

### Cogs (Discord Command Modules)
- **cogs/meta.py**: Meta commands (configuration, setup)
- **cogs/yahoo.py**: Yahoo Fantasy commands (standings, roster, stats, matchups, etc.)
- **cogs/misc.py**: Miscellaneous commands (ping, RIP)

### Database Layer
- **database/models.py**: Peewee ORM models (Guild, etc.)
- **database/fields.py**: Custom field types (EncryptedField)
- **database/migrations.py**: Database migration logic

### Services
- **services/webserver.py**: OAuth callback web server for Yahoo authentication
- **services/reports.py**: Transaction polling and reporting service

### UI Components
- **ui/modals.py**: Discord modals for interactive forms
- **ui/views.py**: Discord views for buttons and interactive components

## Coding Conventions

### Style Guidelines
- **Line Length**: 79 characters (Black formatter configuration)
- **Formatter**: Black (target Python 3.8+)
- **Linter**: flake8
- **Imports**: Group by stdlib, third-party, local (PEP 8)
- **Logging**: Use module-level loggers: `logger = logging.getLogger("discord.harambot.module_name")`

### Naming Conventions
- **Variables/Functions**: snake_case
- **Classes**: PascalCase
- **Constants**: UPPER_SNAKE_CASE
- **Discord Commands**: lowercase with underscores
- **Cogs**: End class names with "Cog" (e.g., YahooCog)

### Discord.py Patterns
- Use `app_commands` for slash commands
- Always defer responses for long-running operations: `await interaction.response.defer()`
- Use embeds for rich formatted responses
- Handle errors gracefully with try-except blocks
- Use Discord views and modals for interactive components

### Database Patterns
- All models inherit from `BaseModel`
- Use Peewee ORM query methods
- Encrypt sensitive data (tokens) using `EncryptedField`
- Check table existence before creating: `Model.table_exists()`
- Use `playhouse.db_url.connect()` for database connection

### API Integration
- Use `yahoo_api.py` wrapper for all Yahoo API calls
- Pass `guild_id` to API methods to fetch guild-specific credentials
- Cache API responses where appropriate using `cachetools`
- Handle API errors and rate limits gracefully

## Environment Variables & Configuration

### Required Environment Variables
```bash
DISCORD_TOKEN         # Discord bot token
YAHOO_KEY            # Yahoo API client ID
YAHOO_SECRET         # Yahoo API client secret
DATABASE_URL         # Database connection URL (e.g., sqlite:///harambot.db)
HARAMBOT_KEY         # Fernet encryption key (URL-safe base64-encoded 32-byte)
```

### Optional Environment Variables
```bash
LOGLEVEL             # Logging level (DEBUG, INFO, WARNING, ERROR)
```

### Configuration Files
- **config/settings.toml**: General settings
- **config/.secrets.toml**: Sensitive credentials (gitignored)

## Common Development Tasks

### Adding a New Discord Command
1. Add command to appropriate cog in `harambot/cogs/`
2. Use `@app_commands.command()` decorator
3. Add logging at command start
4. Defer response if operation takes >3 seconds
5. Handle errors with try-except
6. Return Discord embeds for formatted output

### Adding a New Database Model
1. Create model class in `database/models.py` inheriting from `BaseModel`
2. Add field definitions using Peewee field types
3. Use `EncryptedField` for sensitive data
4. Add migration logic if modifying existing tables
5. Create table in bot initialization if needed

### Working with Yahoo API
1. Use methods in `yahoo_api.py`
2. Pass `guild_id` for guild-specific credentials
3. Handle OAuth token refresh automatically
4. Cache responses using `@cached` decorator
5. Parse Yahoo API responses carefully (nested JSON structures)

### Creating Interactive UI
1. Define views in `ui/views.py` using `discord.ui.View`
2. Define modals in `ui/modals.py` using `discord.ui.Modal`
3. Add buttons using `discord.ui.Button`
4. Handle callbacks with async methods
5. Set appropriate timeouts for views

## Testing
- Test files located in `tests/`
- Use pytest for testing
- Mock Yahoo API responses using JSON fixtures in `tests/`
- Run tests: `pytest` or `make test`
- Coverage reports: `pytest --cov`

## Important Notes

### Security Considerations
- Always encrypt sensitive tokens using `EncryptedField`
- Never log tokens or secrets
- Validate user input for SQL injection
- Use parameterized queries (Peewee handles this)

### Discord Rate Limits
- Defer responses for long operations
- Batch API calls when possible
- Use ephemeral messages for sensitive data
- Handle rate limit errors (429 responses)

### Yahoo API Quirks
- OAuth tokens expire after 1 hour
- Refresh tokens are valid for extended periods
- API responses vary by sport type
- League IDs change per season
- Some endpoints require specific scopes

### Async/Await Patterns
- Use `async def` for Discord command handlers
- Use `await` for Discord API calls
- Use `bot.loop.create_task()` for background tasks
- Handle async errors properly

## Deployment

### Docker
- Use `docker/Dockerfile` for production
- Use `docker/Dockerfile.dev` for development
- Run with docker-compose: `docker-compose up`

### Render
- Configuration in `render.yaml`
- Automatic deployment from GitHub

### Local Development
1. Install dependencies: `poetry install`
2. Set environment variables
3. Run bot: `poetry run harambot`
4. Run reports service: `poetry run harambot_reports`

## Dependencies
Key dependencies and their purposes:
- **discord.py**: Discord bot framework
- **yahoo-fantasy-api**: Yahoo Fantasy Sports API wrapper
- **yahoo-oauth**: Yahoo OAuth2 authentication
- **peewee**: Lightweight ORM
- **dynaconf**: Configuration management
- **cryptography**: Token encryption
- **aiohttp**: Async HTTP client/server
- **cachetools**: API response caching

## Command Examples
```
/standings              - Show league standings
/roster [team]          - Show team roster
/stats [player]         - Show player statistics
/matchups [week]        - Show weekly matchups
/waiver [days]          - Show recent waiver transactions
/trade                  - Create trade approval poll
/configure              - Configure guild settings
/ping                   - Check bot latency
/RIP                    - Pay respects
```

## Architecture Patterns

### Cog Pattern
- Each major feature area is a separate Cog
- Cogs are loaded in `bot.py` on_ready event
- Commands are organized by functionality

### Service Pattern
- Background services run independently
- WebServer handles OAuth callbacks
- Reports service polls for transactions

### Configuration Pattern
- Guild-specific settings stored in database
- Bot-wide settings in settings.toml
- Secrets in .secrets.toml or environment variables

### Error Handling
- Log all errors with context
- Send user-friendly error messages
- Don't expose internal errors to users
- Use error_message constant for generic errors

## Best Practices
1. Always log command invocations with guild_id
2. Use embeds for structured output
3. Defer responses early for slow operations
4. Handle missing/None values gracefully
5. Validate guild configuration before API calls
6. Use descriptive variable names
7. Add docstrings for complex functions
8. Keep functions focused and small
9. Test with multiple sports types
10. Consider timezone differences for scheduling

## Resources
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Yahoo Fantasy API Documentation](https://developer.yahoo.com/fantasysports/guide/)
- [Project Repository](https://github.com/DMcP89/harambot)
- [Project Website](http://harambot.io)
