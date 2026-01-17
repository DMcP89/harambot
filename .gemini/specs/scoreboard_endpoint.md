# Scoreboard Endpoint
This is an endpoint for pulling the current scoreboard data for a specified guild. It leverages the get_matchups function from the yahoo_api module to fetch scoreboard information.

## Authentication
All requests to the `/api/` endpoints must include an `X-API-Key` header with a valid API key.

**Example Header:**
```
X-API-Key: your_api_key_here
```

## Endpoint

 The endpoint is located at `/api/scoreboard/<guild_id>` and supports the GET method.

## GET Method
The GET method retrieves the current scoreboard for the specified guild. It requires the `guild_id` as a URL parameter. 

**Example Request:**
```
GET /api/scoreboard/123456789012345678
```
