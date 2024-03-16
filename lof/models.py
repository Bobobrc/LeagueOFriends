from django.db import models

# Create your models here.
class Player(models.Model):
  name = models.CharField(max_length = 100)
  puuid = models.CharField(max_length = 100)
  
  def __str__(self):
    return f'{self.name} {self.puuid}'
  
class Leaderboard(models.Model):
  leaderboard_name = models.CharField(max_length = 50, unique=True, blank=False, null=False)
  leaderboard_password = models.CharField(max_length = 50, blank=False, null=False)
  players = models.ManyToManyField(Player, related_name='leaderboards', blank=True)
  
  def __str__(self):
    return f'{self.leaderboard_name}'
  
class SoloDuoLeaderboard(models.Model):
  leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE)
  player = models.ManyToManyField(Player, related_name='soloduoleaderboards')
  tier = models.IntegerField()
  rank = models.IntegerField()
  lp = models.IntegerField()
  
  def __str__(self):
    return f'{self.player.name} {self.tier} {self.rank} {self.lp}'
  
class FlexLeaderboard(models.Model):
  leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE)
  player = models.ManyToManyField(Player, related_name='flexleaderboard')
  tier = models.IntegerField()
  rank = models.IntegerField()
  lp = models.IntegerField()
  
  def __str__(self):
    return f'{self.player.name} {self.tier} {self.rank} {self.lp}'
  
class TftLeaderboard(models.Model):
  leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE)
  player = models.ManyToManyField(Player,  related_name='tftleaderboard')
  tier = models.IntegerField()
  rank = models.IntegerField()
  lp = models.IntegerField()
  
  def __str__(self):
    return f'{self.player.name} {self.tier} {self.rank} {self.lp}'
