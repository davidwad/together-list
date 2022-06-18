from django.urls import path

from . import views

urlpatterns = [
    path('', views.vote, name='vote'),
    path('login/', views.signin),
    path('signup/', views.signup),
    path('tracks', views.list_tracks, name='list tracks'),
    path('register-vote', views.register_vote, name='register vote')
]