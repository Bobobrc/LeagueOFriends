from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.utils import timezone

from .forms import RegisterForm, LeaderboardForm
from .models import Leaderboard, SoloDuoLeaderboard, FlexLeaderboard, TftLeaderboard
from .utils import main, transform_leaderboard, update_leaderboard, remove_players, check_leaderboard_exists, can_update

# Create your views here.

def registerPage(request):
  if request.user.is_authenticated:
    return redirect('mainPage')
  
  show_navbar_search = True
  
  form = RegisterForm()
  
  if request.method == 'POST':
    if 'search_leaderboard' in request.POST:
      leaderboard_name = request.POST.get('leaderboard_name')
      if check_leaderboard_exists(request, leaderboard_name):
        return redirect('leaderboard', leaderboard_name=leaderboard_name)
      else:
        return redirect('loginPage')
      
    form = RegisterForm(request.POST)
    if form.is_valid():
      form.save()
      username = form.cleaned_data.get('username')
      messages.success(request, f'Account was created for {username}!')
      return redirect('loginPage')
    
  context = {'form': form, 'show_navbar_search':show_navbar_search}
  return render(request, 'LoF/register.html', context)

def loginPage(request):
  if request.user.is_authenticated:
    return redirect('mainPage')
  
  show_navbar_search = False
  
  if request.method == 'POST':
    if 'search_leaderboard' in request.POST:
      leaderboard_name = request.POST.get('leaderboard_name')
      if check_leaderboard_exists(request, leaderboard_name):
        return redirect('leaderboard', leaderboard_name=leaderboard_name)
    else:
      username = request.POST.get('username')
      password = request.POST.get('password')
      user = authenticate(request, username=username, password=password)
      if user is not None:
        login(request, user)
        messages.success(request, 'You have been logged in successfully.')
        return redirect('mainPage')
      else:
        messages.error(request, 'USERNAME or PASSWORD is incorrect!')
  context = {'show_navbar_search':show_navbar_search}
  return render(request, 'LoF/login.html', context)

def logoutUser(request):
  logout(request)
  messages.success(request, 'You have been logged out successfully.')
  return redirect('loginPage')

@login_required(login_url='loginPage')
def mainPage(request):
  show_navbar_search = False
  
  leaderboards = Leaderboard.objects.filter(user=request.user)
  
  if request.method == 'POST':
    if 'search_leaderboard' in request.POST:
      leaderboard_name = request.POST.get('leaderboard_name')
      if check_leaderboard_exists(request, leaderboard_name):
        return redirect('leaderboard', leaderboard_name=leaderboard_name)
      else:
        return redirect('mainPage')
    create_leaderboard_form = LeaderboardForm(request.POST)
    if create_leaderboard_form.is_valid():
      leaderboard_name = create_leaderboard_form.cleaned_data['leaderboard_name']
      if not Leaderboard.objects.filter(leaderboard_name=leaderboard_name).exists():
        leaderboard = create_leaderboard_form.save(commit=False)
        leaderboard.user = request.user
        create_leaderboard_form.save()
        return redirect('leaderboard', leaderboard_name=leaderboard_name)
    else:
      messages.error(request, 'Leaderboard already exists. Change the name and try again')
  
  create_leaderboard_form = LeaderboardForm()
  context = {'form': create_leaderboard_form, 'leaderboards': leaderboards, 'show_navbar_search': show_navbar_search}
  return render(request, './LoF/main.html', context)

