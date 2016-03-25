from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.views.generic import CreateView, DetailView

from .forms import GameForm
from .models import Game


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

