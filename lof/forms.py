from django import forms

from .models import Leaderboard, Player, SoloDuoLeaderboard

class LeaderboardForm(forms.ModelForm):
  class Meta:
    model = Leaderboard
    fields = '__all__'
    
class PlayerForm(forms.ModelForm):
  class Meta:
    model = Player
    fields = '__all__'
    
class SoloDuoLeaderboardForm(forms.ModelForm):
  class Meta:
    model = SoloDuoLeaderboard
    fields = '__all__'