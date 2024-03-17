from django import forms

from .models import Leaderboard, Player, SoloDuoLeaderboard, FlexLeaderboard, TftLeaderboard

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
    
class FlexLeaderboardForm(forms.ModelForm):
  class Meta:
    model = FlexLeaderboard
    fields = '__all__'
    
class TftLeaderboardForm(forms.ModelForm):
  class Meta:
    model = TftLeaderboard
    fields = '__all__'