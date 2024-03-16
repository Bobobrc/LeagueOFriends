from django.urls import path

from . import views

urlpatterns = [
  path('', views.firstpage, name='firstpage'),
  path('leaderboard/<str:leaderboard_name>', views.leaderboard, name='leaderboard')
]