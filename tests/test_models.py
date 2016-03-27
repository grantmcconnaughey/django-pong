#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase

from pong.models import Game, Player, Point

from .factories import PlayerFactory, GameFactory


class PlayerModelTests(TestCase):

    def test_str_returns_name(self):
        player = PlayerFactory(name='Grant McConnaughey')

        self.assertEqual(str(player), 'Grant McConnaughey')

    def test_games_played_none(self):
        player = PlayerFactory(name='Grant McConnaughey')

        self.assertEqual(list(player.games_played), [])

    def test_games_played_when_player1(self):
        player = PlayerFactory(name='Grant McConnaughey')
        game1 = GameFactory(player1=player)
        game2 = GameFactory(player1=player)

        self.assertEqual(len(player.games_played), 2)

    def test_games_played_when_player2(self):
        player = PlayerFactory(name='Grant McConnaughey')
        game1 = GameFactory(player2=player)
        game2 = GameFactory(player2=player)

        self.assertEqual(len(player.games_played), 2)

    def test_games_played_when_mixed(self):
        player = PlayerFactory(name='Grant McConnaughey')
        GameFactory(player1=player)
        GameFactory(player1=player)
        GameFactory(player2=player)
        GameFactory(player2=player)
        GameFactory()
        GameFactory()

        self.assertEqual(len(player.games_played), 4)

    def test_win_percentage(self):
        player = PlayerFactory()
        GameFactory(player1=player, winner=player)
        GameFactory(player1=player, winner=player)
        GameFactory(player1=player, winner=player)
        GameFactory(player1=player, loser=player)
        GameFactory(player1=player, loser=player)

        self.assertEqual(player.win_percentage, 60.0)

    def test_win_percentage_no_wins(self):
        player = PlayerFactory()
        GameFactory(player1=player, loser=player)
        GameFactory(player1=player, loser=player)

        self.assertEqual(player.win_percentage, 0.0)

    def test_win_percentage_no_games(self):
        player = PlayerFactory()

        self.assertEqual(player.win_percentage, 0.0)

    def test_win_percentage_all_wins(self):
        player = PlayerFactory()
        GameFactory(player1=player, winner=player)
        GameFactory(player1=player, winner=player)
        GameFactory(player1=player, winner=player)

        self.assertEqual(player.win_percentage, 100.0)


class GameModelTests(TestCase):

    def setUp(self):
        self.player1 = PlayerFactory(name='Player 1')
        self.player2 = PlayerFactory(name='Player 2')
        self.game = GameFactory(player1=self.player1, player2=self.player2)

    def test_str(self):
        self.assertEqual(str(self.game), 'Player 1 vs. Player 2')

    def test_player1_points_None(self):
        self.assertEqual(self.game.player1_points, 0)

    def test_player1_points(self):
        self.game.add_point(self.player1)
        self.game.add_point(self.player1)
        self.game.add_point(self.player1)
        self.game.add_point(self.player2)
        self.game.add_point(self.player2)

        self.assertEqual(self.game.player1_points, 3)

    def test_player2_points_None(self):
        self.assertEqual(self.game.player2_points, 0)

    def test_player2_points(self):
        self.game.add_point(self.player2)
        self.game.add_point(self.player2)
        self.game.add_point(self.player2)
        self.game.add_point(self.player1)
        self.game.add_point(self.player1)

        self.assertEqual(self.game.player2_points, 3)

    def test_add_point_creates_first_point(self):
        self.game.add_point(self.player1)

        point = Point.objects.get()

        self.assertEqual(point.game, self.game)
        self.assertEqual(point.player, self.player1)
        self.assertEqual(point.order, 1)

    def test_add_point_creates_last_point(self):
        for i in range(11):
            self.game.add_point(self.player1)

        self.assertEqual(Point.objects.count(), 11)
        self.assertEqual(Point.objects.filter(game=self.game).count(), 11)
        self.assertEqual(Point.objects.filter(game=self.game, order=0).count(), 0)
        self.assertEqual(Point.objects.filter(game=self.game, order=1).count(), 1)
        self.assertEqual(Point.objects.filter(game=self.game, order=2).count(), 1)
        self.assertEqual(Point.objects.filter(game=self.game, order=3).count(), 1)
        self.assertEqual(Point.objects.filter(game=self.game, order=10).count(), 1)
        self.assertEqual(Point.objects.filter(game=self.game, order=11).count(), 1)
        self.assertEqual(Point.objects.filter(game=self.game, order=12).count(), 0)

    def test_add_point_marks_winner_and_loser(self):
        for i in range(Game.POINTS_TO_WIN):
            self.game.add_point(self.player1)

        game = Game.objects.get(pk=self.game.pk)
        self.assertEqual(game.winner, self.player1)
        self.assertEqual(game.loser, self.player2)

    def test_add_point_will_not_create_new_point_if_game_is_over(self):
        for i in range(Game.POINTS_TO_WIN):
            self.game.add_point(self.player1)

        self.assertTrue(self.game.game_over())

        # Game is over. add_point will not add any more points to this game.
        self.assertEqual(Point.objects.count(), 11)
        self.game.add_point(self.player2)
        self.game.add_point(self.player2)
        self.assertEqual(Point.objects.count(), 11)
