import random
from functools import cmp_to_key
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect

from .forms import TrackForm, UserForm
from .models import Vote
from app.apicaller import ApiCaller


# Test
# PLAYLIST_ID = "7db8ovaFEAB4blO9f1oEEy?si=c05681fba3d546f6"

# Real
PLAYLIST_ID = '0bWBuhxBO3Ke2FC9Q6AjZk?si=f99503563b884268'

N_WINNERS = 3


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


@login_required
def vote(request):
    user = request.user
    if not user.groups.filter(name='Coronatoppen').exists():
        messages.info(request, 'An administrator must approve your account.')
        return redirect('/app/login')
    if Vote.objects.filter(user=user).exists():
        return HttpResponse("Nice try. You have already voted this week.")
    request_url = 'playlists/{playlist_id}/tracks'.format(
        playlist_id=PLAYLIST_ID)
    response = ApiCaller.get(request_url)
    if not response.ok:
        print(response)
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
            votes = form.cleaned_data
            for track_id in votes.get(form.form_name):
                vote_instance = Vote(user=user, track_id=track_id)
                vote_instance.save()
            return HttpResponseRedirect('results')
        else:
            return render(request, 'vote.html', {'form': form})
    else:
        form = TrackForm(choices=form_list)
        return render(request, 'vote.html', {'form': form})


def results(request):
    request_url = 'playlists/{playlist_id}/tracks'.format(
        playlist_id=PLAYLIST_ID)
    response = ApiCaller.get(request_url)
    response_dict = response.json()
    track_vote_list = []
    for track in response_dict['tracks']['items']:
        track_dict = {}
        id = track['track']['id']
        name = track['track']['name']
        artists = [artist['name'] for artist in track['track']['artists']]
        track_dict['artist'] = ', '.join(artists)
        track_dict['track'] = name
        votes = Vote.objects.filter(track_id=id)
        if votes:
            n_votes = str(len(votes))
            track_dict['n_votes'] = n_votes
            voters = [vote_instance.user.username for vote_instance in votes]
            track_dict['voters'] = ', '.join(voters)
        else:
            track_dict['n_votes'] = '0'
            track_dict['voters'] = ''
        track_vote_list.append(track_dict)
    return render(request, 'list_votes.html', {'tracks': track_vote_list})


@user_passes_test(lambda u: u.is_superuser)
def finish_vote(request):
    vote_dict = {}
    # Count votes for each track
    for vote_instance in Vote.objects.all():
        track_id = vote_instance.track_id
        if track_id in vote_dict:
            vote_dict[track_id] += 1
        else:
            vote_dict[track_id] = 1

    votes_sorted = sorted(vote_dict.items(), key=cmp_to_key(compare_random_ties), reverse=True)
    top_tracks = [vote_inst[0] for vote_inst in votes_sorted[:N_WINNERS]]
    response = ApiCaller.get('tracks', params={'ids': ','.join(top_tracks)})
    response_dict = response.json()
    if 'tracks' in response_dict:
        track_names = [track_item['name'] for track_item in response.json()['tracks']]
        return render(request, 'finish.html', {'tracks': track_names})
    else:
        return HttpResponse('No votes found.')


@user_passes_test(lambda u: u.is_superuser)
def reset_votes(request):
    Vote.objects.all().delete()
    return HttpResponse("Deleted votes")


def compare_random_ties(x, y):
    if x[1] < y[1]:
        return -1
    elif x[1] > y[1]:
        return 1
    else:
        return random.randint(0, 1) * 2 - 1


# @user_passes_test(lambda u: u.is_superuser)
# def finish_vote(request):
#     n_winners = 1

#     # Get all tracks in playlist from Spotify API
#     request_url = 'playlists/{playlist_id}/tracks'.format(
#         playlist_id=PLAYLIST_ID)
#     response = ApiCaller.get(request_url)
#     response_dict = response.json()
#     vote_dict = {}
#     uri_dict = {}
#     for track in response_dict['tracks']['items']:
#         track_id = track['track']['id']
#         uri = track['track']['uri']
#         vote_dict[track_id] = 0
#         uri_dict[track_id] = uri
    
#     # Count votes for each track
#     for vote_instance in Vote.objects.all():
#         track_id = vote_instance.track_id
#         vote_dict[track_id] += 1

#     track_ids = sorted(vote_dict.items(), key=cmp_to_key(compare_random_ties), reverse=True)
#     track_uris = [uri_dict[item[0]] for item in track_ids]
#     winner_uris = track_uris[:n_winners]
#     loser_uris = track_uris[n_winners:]

#     winners_url = 'playlists/{playlist_id}/tracks/'.format(
#         playlist_id=WINNERS_ID)
#     response = ApiCaller.post(winners_url, body={'uris': winner_uris})
#     print(response.json())
#     return HttpResponse("Finished vote")