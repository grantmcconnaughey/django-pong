from django.conf.urls import url

from . import views


urlpatterns = [
    # Game URLs
    url(r'^$', views.index, name='pong_index'),
    url(r'^create/$', views.GameCreateView.as_view(), name='pong_game_create'),
    url(r'^detail/(?P<pk>\d+)/$', views.GameDetailView.as_view(), name='pong_game_detail'),
    url(r'^add_point/$', views.add_point, name='pong_add_point'),

    # Player URLs
    url(r'^player/detail/(?P<pk>\d+)/$',
        views.PlayerDetailView.as_view(),
        name='pong_player_detail'),
]
