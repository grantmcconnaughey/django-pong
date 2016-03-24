import factory
from factory import DjangoModelFactory

from pong.models import Game, Player


class PlayerFactory(DjangoModelFactory):
    class Meta:
        model = Player

    name = 'Pong Player'


class GameFactory(DjangoModelFactory):
    class Meta:
        model = Game

    player1 = factory.SubFactory(PlayerFactory)
    player2 = factory.SubFactory(PlayerFactory)
