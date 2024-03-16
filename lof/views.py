from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404

from .models import Leaderboard, SoloDuoLeaderboard, Player
from .forms import LeaderboardForm, PlayerForm, SoloDuoLeaderboard
from .utils import main, transform_leaderboard

# Create your views here.

def firstpage(request):
  if request.method == "POST":
    if 'search_leaderboard' in request.POST:
      leaderboard_name = request.POST.get('leaderboard_name')
      try:
        Leaderboard.objects.get(leaderboard_name = leaderboard_name)
        return redirect('leaderboard', leaderboard_name = leaderboard_name)
      except Leaderboard.DoesNotExist:
        return render(request, './lof/firstpage.html', {'error_message': "Leaderboard does not exist!"})
    else:
      create_leaderboard_form = LeaderboardForm(request.POST)
      if create_leaderboard_form.is_valid():
        leaderboard_name = create_leaderboard_form.cleaned_data['leaderboard_name']
        create_leaderboard_form.save()  
        return redirect('leaderboard', leaderboard_name = leaderboard_name)
      else:
        return render(request, './lof/firstpage.html', {'error_message': "Leaderboard already exists!"})
  return render(request, './lof/firstpage.html')

def leaderboard(request, leaderboard_name):
  leaderboard = Leaderboard.objects.get(leaderboard_name=leaderboard_name)
  if request.method == "POST":
    region = request.POST['region']
    username = request.POST['username']
    tag = request.POST['tag']
    main(leaderboard_name, region, username, tag )
  try:
    solo_duo_leaderboard = SoloDuoLeaderboard.objects.filter(leaderboard=leaderboard)
  except:
    return render(request, './lof/leaderboard.html', {
      'leaderboard_name': leaderboard_name,
      'players': [],
    })
  else:
    ordered_leaderboard = solo_duo_leaderboard.order_by('-tier', '-rank', '-lp')
    player_names = []
    for players in ordered_leaderboard:
      player_names += [player.name for player in players.player.all()]
    players = transform_leaderboard(player_names, ordered_leaderboard)
    return render(request, './lof/leaderboard.html', {
      'leaderboard_name' : leaderboard_name,
      'players' : players
    })
    return render(request, './lof/leaderboard.html', {
        'leaderboard_name': leaderboard_name,
        'players': [],
      })
  '''try:
    leaderboard = Leaderboard.objects.get(leaderboard_name=leaderboard_name)
    solo_duo_leaderboard = SoloDuoLeaderboard.objects.filter(leaderboard=leaderboard)
    players = Player.objects.filter(soloduoleaderboards__in = solo_duo_leaderboard)
  except SoloDuoLeaderboard.DoesNotExist:
    return render(request, './lof/leaderboard.html', {
      'leaderboard_name': leaderboard_name,
      'players': [],
    })
  else:
    return render(request, './lof/leaderboard.html', {
              'leaderboard_name': leaderboard_name,
              'players': players,
          })'''