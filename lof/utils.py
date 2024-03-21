import requests

from .models import SoloDuoLeaderboard, Leaderboard, Player, FlexLeaderboard, TftLeaderboard
from .forms import PlayerForm, SoloDuoLeaderboardForm, FlexLeaderboardForm, TftLeaderboardForm

api_key = ''
tiers = ('UNRANKED', 'IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'EMERALD', 'DIAMOND', 'MASTER', 'GRANDMASTER', 'CHALLENGER')
ranks = ('UNRANKED', 'IV', 'III', 'II', 'I')

def main(leaderboard_name, region, username, tag, wanted_leaderboards): 
  updated = False
  if Player.objects.filter(name=username).exists():
    puuid = Player.objects.get(name=username).puuid
  else:
    puuid = get_puuid(transform_region(region), username, tag)
  id = get_id(region, puuid)
  data = get_data(region, id)
  tft_data = get_tft_data(region, id)
  if 'tft' in wanted_leaderboards:
    for queue in tft_data:
      if queue['queueType'] == 'RANKED_TFT':
        add_player_to_leaderboard(leaderboard_name, region, tag, puuid, id, False, username, queue, 'TFT')
  if 'solo_duo' in wanted_leaderboards or 'flex' in wanted_leaderboards:
    for queue in data:
      if queue['queueType'] == 'RANKED_SOLO_5x5' and 'solo_duo' in wanted_leaderboards:
        add_player_to_leaderboard(leaderboard_name, region, tag, puuid, id, False, username, queue, 'S/D')
      elif queue['queueType'] == 'RANKED_FLEX_SR':
        add_player_to_leaderboard(leaderboard_name, region, tag, puuid, id, False, username, queue, 'FLEX')


def get_puuid(region, username, tag):
  url = 'https://' + region + '.api.riotgames.com/riot/account/v1/accounts/by-riot-id/'+ username + '/' + tag + '?api_key=' + api_key
  response = requests.get(url)
  return response.json()['puuid']
  
def get_id(region, puuid):
  url = 'https://' + region + '.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/' + puuid + '?api_key=' + api_key
  response = requests.get(url)
  return response.json()['id']
  
def get_data(region, id):
  url = 'https://' + region + '.api.riotgames.com/lol/league/v4/entries/by-summoner/' + id + '?api_key=' + api_key
  response = requests.get(url)
  return response.json()

def get_tft_data(region, id):
  url = 'https://' + region + '.api.riotgames.com/tft/league/v1/entries/by-summoner/' + id + '?api_key=' + api_key
  response = requests.get(url)
  return response.json()
  
def add_player_to_leaderboard(leaderboard_name, region, tag, puuid, id, unranked, username, player_info, type):
    if unranked:
      name = username
      defaults = {'tier': player_info['tier'], 'rank': player_info['rank'], 'lp': player_info['leaguePoints']}
    else:
      name = username
      defaults = {'tier': tiers.index(player_info['tier']), 'rank': ranks.index(player_info['rank']), 'lp': player_info['leaguePoints']}

    leaderboard = Leaderboard.objects.get(leaderboard_name=leaderboard_name)
    if Player.objects.filter(name=username).exists():
      player = Player.objects.get(name=username)
      if type == 'S/D':
        add_player_to_soloduoleaderboard(player, leaderboard, defaults)
      elif type == 'FLEX':
        add_player_to_flexleaderboard(player, leaderboard, defaults)
      else:
        add_player_to_tftleaderboard(player, leaderboard, defaults)
    else:
      create_player_form = PlayerForm({'region':region, 'name':username, 'tag':tag, 'puuid':puuid, 'summonerID': id})
      if create_player_form.is_valid():
        create_player_form.save()
        player = Player.objects.get(name=username)
        if type == 'S/D':
          add_player_to_soloduoleaderboard(player, leaderboard, defaults)
        elif type == 'FLEX':
          add_player_to_flexleaderboard(player, leaderboard, defaults)
        else:
          add_player_to_tftleaderboard(player, leaderboard, defaults)
    
def transform_leaderboard(player_names, ordered_leaderboard):
  context = []
  n = 0
  if player_names != []:
    for player in ordered_leaderboard:
      context.append([player_names[n], tiers[player.tier], ranks[player.rank], player.lp])
      n += 1
  return context

def transform_region(region):
  if region == 'EUW1' or region == 'EUN1' or region == 'RU' or region == 'TR1':
    return 'europe'
  elif region == 'LA1' or region == 'LA2' or region == 'NA1' or region == 'BR1':
    return 'americas'
  else:
    return 'asia'

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
      
def add_player_to_tftleaderboard(player,leaderboard,defaults):
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
  if type=='sd':
    leaderboard = SoloDuoLeaderboard.objects.filter(leaderboard = leaderboard)
    for player in leaderboard:
      player_data = player.player.first()
      data = get_data(player_data.region, player_data.summonerID)
      for queue in data:
        if queue['queueType'] == 'RANKED_SOLO_5x5':
          player.tier = tiers.index(queue['tier'])
          player.rank = ranks.index(queue['rank'])
          player.lp = queue['leaguePoints']
          player.save()
  elif type=='flex':
    leaderboard = FlexLeaderboard.objects.filter(leaderboard = leaderboard)
    for player in leaderboard:
      player_data = player.player.first()
      data = get_data(player_data.region, player_data.summonerID)
      for queue in data:
        if queue['queueType'] == 'RANKED_FLEX_SR':
          player.tier = tiers.index(queue['tier'])
          player.rank = ranks.index(queue['rank'])
          player.lp = queue['leaguePoints']
          player.save()
  else:
    leaderboard = TftLeaderboard.objects.filter(leaderboard = leaderboard)
    for player in leaderboard:
      player_data = player.player.first()
      data = get_tft_data(player_data.region, player_data.summonerID)
      for queue in data:
        if queue['queueType'] == 'RANKED_TFT':
          player.tier = tiers.index(queue['tier'])
          player.rank = ranks.index(queue['rank'])
          player.lp = queue['leaguePoints']
          player.save()
    
def remove_players(leaderboard, players, type):
  if type == 'sd':
    for player in players:
      player = Player.objects.get(name=player)
      leaderboard_instance = SoloDuoLeaderboard.objects.filter(leaderboard=leaderboard, player = player)
      leaderboard_instance.delete()
  elif type == 'flex':
    for player in players:
      player = Player.objects.get(name=player)
      leaderboard_instance = FlexLeaderboard.objects.filter(leaderboard=leaderboard, player = player)
      leaderboard_instance.delete()
  else:
    for player in players:
      player = Player.objects.get(name=player)
      leaderboard_instance = TftLeaderboard.objects.filter(leaderboard=leaderboard, player = player)
      leaderboard_instance.delete()
