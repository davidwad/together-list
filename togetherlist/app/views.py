from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect

from .forms import TrackForm, UserForm
from app.apicaller import ApiCaller


PLAYLIST_ID = "7db8ovaFEAB4blO9f1oEEy?si=c05681fba3d546f6"
# PLAYLIST_ID = '0bWBuhxBO3Ke2FC9Q6AjZk?si=f99503563b884268'


def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(
            request,
            username=username,
            password=password
        )
        if user is None:
            return HttpResponse("Invalid credentials.")
        login(request, user)
        return redirect('/app')
    else:
        form = UserForm()
        return render(request, 'login.html', {'form': form})


def signup(request):
	if request.method == "POST":
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect('/app')
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = UserCreationForm()
	return render(request=request, template_name="signup.html", context={"form":form})


def list_tracks(request):
    request_url = 'playlists/{playlist_id}/tracks'.format(
        playlist_id=PLAYLIST_ID)
    response = ApiCaller.get(request_url)
    response_dict = response.json()
    track_string_list = []
    for track in response_dict['tracks']['items']:
        name = track['track']['name']
        artists = [artist['name'] for artist in track['track']['artists']]
        track_string_list.append(
            '{artists} - {track}'.format(artists=', '.join(artists), track=name))

    return render(request, 'list.html', {'tracks': track_string_list})


@login_required
def vote(request):
    user = request.user
    if not user.groups.filter(name='Coronatoppen').exists():
        messages.info(request, 'An administrator must approve your account.')
        return redirect('/app/login')
    request_url = 'playlists/{playlist_id}/tracks'.format(
        playlist_id=PLAYLIST_ID)
    response = ApiCaller.get(request_url)
    response_dict = response.json()
    form_list = []
    for track in response_dict['tracks']['items']:
        id = track['track']['id']
        name = track['track']['name']
        artists = [artist['name'] for artist in track['track']['artists']]
        display = '{artists} - {track}'.format(
            artists=', '.join(artists), track=name)
        form_list.append((id, display))

    if request.method == 'POST':
        form = TrackForm(request.POST, choices=form_list)
        if form.is_valid():
            print(form.cleaned_data)
            return HttpResponseRedirect('register-vote')
    else:
        form = TrackForm(choices=form_list)
        return render(request, 'name.html', {'form': form})


def register_vote(request):
    if request.method == 'POST':
        return HttpResponse('Thank you for voting.')
