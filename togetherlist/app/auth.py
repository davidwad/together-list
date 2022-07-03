import json
import requests


AUTH_TOKEN = "Basic MTZlZTA2YjU1Mjk2NGE4YTg1ZWZkZDY1N2EzZDQwZDQ6M2I2MzFkOTI0YjExNGFjNTkzMzk0OTY5Y2QxZDQ0NWE="
AUTH_URL = "https://accounts.spotify.com/api/token"
REDIRECT_URI = 'http://localhost:8000/callback/'


def get_access_token():
    params = {
        'grant_type': 'client_credentials'
    }
    headers = {
        'Authorization': AUTH_TOKEN,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(AUTH_URL, params=params, headers=headers)
    if response.ok:
        try:
            response_dict = response.json()
            return response_dict['access_token']
        except (KeyError, json.decoder.JSONDecodeError):
            raise Exception('Authorization failed')
    else:
        raise Exception('Authorization failed')
