from email.mime import base
import json
import requests

from app.auth import get_access_token


SPOTIFY_BASE_URL = "https://api.spotify.com/v1"

class ApiCaller:

    @staticmethod
    def get(url, params: dict=None, headers: dict={}):
        full_url = '{base_url}/{endpoint_url}'.format(base_url=SPOTIFY_BASE_URL, endpoint_url=url)
        access_token = get_access_token()
        headers['Authorization'] = 'Bearer ' + access_token
        response = requests.get(full_url, params=params, headers=headers)
        return response

