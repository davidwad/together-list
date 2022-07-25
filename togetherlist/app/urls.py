from django.urls import path

from . import views

urlpatterns = [
    path('', views.vote, name='vote'),
    path('login/', views.signin, name='login'),
    path('signup/', views.signup, name='signup'),
    path('results/', views.results, name='register vote'),
    path('finish/', views.finish_vote, name='finish vote'),
    path('reset/', views.reset_votes, name='reset votes')
]