from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import recommended_movies_list, recommended_movies_update, register, login, ratings, watch_list

# router = DefaultRouter() # Uncomment to enable router
# router.register(r'movies', MovieViewSet) # Example of registering a viewset

urlpatterns = [
    # User registration and login
    path('register/', register, name='register'),
    path('login/', login, name='login'),

    # WatchList endpoints
    path('movies/watch_list/', watch_list, name='watch-list'),
    
    # Recommended Movies endpoints
    path('movies/recommended/', recommended_movies_list, name='recommended-movies'),
    path('movies/recommended/update/', recommended_movies_update, name='updated-recommended-movies'),

    # Ratings endpoint
    path('ratings/', ratings, name='ratings'),

    # Uncomment the following line to enable router URLs
    # path('', include(router.urls)),
]
