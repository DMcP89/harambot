import base64
import requests
import time

from harambot.config import settings

YAHOO_API_URL = "https://api.login.yahoo.com/oauth2/"
YAHOO_AUTH_URI = "request_auth?redirect_uri=oob&response_type=code&client_id="


def yahoo_auth(code):
    encoded_creds = base64.b64encode(
        ("{0}:{1}".format(settings.yahoo_key, settings.yahoo_secret)).encode(
            "utf-8"
        )
    )
    details = requests.post(
        url="{}get_token".format(YAHOO_API_URL),
        data={
            "code": code,
            "redirect_uri": "oob",
            "grant_type": "authorization_code",
        },
        headers={
            "Authorization": "Basic {0}".format(encoded_creds.decode("utf-8")),
            "Content-Type": "application/x-www-form-urlencoded",
        },
    ).json()

    details["token_time"] = time.time()
    return details
