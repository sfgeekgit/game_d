from django.urls import path
from . import views

urlpatterns = [
    path('user/me/', views.get_or_create_user, name='get_or_create_user'),
    path('user/me/points/', views.add_points, name='add_points'),
    path('town/', views.get_town, name='get_town'),
    path('town/event/', views.trigger_town_event, name='trigger_town_event'),
]