def leaderboardPage(request, leaderboard_name):
  leaderboard = Leaderboard.objects.get(leaderboard_name=leaderboard_name)

  show_navbar_search = True
  
  wanted_leaderboards = []
  
  leaderboard_creator = request.user.username == leaderboard.user.username
  
  now = timezone.now()
  
  soloduo_leaderboard = leaderboard.soloduoleaderboard_set.first()
  flex_leaderboard = leaderboard.flexleaderboard_set.first()
  tft_leaderboard = leaderboard.tftleaderboard_set.first()
  
  can_update_soloduo = can_update(now, soloduo_leaderboard.last_updated) if soloduo_leaderboard else True
  can_update_flex = can_update(now, flex_leaderboard.last_updated) if flex_leaderboard else True
  can_update_tft = can_update(now, tft_leaderboard.last_updated) if tft_leaderboard else True
  if request.method == 'POST':
    
    request.session['inSoloDuo'] = 'inSoloDuo' in request.POST
    request.session['inFlex'] = 'inFlex' in request.POST
    request.session['inTft'] = 'inTft' in request.POST
    
    if 'search_leaderboard' in request.POST:
      leaderboard_name = request.POST.get('leaderboard_name')
      if check_leaderboard_exists(request, leaderboard_name):
        return redirect('leaderboard', leaderboard_name=leaderboard_name)
      else:
        return redirect('mainPage')
      
    if 'deleteLeaderboard' in request.POST:
      leaderboard.delete()
      return redirect('mainPage')
    if 'updateSoloDuo' in request.POST and can_update_soloduo:
      try:
        soloduo_leaderboard.last_updated = now
        soloduo_leaderboard.save()
        update_leaderboard(leaderboard, 'sd')
        return redirect('leaderboard', leaderboard_name=leaderboard_name)
      except:
        messages.error(request, 'Can\'t update an empty leaderboard!')
    elif 'updateFlex' in request.POST and can_update_flex:
      try:
        flex_leaderboard.last_updated = now
        flex_leaderboard.save()
        update_leaderboard(leaderboard, 'flex')
        return redirect('leaderboard', leaderboard_name=leaderboard_name)
      except:
        messages.error(request, 'Can\'t update an empty leaderboard!')
    elif 'updateTft' in request.POST and can_update_tft:
      try:
        tft_leaderboard.last_updated = now
        tft_leaderboard.save()
        update_leaderboard(leaderboard, 'tft')
        return redirect('leaderboard', leaderboard_name=leaderboard_name)
      except:
        messages.error(request, 'Can\'t update an empty leaderboard!')
    elif 'remove_player' in request.POST:
      if leaderboard_creator:
        player_info = request.POST.get('remove_player')
        player_name, table = player_info.split('_')
        if 'soloduo' == table:
          remove_players(leaderboard, player_name, 'sd')
        elif 'flex' == table:
          remove_players(leaderboard, player_name, 'flex')
        else:
          remove_players(leaderboard, player_name, 'tft')
    elif 'add_player' in request.POST:
      region = request.POST['region']
      username = request.POST['username']
      tag = request.POST['tag']
      if request.POST.get('inSoloDuo') == 'on':
        wanted_leaderboards.append('inSoloDuo')
      if request.POST.get('inFlex') == 'on':
        wanted_leaderboards.append('inFlex')
      if request.POST.get('inTft') == 'on':
        wanted_leaderboards.append('inTft')
        
      try:
        main(leaderboard_name, region, username, tag, wanted_leaderboards)
      except ValueError as ve:
        messages.error(request, str(ve))
      except Exception as e:
        messages.error(request, str(e))
        
  soloduo_ordered_players = SoloDuoLeaderboard.objects.filter(leaderboard=leaderboard)
  flex_ordered_players = FlexLeaderboard.objects.filter(leaderboard=leaderboard)
  tft_ordered_players = TftLeaderboard.objects.filter(leaderboard=leaderboard)
  
  solo_duo_players = []
  for player_entry in soloduo_ordered_players:
    player = player_entry.player.first()
    if player:
        solo_duo_players.append(player.name + '#' + player.tag)
  flex_players = []
  for player_entry in flex_ordered_players:
    player = player_entry.player.first()
    if player:
        flex_players.append(player.name + '#' + player.tag)
  tft_players = []
  for player_entry in tft_ordered_players:
    player = player_entry.player.first()
    if player:
        tft_players.append(player.name + '#' + player.tag)
        
  solo_duo_players = transform_leaderboard(solo_duo_players, soloduo_ordered_players)
  flex_players = transform_leaderboard(flex_players, flex_ordered_players)
  tft_players = transform_leaderboard(tft_players, tft_ordered_players)
  context = {
    'in_soloq': request.session.get('inSoloDuo', False),
    'in_flex': request.session.get('inFlex', False),
    'in_tft': request.session.get('inTft', False),
    'can_update_soloduo': can_update_soloduo,
    'can_update_flex': can_update_flex,
    'can_update_tft': can_update_tft,
    'leaderboard_creator': leaderboard_creator,
    'leaderboard_name' : leaderboard_name,
    'solo_duo_players' : solo_duo_players,
    'flex_players' : flex_players,
    'tft_players' : tft_players,
    'leaderboard': leaderboard,
    'show_navbar_search':show_navbar_search,
    }
  
  return render(request, 'lof/leaderboard.html', context)