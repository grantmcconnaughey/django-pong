from django import forms
from django.core.exceptions import ValidationError

from .models import Game


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
