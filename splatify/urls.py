from django.urls import path
from .views import homepage, room, show_top_artists, splat, play

urlpatterns = [
    path('', homepage, name='homepage'),
    path('room', room, name='room'),
    path('topartists', show_top_artists, name='show_top'),
    path('splat/<int:user_id>', splat, name='splat'),
    path('play/<slug:playlist_id>', play, name='play')
]
