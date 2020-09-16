from yahoo_oauth import OAuth2

import os

key = input("Enter Consumer Key:")
secret = input("Enter Consumer Secret:")



key = "dj0yJmk9S2hMMjJNQXc4bTdRJmQ9WVdrOVVqaEhjVlpoTTJNbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTg2"
secret = "562efc5cb7f6b3614c825b580875a757fd76f347"

oauth = OAuth2(key, secret)
os.remove('secrets.json')
print("Access Token: {}".format(oauth.access_token))
print("Guid: {}".format(oauth.guid))
print("Refresh Token: {}".format(oauth.refresh_token))
print("Token time: {}".format(oauth.token_time))
print("Token type: {}".format(oauth.token_type))