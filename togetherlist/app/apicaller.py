import json
import requests

from app.auth import get_access_token


SPOTIFY_BASE_URL = "https://api.spotify.com/v1"

class ApiCaller:
    @staticmethod
    def get(url, params: dict = None, headers: dict = {}) -> requests.Response:
        full_url = '{base_url}/{endpoint_url}'.format(base_url=SPOTIFY_BASE_URL, endpoint_url=url)
        access_token = get_access_token()
        headers['Authorization'] = 'Bearer ' + access_token
        response = requests.get(full_url, params=params, headers=headers)
        if response.status_code != requests.codes['\o/']:
            raise Exception('Get request to {url} unsuccessful: {code}'.format(url=full_url, code=response.status_code))
        return response

    @staticmethod
    def post(url, body: dict = {}, params: dict = None, headers: dict={}) -> requests.Response:
        full_url = '{base_url}/{endpoint_url}'.format(base_url=SPOTIFY_BASE_URL, endpoint_url=url)
        access_token = get_access_token()
        headers['Authorization'] = 'Bearer ' + access_token
        headers['Content-Type'] = 'application/json'
        response = requests.post(full_url, json=body, params=params, headers=headers)
        if response.status_code != requests.codes['\o/'] and response.status_code != requests.codes['created']:
            raise Exception('Post request to {url} unsuccessful: {code}'.format(url=full_url, code=response.status_code))
        return response

    @staticmethod
    def delete(url, body: dict = {}, params: dict = None, headers: dict={}) -> requests.Response:
        full_url = '{base_url}/{endpoint_url}'.format(base_url=SPOTIFY_BASE_URL, endpoint_url=url)
        access_token = get_access_token()
        headers['Authorization'] = 'Bearer ' + access_token
        headers['Content-Type'] = 'application/json'
        response = requests.delete(full_url, json=body, params=params, headers=headers)
        if response.status_code != requests.codes['\o/']:
            raise Exception('Delete request to {url} unsuccessful: {code}'.format(url=full_url, code=response.status_code))
        return response
