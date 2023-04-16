import json
import requests
import time


AUTH_TOKEN = "Basic MTZlZTA2YjU1Mjk2NGE4YTg1ZWZkZDY1N2EzZDQwZDQ6M2I2MzFkOTI0YjExNGFjNTkzMzk0OTY5Y2QxZDQ0NWE="
REFRESH_TOKEN = "AQAhckpke8p4na7kWU4Fgu1DtJHlandokOnoZQlJExJ7Jn0RXBWCv9NhQqHkfjDXP4g4RgmFjw4HDs24uoDiYV4RMEZiO5sd1nHwDe6t6rDL8O_5ZB8eCDf0Lyz4CiR4aCU"
AUTH_URL = "https://accounts.spotify.com/api/token"
REDIRECT_URI = "http://localhost:8000/callback/"

access_token = ''
token_expiry_time = 0
# def get_access_token():
#     params = {
#         'grant_type': 'client_credentials'
#     }
#     headers = {
#         'Authorization': AUTH_TOKEN,
#         'Content-Type': 'application/x-www-form-urlencoded'
#     }
#     response = requests.post(AUTH_URL, params=params, headers=headers)
#     if response.ok:
#         try:
#             response_dict = response.json()
#             return response_dict['access_token']
#         except (KeyError, json.decoder.JSONDecodeError):
#             raise Exception('Authorization failed')
#     else:
#         raise Exception('Authorization failed')

# def get_access_token():
#     params = {
#         'grant_type': 'authorization_code',
#         'code': AUTH_CODE,
#         'redirect_uri': REDIRECT_URI
#     }
#     headers = {
#         'Authorization': AUTH_TOKEN,
#         'Content-Type': 'application/x-www-form-urlencoded'
#     }
#     response = requests.post(AUTH_URL, params=params, headers=headers)
#     if response.ok:
#         try:
#             response_dict = response.json()
#             return response_dict['access_token']
#         except (KeyError, json.decoder.JSONDecodeError):
#             raise Exception('Authorization failed: ' + response.json()['error'])
#     else:
#         raise Exception('Authorization failed: ' + response.json()['error'])

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
        'refresh_token': REFRESH_TOKEN,
        'redirect_uri': REDIRECT_URI
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
            raise Exception('Authorization failed: ' + response.json()['error'])
    else:
        raise Exception('Authorization failed: ' + response.json()['error'])