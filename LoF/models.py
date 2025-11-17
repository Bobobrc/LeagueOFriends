from django.db import models

from django.contrib.auth.models import User

# Create your models here.
class Player(models.Model):
  region = models.CharField(max_length=100)
  name = models.CharField(max_length=100)
  tag = models.CharField(max_length=100)
  lol_puuid = models.CharField(max_length=100)
  tft_puuid = models.CharField(max_length=100)
  
  def __str__(self):
    return f'{self.region} {self.name} {self.tag}'
  
  class Meta:
    ordering = ['region', 'name']
    
class Leaderboard(models.Model):
  leaderboard_name = models.CharField(max_length=50, unique=True, blank=False, null=False)
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaderboards', blank=True)
  players = models.ManyToManyField(Player, related_name='leaderboards', blank=True)
  
  def __str__(self):
    return f'{self.leaderboard_name} ({self.user})'
  
  class Meta:
    ordering = ['user__username', 'leaderboard_name']
    
class SoloDuoLeaderboard(models.Model):
  leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE)
  player = models.ManyToManyField(Player, related_name='soloduoleaderboard')
  last_updated = models.DateTimeField(null=True, blank=True)
  tier = models.IntegerField()
  rank = models.IntegerField()
  lp = models.IntegerField()
  
  def __str__(self):
    return f'{self.player} {self.tier} {self.rank} {self.lp}'
  
  class Meta:
    ordering = ['leaderboard__leaderboard_name', '-tier', '-rank', '-lp']
    
class FlexLeaderboard(models.Model):
  leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE)
  player = models.ManyToManyField(Player, related_name='flexleaderboard')
  last_updated = models.DateTimeField(null=True, blank=True)
  tier = models.IntegerField()
  rank = models.IntegerField()
  lp = models.IntegerField()
  
  def __str__(self):
    return f'{self.player.name} {self.tier} {self.rank} {self.lp}'
  
  class Meta:
    ordering = ['leaderboard__leaderboard_name', '-tier', '-rank', '-lp']
    
class TftLeaderboard(models.Model):
  leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE)
  player = models.ManyToManyField(Player, related_name='tftleaderboard')
  last_updated = models.DateTimeField(null=True, blank=True)
  tier = models.IntegerField()
  rank = models.IntegerField()
  lp = models.IntegerField()
  
  def __str__(self):
    return f'{self.player.name} {self.tier} {self.rank} {self.lp}'
  
  class Meta:
    ordering = ['leaderboard__leaderboard_name', '-tier', '-rank', '-lp']
  