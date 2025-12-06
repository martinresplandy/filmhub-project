from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import recommended_movies_list, register, login, ratings, watch_list, movie_by_id, movies_catalog

# router = DefaultRouter() # Uncomment to enable router
# router.register(r'movies', MovieViewSet) # Example of registering a viewset

urlpatterns = [
    # **** USERS **** #
    # User registration and login
    path('register/', register, name='register'),
    path('login/', login, name='login'),

    # **** MOVIES **** #
    # Specific movie endpoints
    path('movie/', movie_by_id, name='watch-list'),
    
    # Movies catalog # to use the search functionality just add ?search=your_query to the url
    path('movies/', movies_catalog, name='movies-catalog'),

    # WatchList endpoints
    path('movies/watch_list/', watch_list, name='watch-list'),
    
    # Recommended Movies endpoints
    path('movies/recommended/', recommended_movies_list, name='recommended_movies'),

    # **** RATINGS **** #
    # Ratings endpoint
    path('ratings/', ratings, name='ratings'),

    # Uncomment the following line to enable router URLs
    # path('', include(router.urls)),
    

    # JUST A COMMENT TO HELP USING CATALOG AND SEARCH FUNCTIONALITY (http://localhost:8000/api/...) ( you have to use the tokens in auth also)
    ## search by director: /movies/?search=director_name&search_type=director ( put Steven Spielberg or somehting in the director_name field)
    ## search by genre: /movies/?search=genre_name&search_type=genre ( put action or somehting in the genre_name field)
    ## search by title: /movies/?search=title&search_type=title ( put batman or somehting in the title field)

    ## catalog: /movies/ ( shows the catalog of movies with popular, top rated, action, comedy, drama)
]
