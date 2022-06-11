from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('tracks', views.list_tracks, name='list tracks'),
    path('vote', views.vote, name='vote'),
    path('register-vote', views.register_vote, name='register vote')
]