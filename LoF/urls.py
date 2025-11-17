from django.urls import path

from . import views

urlpatterns = [
  path('', views.mainPage, name='mainPage'),
  path('login', views.loginPage, name='loginPage'),
  path('logout', views.logoutUser, name='logout'),
  path('register', views.registerPage, name='registerPage'),
  path('leaderboard/<str:leaderboard_name>', views.leaderboardPage, name='leaderboard'),
]