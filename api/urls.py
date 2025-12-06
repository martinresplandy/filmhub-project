from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    recommended_movies_list_view, 
    register_view, 
    login_view, 
    ratings_view, 
    watch_list_view, 
    watched_movies_view,
    movies_catalog_view
)

urlpatterns = [
    # **** USERS **** #
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),

    # **** MOVIES **** #
    path('movies/', movies_catalog_view, name='movies-catalog'),
    
    # WatchList endpoints
    path('movies/watch_list/', watch_list_view, name='watch-list'),
    
    # Watched movies endpoints
    path('movies/watched/', watched_movies_view, name='watched-movies'),
    
    # Recommended Movies endpoints
    path('recommended_movies/', recommended_movies_list_view, name='recommended-movies'),

    # **** RATINGS **** #
    path('ratings/', ratings_view, name='ratings'),
]