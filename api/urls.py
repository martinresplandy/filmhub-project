from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MovieViewSet, register, login, ratings

router = DefaultRouter()
router.register(r'movies', MovieViewSet)

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('ratings/', ratings, name='ratings'),
    path('', include(router.urls)),
]
