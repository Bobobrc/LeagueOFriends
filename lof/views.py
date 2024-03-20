from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404

from .models import Leaderboard, SoloDuoLeaderboard, FlexLeaderboard, TftLeaderboard
from .forms import LeaderboardForm
from .utils import main, transform_leaderboard, update_leaderboard, remove_players

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
  wanted_leaderboards = []
  error_message = None
  leaderboard = Leaderboard.objects.get(leaderboard_name=leaderboard_name)
  if request.method == "POST":
    if 'update_sd_leaderboard' in request.POST:
      update_leaderboard(leaderboard, 'sd')
    elif 'update_flex_leaderboard' in request.POST:
      update_leaderboard(leaderboard, 'flex')
    elif 'update_tft_leaderboard' in request.POST:
      update_leaderboard(leaderboard, 'tft')
    elif 'remove_player' in request.POST:
      print(request.POST)
      if 'sd_players' in request.POST:
        players = request.POST.getlist('sd_players')
        remove_players(leaderboard, players, 'sd')
      if 'flex_players' in request.POST:
        players = request.POST.getlist('flex_players')
        remove_players(leaderboard, players, 'flex')
      if 'tft_players' in request.POST:
        players = request.POST.getlist('tft_players')
        remove_players(leaderboard, players, 'tft')
    else:
      region = request.POST['region']
      username = request.POST['username']
      tag = request.POST['tag']
      if request.POST.get('solo_duo') == 'on':
        wanted_leaderboards.append('solo_duo')
      if request.POST.get('flex') == 'on':
        wanted_leaderboards.append('flex')
      if request.POST.get('tft') == 'on':
        wanted_leaderboards.append('tft')
      try:
        main(leaderboard_name, region, username, tag, wanted_leaderboards)
      except:
        error_message = 'Couldn\'t find the player, try again!'
  try:
    solo_duo_leaderboard = SoloDuoLeaderboard.objects.filter(leaderboard=leaderboard)
    flex_leaderboard = FlexLeaderboard.objects.filter(leaderboard=leaderboard)
    tft_leaderboard = TftLeaderboard.objects.filter(leaderboard=leaderboard)
  except:
    return render(request, './lof/leaderboard.html', {
      'leaderboard_name': leaderboard_name,
      'players': [],
      'error_message': error_message
    })
  else:
    solo_duo_leaderboard = solo_duo_leaderboard.order_by('-tier', '-rank', '-lp')
    flex_leaderboard = flex_leaderboard.order_by('-tier', '-rank', '-lp')
    tft_leaderboard = tft_leaderboard.order_by('-tier', '-rank', '-lp')
    solo_duo_players = []
    for players in solo_duo_leaderboard:
      solo_duo_players += [player.name for player in players.player.all()]
    flex_players = []
    for players in flex_leaderboard:
      flex_players += [player.name for player in players.player.all()]
    tft_players = []
    for players in tft_leaderboard:
      tft_players += [player.name for player in players.player.all()]
    solo_duo_players = transform_leaderboard(solo_duo_players, solo_duo_leaderboard)
    flex_players = transform_leaderboard(flex_players, flex_leaderboard)
    tft_players = transform_leaderboard(tft_players, tft_leaderboard)
    return render(request, './lof/leaderboard.html', {
      'leaderboard_name' : leaderboard_name,
      'solo_duo_players' : solo_duo_players,
      'flex_players' : flex_players,
      'tft_players' : tft_players,
      'error_message' : error_message
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