from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import recommended_movies_list_view, register_view, login_view, ratings_view, watch_list_view, movies_catalog_view, movies_search_view, watched_movies_view

# router = DefaultRouter() # Uncomment to enable router
# router.register(r'movies', MovieViewSet) # Example of registering a viewset

urlpatterns = [
    
    # **** USERS **** #

    # User registration
    path('register/', register_view, name='register'),

    # User login
    path('login/', login_view, name='login'),

    # **** MOVIES **** #
    
    # Movies catalog
    path('movies/', movies_catalog_view, name='movies-catalog'),

    # Movies search
    path('movies/search/', movies_search_view, name='movies-search'),

    # Watched movie endpoints
    path('movies/watched/', watched_movies_view, name='watched-movies'),

    # WatchList endpoints
    path('movies/watch_list/', watch_list_view, name='watch-list'),
    
    # Recommended Movies endpoints
    path('movies/recommended/', recommended_movies_list_view, name='recommended-movies'),

    # **** RATINGS **** #

    # Ratings endpoint
    path('ratings/', ratings_view, name='ratings'),
]