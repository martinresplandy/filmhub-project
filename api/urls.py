from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import recommended_movies_list_view, register_view, login_view, ratings_view, watch_list_view, movie_by_id_view, movies_catalog_view, movies_search_view

# router = DefaultRouter() # Uncomment to enable router
# router.register(r'movies', MovieViewSet) # Example of registering a viewset

urlpatterns = [
    # **** USERS **** #
    # User registration and login
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),

    # **** MOVIES **** #
    # Specific movie endpoints
    path('movie/', movie_by_id_view, name='watch-list'),
    
    # Movies catalog # to use the search functionality just add ?search=your_query to the url
    path('movies/', movies_catalog_view, name='movies-catalog'),

    # Movies search
    path('movies/search/', movies_search_view, name='movies-search'),  # Uncomment if a separate search view is created

    # WatchList endpoints
    path('movies/watch_list/', watch_list_view, name='watch-list'),
    
    # Recommended Movies endpoints
    path('movies/recommended/', recommended_movies_list_view, name='recommended-movies'),

    # **** RATINGS **** #
    # Ratings endpoint
    path('ratings/', ratings_view, name='ratings'),

    # Uncomment the following line to enable router URLs
    # path('', include(router.urls)),
    

    # JUST A COMMENT TO HELP USING CATALOG AND SEARCH FUNCTIONALITY (http://localhost:8000/api/...) ( you have to use the tokens in auth also)
    ## search by director: /movies/?search=director_name&search_type=director ( put Steven Spielberg or somehting in the director_name field)
    ## search by genre: /movies/?search=genre_name&search_type=genre ( put action or somehting in the genre_name field)
    ## search by title: /movies/?search=title&search_type=title ( put batman or somehting in the title field)

    ## catalog: /movies/ ( shows the catalog of movies with popular, top rated, action, comedy, drama)
]
