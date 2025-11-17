from django.contrib import admin

from .models import Player, Leaderboard, SoloDuoLeaderboard, FlexLeaderboard, TftLeaderboard

# Register your models here.

class LeaderboardAdmin(admin.ModelAdmin):
  list_display = ('leaderboard_name', 'last_updated', 'player_name', 'tier', 'rank', 'lp')
  
  def leaderboard_name(self, obj):
    return obj.leaderboard.leaderboard_name
  
  def player_name(self, obj):
    try:
      player = obj.player.get()
      return player.name
    except Player.DoesNotExist:
      return '-'
    
class PlayerAdmin(admin.ModelAdmin):
  list_display = ('region', 'name', 'tag')
  
class LeaderboardA(admin.ModelAdmin):
  list_display = ('user', 'leaderboard_name')
  
admin.site.register(Player, PlayerAdmin)
admin.site.register(Leaderboard, LeaderboardA)
admin.site.register(SoloDuoLeaderboard, LeaderboardAdmin)
admin.site.register(FlexLeaderboard, LeaderboardAdmin)
admin.site.register(TftLeaderboard, LeaderboardAdmin)