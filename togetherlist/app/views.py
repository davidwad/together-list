import random
from functools import cmp_to_key
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect

from .forms import TrackForm, UserForm
from .models import Vote
from app.apicaller import ApiCaller


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
        return redirect(results)
    request_url = 'playlists/{playlist_id}/tracks'.format(
        playlist_id=settings.BASE_PLAYLIST_ID)
    response = ApiCaller.get(request_url)
    response_dict = response.json()
    form_list = []
    for track in response_dict['items']:
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
            messages.info(request, 'You must select exactly {n_votes} tracks!'.format(n_votes=settings.N_VOTES))
            return render(request, 'vote.html', {'form': form})
    else:
        form = TrackForm(choices=form_list)
        return render(request, 'vote.html', {'form': form})


def results(request):
    tracks = get_all_tracks(settings.BASE_PLAYLIST_ID)
    track_vote_list = []
    for track in tracks:
        track_dict = {}
        id = track['id']
        name = track['name']
        artists = [artist['name'] for artist in track['artists']]
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
    if request.user.is_superuser:
        return render(request, 'list_votes.html', {'tracks': track_vote_list, 'is_superuser': True})
    else:
        return render(request, 'list_votes.html', {'tracks': track_vote_list})


@user_passes_test(lambda u: u.is_superuser)
def finish_vote(request):
    if request.method == 'POST':
        tracks = get_all_tracks(settings.BASE_PLAYLIST_ID)
        if len(tracks) > 0:
            winning_tracks = move_tracks(tracks)
            delete_tracks_and_votes(tracks)
            return render(request, 'show_winners.html', {'winning_tracks': winning_tracks})
        else:
            return redirect('results')
        

    return render(request, 'confirm_finish.html')


def compare_random_ties(x, y):
    if x[1] < y[1]:
        return -1
    elif x[1] > y[1]:
        return 1
    else:
        return random.randint(0, 1) * 2 - 1


def add_tracks_to_playlist(track_uris: list[str], playlist_id: str):
    if len(track_uris) > 0:
        request_url = 'playlists/{playlist_id}/tracks'.format(
            playlist_id=playlist_id)
        ApiCaller.post(request_url, body={'uris': track_uris})


def get_all_tracks(playlist_id: str) -> list:
    request_url = 'playlists/{playlist_id}/tracks'.format(
        playlist_id=playlist_id)
    response = ApiCaller.get(request_url)
    response_dict = response.json()
    if 'items' in response_dict:
        return [item['track'] for item in response_dict['items']]
    else:
        return []


def move_tracks(tracks: list[dict]) -> list[str]:
    vote_dict = {}
    # Count votes for each track
    for vote_instance in Vote.objects.all():
        track_id = vote_instance.track_id
        if track_id in vote_dict:
            vote_dict[track_id] += 1
        else:
            vote_dict[track_id] = 1
    
    if len(vote_dict) == 0:
        return []

    # Pick winners with most votes
    votes_sorted = sorted(vote_dict.items(), key=cmp_to_key(compare_random_ties), reverse=True)
    winner_ids = [vote_inst[0] for vote_inst in votes_sorted[:settings.N_WINNERS]]

    # Get info for winning and losing tracks from Spotify API
    winner_names = []
    winner_uris = []
    loser_uris = []
    for track in tracks:
        track_id = track['id']
        if track_id in winner_ids:
            winner_names.append(track['name'])
            winner_uris.append(track['uri'])
        else:
            loser_uris.append(track['uri'])

    # Add tracks to winner and loser playlists
    add_tracks_to_playlist(loser_uris, settings.LOSERS_PLAYLIST_ID)
    add_tracks_to_playlist(winner_uris, settings.WINNERS_PLAYLIST_ID)

    return winner_names


def delete_tracks_and_votes(tracks: list[dict]):
    # Extract track URIs
    track_uris = []
    for track in tracks:
        track_uris.append({'uri': track['uri']})

    # Delete votes
    Vote.objects.all().delete()

    # Delete all tracks in playlist
    request_url = 'playlists/{playlist_id}/tracks'.format(
        playlist_id=settings.BASE_PLAYLIST_ID)
    ApiCaller.delete(request_url, body={'tracks': track_uris})
