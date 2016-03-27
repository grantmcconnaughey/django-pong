from operator import attrgetter

from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView

from .forms import GameForm, MatchupForm
from .models import Game, Player


def index(request):
    games = Game.objects.all().order_by('-date')[:5]
    leaderboard = sorted(
        Player.objects.all(), key=attrgetter('win_percentage'), reverse=True)

    return render(request, 'pong/index.html', {
        'games': games,
        'leaderboard': leaderboard,
    })


class GameCreateView(CreateView):
    model = Game
    form_class = GameForm
    template_name = 'pong/game/create.html'

    def get_success_url(self):
        return reverse('pong_game_detail', args=[self.object.pk])


class GameDetailView(DetailView):
    model = Game
    template_name = 'pong/game/detail.html'


@require_POST
def add_point(request):
    player_number = request.POST['player']
    if str(player_number) not in ['1', '2']:
        return HttpResponseBadRequest()

    game = get_object_or_404(Game, pk=request.POST['game_id'])
    player = getattr(game, 'player%s' % player_number)
    game.add_point(player)

    data = {
        'game_over': game.game_over(),
        'player1_points': game.player1_points,
        'player2_points': game.player2_points,
    }

    return JsonResponse(data)


def create_matchup(request):
    stats = None
    if request.method == 'POST':
        form = MatchupForm(request.POST)
        if form.is_valid():
            stats = form.get_stats()
    else:
        form = MatchupForm()
    return render(request, 'pong/stats/create_matchup.html', {
        'form': form,
        'stats': stats,
    })


class PlayerDetailView(DetailView):
    model = Player
    template_name = 'pong/player/detail.html'
