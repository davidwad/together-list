from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect

from .forms import NameForm
from app.apicaller import ApiCaller


PLAYLIST_ID = "7db8ovaFEAB4blO9f1oEEy?si=c05681fba3d546f6"


def index(request):
    return HttpResponse("Welcome to TogetherList")


def list_tracks(request):
    request_url = 'playlists/{playlist_id}/tracks'.format(playlist_id=PLAYLIST_ID)
    response = ApiCaller.get(request_url)
    response_dict = response.json()
    track_string_list = []
    for track in response_dict['tracks']['items']:
        name = track['track']['name']
        artists = [artist['name'] for artist in track['track']['artists']]
        track_string_list.append('{artists} - {track}'.format(artists=', '.join(artists), track=name))

    return render(request, 'list.html', {'tracks': track_string_list})


def vote(request):
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/register-vote')
    else:
        form = NameForm()

    return render(request, 'name.html', {'form': form})


def register_vote(request):
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            return HttpResponse('Thank you for voting.')
