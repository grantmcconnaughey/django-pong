from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Player(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('pong_player_detail', args=[self.pk])

    @property
    def games_played(self):
        return Game.objects.filter(Q(player1=self) | Q(player2=self))

    def games_played_against(self, other_player):
        return Game.objects.filter(Q(player1=self, player2=other_player) |
                                   Q(player1=other_player, player2=self))\
                           .filter(winner__isnull=False)

    @property
    def win_percentage(self):
        # Only include completed games
        games_played = self.games_played.filter(winner__isnull=False).count()
        if games_played == 0:
            return 0.0

        wins = self.wins.all().count()
        return round((wins / (games_played * 1.0)) * 100.0, 2)


@python_2_unicode_compatible
class Game(models.Model):
    player1 = models.ForeignKey('pong.Player', related_name='+')
    player2 = models.ForeignKey('pong.Player', related_name='+')
    winner = models.ForeignKey('pong.Player', null=True, blank=True, related_name='wins')
    loser = models.ForeignKey('pong.Player', null=True, blank=True, related_name='losses')
    date = models.DateTimeField(auto_now_add=True)

    POINTS_TO_WIN = 11
    MUST_WIN_BY = 2

    def __str__(self):
        return '{} vs. {}'.format(self.player1, self.player2)

    def get_absolute_url(self):
        return reverse('pong_game_detail', args=[self.pk])

    @property
    def player1_points(self):
        return Point.objects.filter(game=self, player=self.player1).count()

    @property
    def player2_points(self):
        return Point.objects.filter(game=self, player=self.player2).count()

    @property
    def winning_score(self):
        return max([self.player1_points, self.player2_points])

    @property
    def losing_score(self):
        return min([self.player1_points, self.player2_points])

    def get_winner(self):
        if (self.player1_points >= self.POINTS_TO_WIN and
                self.player1_points - self.player2_points >= self.MUST_WIN_BY):
            return self.player1
        elif (self.player2_points >= self.POINTS_TO_WIN and
                self.player2_points - self.player1_points >= self.MUST_WIN_BY):
            return self.player2
        else:
            return None

    def add_point(self, player):
        """
        Adds a point to the game and marks the winner/loser if this is the
        last point in the game.
        """
        if self.game_over():
            return
        next_point = Point.objects.filter(game=self).count() + 1
        point = Point.objects.create(game=self, player=player, order=next_point)

        winner = self.get_winner()
        if winner:
            self.winner = winner
            self.loser = self.player2 if winner == self.player1 else self.player1
            self.save()

        return point

    def game_over(self):
        return bool(self.winner)

    def game_went_to_deuce(self):
        """
        Games go to deuce if both players have scores above POINTS_TO_WIN - 1.
        For instance, if games go to 11 points and both players have 10 or
        more points, then the game went to deuce.
        """
        return (self.player1_points >= self.POINTS_TO_WIN - 1 and
                self.player2_points >= self.POINTS_TO_WIN - 1)


@python_2_unicode_compatible
class Point(models.Model):
    player = models.ForeignKey('pong.Player')
    game = models.ForeignKey('pong.Game')
    order = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return 'Point to {} in game {}'.format(self.player, self.game)

    class Meta:
        index_together = (
            ('player', 'game'),
        )
