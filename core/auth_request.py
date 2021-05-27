from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from time import time
import os


client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
token_url = os.environ['TOKEN_URL']
audience = os.environ['AUDIENCE']

client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)
auth_token = None


def is_expired(token):
    return time() <= (token['expired_at'] - 2)


def ensure_auth_token():
    global auth_token
    if auth_token is None or is_expired(auth_token):
        auth_token = oauth.fetch_token(
            token_url=token_url, client_id=client_id, client_secret=client_secret, audience=audience
        )
        auth_token['expired_at'] = time() + auth_token['expires_in']


def auth_request(url, data):
    ensure_auth_token()
    oauth.request('POST', url, data)


if __name__ == "__main__":
    auth_request("http://localhost:8080/board/proto/throw", "S3")
