from django.conf.urls import include, url
from django.contrib import admin

from pong.urls import urlpatterns


urlpatterns += [
    url(r"^admin/", include(admin.site.urls)),
]
