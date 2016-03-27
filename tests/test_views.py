from django.core.urlresolvers import reverse
from django.test import TestCase

from pong.forms import GameForm
from pong.models import Game, Point
from tests.factories import PlayerFactory, GameFactory


class GameViewTests(TestCase):

    def setUp(self):
        self.player1 = PlayerFactory(name='Player 1')
        self.player2 = PlayerFactory(name='Player 2')

    def test_index(self):
        url = reverse('pong_index')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_game_create_get(self):
        url = reverse('pong_game_create')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], GameForm)

    def test_game_create_makes_new_game(self):
        url = reverse('pong_game_create')
        data = {
            'player1': self.player1.pk,
            'player2': self.player2.pk,
        }

        response = self.client.post(url, data)

        game = Game.objects.get()
        self.assertEqual(game.player1, self.player1)
        self.assertEqual(game.player2, self.player2)
        self.assertIsNone(game.winner)
        self.assertIsNone(game.loser)
        self.assertIsNotNone(game.date)

    def test_game_create_redirects_to_game_detail(self):
        url = reverse('pong_game_create')
        data = {
            'player1': self.player1.pk,
            'player2': self.player2.pk,
        }

        response = self.client.post(url, data)

        game = Game.objects.get()
        expected_url = reverse('pong_game_detail', args=[game.pk])
        self.assertRedirects(response, expected_url)

    def test_game_create_cannot_use_same_player_for_both(self):
        url = reverse('pong_game_create')
        data = {
            'player1': self.player1.pk,
            'player2': self.player1.pk,
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        # No games were created
        self.assertFalse(Game.objects.exists())

    def test_game_detail_get(self):
        game = GameFactory()
        url = reverse('pong_game_detail', args=[game.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['game'], game)

    def test_add_point_post_adds_new_point_for_player_1(self):
        game = GameFactory()
        url = reverse('pong_add_point')
        data = {
            'game_id': game.pk,
            'player': '1',
        }

        response = self.client.post(url, data)

        self.assertEqual(Point.objects.count(), 1)
        point = Point.objects.get()
        self.assertEqual(point.game, game)
        self.assertEqual(point.player, game.player1)

    def test_add_point_post_adds_new_point_for_player_2(self):
        game = GameFactory()
        url = reverse('pong_add_point')
        data = {
            'game_id': game.pk,
            'player': '2',
        }

        response = self.client.post(url, data)

        self.assertEqual(Point.objects.count(), 1)
        point = Point.objects.get()
        self.assertEqual(point.game, game)
        self.assertEqual(point.player, game.player2)

    def test_add_point_post_400_error_if_player_not_1_or_2(self):
        game = GameFactory()
        url = reverse('pong_add_point')
        data = {
            'game_id': game.pk,
            'player': '3',
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 400)
