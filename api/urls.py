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
    path('movies/recommended/', recommended_movies_list, name='recommended-movies'),

    # **** RATINGS **** #
    # Ratings endpoint
    path('ratings/', ratings, name='ratings'),

    # Uncomment the following line to enable router URLs
    # path('', include(router.urls)),
]
