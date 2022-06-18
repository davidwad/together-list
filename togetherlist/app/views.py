from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect

from .forms import TrackForm, UserForm, UserRegistrationForm
from .models import Track
from app.apicaller import ApiCaller



PLAYLIST_ID = "7db8ovaFEAB4blO9f1oEEy?si=c05681fba3d546f6"
# PLAYLIST_ID = '0bWBuhxBO3Ke2FC9Q6AjZk?si=f99503563b884268'

def is_member(user):
    return user.groups.filter(name='Coronatoppen').exists()


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
        if request.method=="POST":
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            username = request.POST['username']
            password = request.POST['password']
            email = request.POST['email']
            newuser = User.objects.create_user(
                first_name=first_name, 
                last_name=last_name,
                username=username,
                password=password,
                email=email
            )
            try:
                newuser.save()
            except:
                return HttpResponse("Something went wrong.")
        else:
            form = UserRegistrationForm()
        return render(request, 'signup.html', {'form':form}) 

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
@user_passes_test(is_member)
def vote(request):
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
            # form.cleaned_data
            return HttpResponseRedirect('/register-vote')
    else:
        form = TrackForm(request.POST, choices=form_list)

    return render(request, 'name.html', {'form': form})


def register_vote(request):
    if request.method == 'POST':
        # form = TrackForm(request.POST)
        # if form.is_valid():
        return HttpResponse('Thank you for voting.')
