from django.urls import path
from . import views

urlpatterns = [
    path('genre_search/', views.genre_search, name='genre_search'),

]
