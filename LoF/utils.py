import requests

from datetime import timedelta

from django.contrib import messages
from django.conf import settings

from .models import Leaderboard, Player, SoloDuoLeaderboard, FlexLeaderboard, TftLeaderboard
from .forms import PlayerForm, SoloDuoLeaderboardForm, FlexLeaderboardForm, TftLeaderboardForm

lol_api_key = settings.LOL_API_KEY
tft_api_key = settings.TFT_API_KEY
tiers = ('UNRANKED', 'IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'EMERALD', 'DIAMOND', 'MASTER', 'GRANDMASTER', 'CHALLENGER')
ranks = ('UNRANKED', 'IV', 'III', 'II', 'I')

def main(leaderboard_name, region, username, tag, wanted_leaderboards):
  player = Player.objects.filter(name=username, tag=tag, region=region).first()
  if player:
    tft_puuid = player.tft_puuid
    lol_puuid = player.lol_puuid
  else:
    tft_puuid = get_puuid(transform_region(region), username, tag, 'TFT')
    lol_puuid = get_puuid(transform_region(region), username, tag, 'LOL')
  
  tft_unranked = True
  solo_duo_unranked = True
  flex_unranked = True
  if 'inTft' in wanted_leaderboards:
    tft_data = get_tft_data(region, tft_puuid)
    for queue in tft_data:
      if queue['queueType'] == 'RANKED_TFT':
        tft_unranked = False
        add_player_to_leaderboard(leaderboard_name, region, tag, lol_puuid, tft_puuid, tft_unranked, username, queue, 'TFT')
        break
    if tft_unranked == True:
      add_player_to_leaderboard(leaderboard_name, region, tag, lol_puuid, tft_puuid, tft_unranked, username, [], 'TFT')
      
  if 'inSoloDuo' in wanted_leaderboards or 'inFlex' in wanted_leaderboards:
    data = get_data(region, lol_puuid)
    for queue in data:
      if queue['queueType'] == 'RANKED_SOLO_5x5' and 'inSoloDuo' in wanted_leaderboards:
        solo_duo_unranked = False
        add_player_to_leaderboard(leaderboard_name, region, tag, lol_puuid, tft_puuid, solo_duo_unranked, username, queue, 'S/D')
      elif queue['queueType'] == 'RANKED_FLEX_SR' and 'inFlex' in wanted_leaderboards:
        flex_unranked = False
        add_player_to_leaderboard(leaderboard_name, region, tag, lol_puuid, tft_puuid, flex_unranked, username, queue, 'FLEX')
    if solo_duo_unranked == True and 'inSoloDuo' in wanted_leaderboards:
      add_player_to_leaderboard(leaderboard_name, region, tag, lol_puuid, tft_puuid, solo_duo_unranked, username, [], 'S/D')
    if flex_unranked == True and 'inFlex' in wanted_leaderboards:
      add_player_to_leaderboard(leaderboard_name, region, tag, lol_puuid, tft_puuid, flex_unranked, username, [], 'FLEX')
      
def get_puuid(region, username, tag, game):
  if game == 'LOL':
    url = f'https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{username}/{tag}?api_key={lol_api_key}'
  if game == 'TFT':
    url = f'https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{username}/{tag}?api_key={tft_api_key}'
  response = requests.get(url)
  if response.status_code == 200:
    return response.json().get('puuid')
  elif response.status_code in [400, 404]:
    raise ValueError('Player not found. Please check the username and tag')
  elif response.status_code in [429, 500]:
    raise Exception('Can\'t get the player. Please try again later')
  else:
    raise Exception('Couldn\'t add the player, try again!')

def get_data(region, puuid):
  url = f'https://{region}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}?api_key={lol_api_key}'
  response = requests.get(url)
  if response.status_code == 200:
    return response.json()
  elif response.status_code in [400, 404]:
    raise ValueError('Player not found. Please check the username and tag')
  elif response.status_code in [429, 500]:
    raise Exception('Can\'t get the player. Please try again later')
  else:
    raise Exception('Couldn\'t add the player, try again!')
  
def get_tft_data(region, puuid):
  url = f'https://{region}.api.riotgames.com/tft/league/v1/by-puuid/{puuid}?api_key={tft_api_key}'
  response = requests.get(url)
  if response.status_code == 200:
    return response.json()
  elif response.status_code in [400, 404]:
    raise ValueError('Player not found. Please check the username and tag')
  elif response.status_code in [429, 500]:
    raise Exception('Can\'t get the player. Please try again later')
  else:
    raise Exception('Couldn\'t add the player, try again!')
  
def add_player_to_leaderboard(leaderboard_name, region, tag, lol_puuid, tft_puuid, unranked, username, player_info, type):
  if unranked:
    defaults = {'tier': 0, 'rank': 0, 'lp': 0}
  else:
    defaults = {'tier': tiers.index(player_info['tier']), 'rank': ranks.index(player_info['rank']), 'lp':player_info['leaguePoints']}
  
  leaderboard = Leaderboard.objects.get(leaderboard_name=leaderboard_name)
  player = Player.objects.filter(name=username, tag=tag, region=region).first()
  
  if player and region == player.region:
    if type == 'S/D':
      add_player_to_soloduoleaderboard(player, leaderboard, defaults)
    elif type == 'FLEX':
      add_player_to_flexleaderboard(player, leaderboard, defaults)
    else:
      add_player_to_tftleaderboard(player, leaderboard, defaults)
  else:
    create_player_form = PlayerForm({'region': region, 'name': username, 'tag': tag, 'lol_puuid': lol_puuid, 'tft_puuid': tft_puuid})
    if create_player_form.is_valid():
      create_player_form.save()
      player = Player.objects.get(name=username, tag=tag, region=region)
      if type == 'S/D':
        add_player_to_soloduoleaderboard(player, leaderboard, defaults)
      elif type == 'FLEX':
        add_player_to_flexleaderboard(player, leaderboard, defaults)
      else:
        add_player_to_tftleaderboard(player, leaderboard, defaults)
        
def transform_leaderboard(player_names, ordered_leaderboard):
  context = []
  if player_names != []:
    for n, player in enumerate(ordered_leaderboard):
      tier = tiers[player.tier]
      player_name = player_names[n]
      
      if tier == 'UNRANKED':
        context.append([n+1, player_name, tier])
      elif tier in {'MASTER', 'GRANDMASTER', 'CHALLENGER'}:
        context.append([n+1, player_name, tier, player.lp])
      else:
        context.append([n+1, player_name, tier, ranks[player.rank], player.lp])
  return context

def transform_region(region):
  region_map = {
        'EUW1': 'europe',
        'EUN1': 'europe',
        'RU': 'europe',
        'TR1': 'europe',
        'LA1': 'americas',
        'LA2': 'americas',
        'NA1': 'americas',
        'BR1': 'americas'
    }
  return region_map.get(region, 'asia')

def add_player_to_soloduoleaderboard(player, leaderboard, defaults):
  if not SoloDuoLeaderboard.objects.filter(leaderboard=leaderboard, player=player).exists():
    create_soloduoleaderboard_form = SoloDuoLeaderboardForm({
      'leaderboard': leaderboard,
      'player': [player],
      'tier': defaults['tier'],
      'rank': defaults['rank'],
      'lp': defaults['lp']
    })
    if create_soloduoleaderboard_form.is_valid():
      create_soloduoleaderboard_form.save()
      
def add_player_to_flexleaderboard(player, leaderboard, defaults):
  if not FlexLeaderboard.objects.filter(leaderboard=leaderboard, player=player).exists():
    create_flexleaderboard_form = FlexLeaderboardForm({
      'leaderboard': leaderboard,
      'player': [player],
      'tier': defaults['tier'],
      'rank': defaults['rank'],
      'lp': defaults['lp']
    })
    if create_flexleaderboard_form.is_valid():
      create_flexleaderboard_form.save()
    
def add_player_to_tftleaderboard(player, leaderboard, defaults):
  if not TftLeaderboard.objects.filter(leaderboard=leaderboard, player=player).exists():
    create_tftleaderboard_form = TftLeaderboardForm({
      'leaderboard': leaderboard,
      'player': [player],
      'tier': defaults['tier'],
      'rank': defaults['rank'],
      'lp': defaults['lp']
    })
    if create_tftleaderboard_form.is_valid():
      create_tftleaderboard_form.save()
    
def update_leaderboard(leaderboard, type):
  leaderboard_model = {
    'sd': SoloDuoLeaderboard,
    'flex': FlexLeaderboard,
    'tft': TftLeaderboard
  }.get(type)
  
  if not leaderboard_model:
    return
  
  players = leaderboard_model.objects.filter(leaderboard=leaderboard)
  updates = []
  for player in players:
    player_data = player.player.first()
    if type != 'tft':
      data = get_data(player_data.region, player_data.lol_puuid)
    else:
      data = get_tft_data(player_data.region, player_data.tft_puuid)
    
    for queue in data:
      if queue['queueType'] == ('RANKED_SOLO_5x5' if type == 'sd' else
                                'RANKED_FLEX_SR' if type == 'flex' else
                                'RANKED_TFT'):
        new_tier = tiers.index(queue['tier'])
        new_rank = ranks.index(queue['rank'])
        new_lp = queue['leaguePoints']
        if player.tier != new_tier or player.rank != new_rank or player.lp != new_lp:
          player.tier = new_tier
          player.rank = new_rank
          player.lp = new_lp
          updates.append(player)
          
    if updates:
      leaderboard_model.objects.bulk_update(updates, ['tier', 'rank', 'lp'])
      
def remove_players(leaderboard, player, type):
  player_name = player.split('#')[0]
  player_instance = Player.objects.get(name=player_name)
  
  leaderboard_model = {
    'sd': SoloDuoLeaderboard,
    'flex': FlexLeaderboard,
    'tft': TftLeaderboard
  }.get(type)
  
  if leaderboard_model:
    leaderboard_instance = leaderboard_model.objects.filter(leaderboard=leaderboard, player=player_instance)
    leaderboard_instance.delete()
    
def check_leaderboard_exists(request, leaderboard_name):
  if Leaderboard.objects.filter(leaderboard_name=leaderboard_name).exists():
    return True
  else:
    messages.error(request, "Leaderboard does not exist!")
    
def can_update(now, last_updated):
  delay = 3*60
  return not last_updated or (now - last_updated) > timedelta(seconds=delay)