# The Config Endpoint
 
 The Config Endpoint is used to configure guilds for Harambot via REST API calls instead of through commands in Discord. Functionally it performs the same logic as the `on_submit` function of the `ConfigModal` in `harambot/ui/modals.py`, minus the Discord-specific interactions.

## Endpoint

 The endpoint is located at `/api/config/<guild_id>` and supports both GET and POST methods.

 ## GET Method
The GET method retrieves the current configuration for the specified guild. It requires the `guild_id` as a URL parameter.

**Example Request:**
```
GET /api/config/123456789012345678
```

**Example Response (Success):**
```json
{
    "league_id": "1234456",
    "league_type": "nfl",
    "RIP_text": "RIP Harambe",
    "RIP_image_url": "https://example.com/harambe.png"
}
```

**Example Response (Not Found):**
```json
{
    "error": "Guild not found"
}
```

## POST Method
The POST method updates the configuration for an existing guild or creates a new one. It requires the `guild_id` as a URL parameter and a JSON body containing the configuration fields.

### Updating an Existing Guild
If the guild is already configured, the provided fields will be updated.

**Example Request:**
```json
{
    "league_id": "6543210",
    "league_type": "nba",
    "RIP_text": "Remembering Harambe",
    "RIP_image_url": "https://example.com/new_harambe.png"
}
```

**Example Response:**
```json
{
    "message": "Configuration updated successfully."
}
```

### Creating a New Guild
If the guild does not exist, a `yahoo_token` must be provided in the JSON body to authenticate with the Yahoo API and initialize the guild.

**Example Request:**
```json
{
    "league_id": "6543210",
    "league_type": "nba",
    "RIP_text": "Remembering Harambe",
    "RIP_image_url": "https://example.com/new_harambe.png",
    "yahoo_token": "your_yahoo_auth_token_here"
}
```

**Example Response (Success):**
```json
{
    "message": "Guild created and configured successfully."
}
```

**Example Response (Missing Token for New Guild):**
```json
{
    "error": "Guild not found and no yahoo_token provided for creation"
}
```

**Example Response (Authentication Failure):**
```json
{
    "error": "Failed to authenticate with Yahoo API"
}
```