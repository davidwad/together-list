import json
import requests
import time
from django.conf import settings


TOKEN_URL = "https://accounts.spotify.com/api/token"
REDIRECT_URI = "http://localhost:8000/callback/"

access_token = ''
token_expiry_time = 0


def get_access_token():
    global token_expiry_time
    global access_token
    if time.time() > token_expiry_time - 60:
        access_token = refesh_access_token()
        token_expiry_time = time.time() + 3600
        return access_token
    else:
        return access_token


def refesh_access_token():
    params = {
        'grant_type': 'refresh_token',
        'refresh_token': settings.REFRESH_TOKEN,
        'redirect_uri': REDIRECT_URI
    }
    headers = {
        'Authorization': settings.AUTH_TOKEN,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(TOKEN_URL, params=params, headers=headers)
    if response.ok:
        try:
            response_dict = response.json()
            return response_dict['access_token']
        except (KeyError, json.decoder.JSONDecodeError):
            raise Exception('Authorization failed: ' + response.json()['error'])
    else:
        raise Exception('Authorization failed: ' + response.json()['error'])