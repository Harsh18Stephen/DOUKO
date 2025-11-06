from django.urls import path
from . import views

from django.urls import path
from . import views

from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("room/<str:code>/", views.room, name="room"),                # Lobby / room view
    path("game/<str:code>/", views.game, name="game"),                # Active game
    path("result/<str:code>/", views.result_view, name="result_view"),# Result page
    path("start_game/<str:code>/", views.start_game, name="start_game"),
    path("solved/", views.solved_list, name="solved_list"),

    
    # API endpoints
    path('api/room/<str:code>/status/', views.room_status, name='room_status'),
    path('api/room/<str:code>/submit/', views.submit_solution, name='submit_solution'),
]






