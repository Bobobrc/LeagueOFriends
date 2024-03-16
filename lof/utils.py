import requests
from pprint import pprint

from .models import SoloDuoLeaderboard, Leaderboard, Player
from .forms import PlayerForm, SoloDuoLeaderboardForm

api_key = ''
tiers = ('UNRANKED', 'IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'EMERALD', 'DIAMOND', 'MASTER', 'GRANDMASTER', 'CHALLENGER')
ranks = ('UNRANKED', 'IV', 'III', 'II', 'I')

def main(leaderboard_name, region, username, tag): 
  updated = False
  puuid = get_puuid(transform_region(region), username, tag)
  id = get_id(region, puuid)
  data = get_data(region, id)
  for queue in data:
    if queue['queueType'] == 'RANKED_SOLO_5x5':
      update_leaderboard(leaderboard_name, puuid, False, username, queue)
      updated = True
  if not updated:
    update_leaderboard(leaderboard_name, puuid, True, username, {'tier':0, 'rank':0, 'leaguePoints':0})
  return puuid


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
  
def update_leaderboard(leaderboard_name, puuid, unranked, username, player_info):
    if unranked:
      name = username
      defaults = {'tier': 0, 'rank': 0, 'lp': 0}
    else:
      name = username
      defaults = {'tier': tiers.index(player_info['tier']), 'rank': ranks.index(player_info['rank']), 'lp': player_info['leaguePoints']}

    leaderboard = Leaderboard.objects.get(leaderboard_name=leaderboard_name)
    if Player.objects.filter(name=username).exists():
      player = Player.objects.get(name=username)
      create_soloduoleaderboard_form = SoloDuoLeaderboardForm({
          'leaderboard': leaderboard,
          'player': [player],
          'tier': defaults['tier'],
          'rank': defaults['rank'],
          'lp': defaults['lp']
        })
      if create_soloduoleaderboard_form.is_valid():
        create_soloduoleaderboard_form.save()
    else:
      create_player_form = PlayerForm({'name':username, 'puuid':puuid})
      if create_player_form.is_valid():
        player = create_player_form.save()
        create_soloduoleaderboard_form = SoloDuoLeaderboardForm({
          'leaderboard': leaderboard,
          'player': [player],
          'tier': defaults['tier'],
          'rank': defaults['rank'],
          'lp': defaults['lp']
        })
        if create_soloduoleaderboard_form.is_valid():
          create_soloduoleaderboard_form.save()
    
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
