from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView

from .forms import GameForm
from .models import Game, Player


def index(request):
    games = Game.objects.all().order_by('-date')[:10]

    return render(request, 'pong/index.html', {
        'games': games,
    })


class GameCreateView(CreateView):
    model = Game
    form_class = GameForm
    context_object_name = 'games'
    template_name = 'pong/game/create.html'

    def get_success_url(self):
        return reverse('pong_game_detail', args=[self.object.pk])


class GameDetailView(DetailView):
    model = Game
    template_name = 'pong/game/detail.html'


@require_POST
def add_point(request):
    game = get_object_or_404(Game, pk=request.POST['game_id'])
    player = getattr(game, 'player%s' % request.POST['player'])
    game.add_point(player)

    game_over = game.game_over()
    winner = None
    loser = None
    if game_over:
        game.refresh_from_db()
        winner = game.winner
        loser = game.loser

    data = {
        'game_over': game.game_over(),
        'player1_points': game.player1_points,
        'player2_points': game.player2_points,
    }

    return JsonResponse(data)

