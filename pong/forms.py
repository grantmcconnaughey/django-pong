from collections import namedtuple

from django import forms
from django.core.exceptions import ValidationError

from .models import Game, Player


class GameForm(forms.ModelForm):

    class Meta:
        model = Game
        fields = ['player1', 'player2']

    def clean(self):
        cleaned_data = super(GameForm, self).clean()
        if cleaned_data['player1'] == cleaned_data['player2']:
            raise ValidationError('Player 1 and Player 2 cannot '
                                  'be the same person.')
        return cleaned_data


class MatchupForm(forms.Form):
    players = forms.ModelMultipleChoiceField(
        Player.objects.all(), label='Choose two players to compare:',
        widget=forms.CheckboxSelectMultiple)

    def clean_players(self):
        players = self.cleaned_data['players']
        if len(players) != 2:
            raise ValidationError('Select only 2 players to compare')
        return players

    def get_stats(self):
        Matchup = namedtuple('Matchup', ['player1', 'player2',
                                         'games_played', 'player1_win_percentage'])
        players = self.cleaned_data['players']
        player1 = players[0]
        player2 = players[1]

        games_played = player1.games_played_against(player2)
        games_played_count = games_played.count()
        if games_played_count == 0:
            player1_win_percentage = 0.0
        else:
            player1_win_percentage = round((games_played.filter(winner=player1).count() / (games_played_count * 1.0)) * 100, 2)

        return Matchup(player1, player2, games_played_count, player1_win_percentage)
