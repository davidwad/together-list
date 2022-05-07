from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from app.apicaller import ApiCaller

PLAYLIST_ID = "3OfKuiS37oW6ciU88lWffV?si=fc3a61cd5aa14b92"


def index(request):
    return HttpResponse("Welcome to TogetherList")


def list_tracks(request):
    request_url = 'playlists/{playlist_id}/tracks'.format(playlist_id=PLAYLIST_ID)
    response = ApiCaller.get(request_url)
    return JsonResponse(response.json())
