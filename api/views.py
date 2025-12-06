from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
import requests

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes

from .validators import get_or_create_movie_from_external_id, get_or_search_movie_from_external_id
from .models import Movie, Rating, UserProfile
from .serializers import UserSerializer, MovieSerializer, RatingSerializer
from .permissions import IsSuperUserOrReadOnly
from .utils import (
    update_recommendations, 
    API_BASE_URL, 
    API_KEY, 
    format_movie, 
    fetch_movies, 
    search_by_director, 
    search_by_genre
)

# ****  USER **** #

# Register view
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        UserProfile.objects.create(user=user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Login view
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })
    return Response({'error': 'Invalid Credentials!'}, status=status.HTTP_401_UNAUTHORIZED)

# ****  RATING **** #

@api_view(['GET', 'POST', 'PATCH'])
@permission_classes([IsAuthenticated])
def ratings(request):
    if request.method == 'GET':
        ratings = Rating.objects.filter(user=request.user)
        serializer = RatingSerializer(ratings, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Check if the movie exists
        external_id = request.data.get('movie')
        movie = get_or_create_movie_from_external_id(external_id)
        if not movie:
            return Response({'error': 'Movie not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Prevent users from rating the same movie multiple times
        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            movie_obj = serializer.validated_data['movie']
            if (Rating.objects.filter(user=request.user, movie=movie_obj).exists()):
                return Response({'error': 'You have already rated this movie.'}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PATCH':
        # Update existing rating by movie external_id
        movie_external_id = request.data.get('movie')
        if not movie_external_id:
            return Response({'error': 'Movie external_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            rating = Rating.objects.get(id=rating_id, user=request.user)
        except Rating.DoesNotExist:
            return Response({'error': 'Rating not found. You need to create a rating first using POST.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RatingSerializer(rating, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# **** WATCHED MOVIES **** #

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def watched_movies(request):
    if request.method == 'GET':
        user_profile = request.user.userprofile
        watched_movies = user_profile.watched_movies.all()
        serializer = MovieSerializer(watched_movies, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        movie_id = request.data.get('external_id')
        movie = get_or_create_movie_from_external_id(movie_id)
        if not movie:
            return Response({'error': 'Movie not found.'}, status=status.HTTP_404_NOT_FOUND)
        user_profile = request.user.userprofile
        # Check if movie is already in watched movies
        if user_profile.watched_movies.filter(pk=movie.pk).exists():
            return Response({'error': 'Movie already in your watched movies.'}, status=status.HTTP_400_BAD_REQUEST)
        user_profile.watched_movies.add(movie)
        return Response({'message': f'Movie "{movie.title}" added to your watched movies.'}, status=status.HTTP_200_OK)

# **** WATCH LIST **** #

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def watch_list(request):
    if request.method == 'GET':
        user_profile = request.user.userprofile
        watch_list_movies = user_profile.watch_list.all()
        serializer = MovieSerializer(watch_list_movies, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        movie = get_or_create_movie_from_external_id(request.data.get('external_id'))
        if not movie:
            return Response({'error': 'Movie not found.'}, status=status.HTTP_404_NOT_FOUND)
        user_profile = request.user.userprofile
        # Check if movie is already in watch list
        if user_profile.watch_list.filter(pk=movie.pk).exists():
            return Response({'error': 'Movie already in your watch list.'}, status=status.HTTP_400_BAD_REQUEST)
        user_profile.watch_list.add(movie)
        return Response({'message': f'Movie "{movie.title}" added to your watch list.'}, status=status.HTTP_200_OK)

# **** RECOMMENDED MOVIES **** #

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def recommended_movies_list(request):
    if request.method == 'GET':
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        recommended = user_profile.recommended_movies.all()
        serializer = MovieSerializer(recommended, many=True)
        return Response(serializer.data)
    elif request.method == 'UPDATE':
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        recommended = user_profile.update_recommendations()
        serializer = MovieSerializer(recommended, many=True)
        return Response(serializer.data)
    
# **** MOVIE BY ID **** #
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def movie_by_id(request):
    external_id = request.data.get('external_id')
    if not external_id:
        return Response({'error': 'external_id parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # This will fetch from API if movie doesn't exist in database
    movie = get_or_create_movie_from_external_id(external_id)
    if not movie:
        return Response({'error': 'Movie not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = MovieSerializer(movie)
    return Response(serializer.data)

# **** MOVIES CATALOG **** #

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def movies_catalog(request):
    search = request.GET.get('search', '').strip()
    search_type = request.GET.get('search_type', 'title').strip().lower()

    # handle search
    if search:
        if search_type == 'director':
            movies = search_by_director(search)
        elif search_type == 'genre':
            movies = search_by_genre(search)
        else:
            # default is title search
            url = f"{API_BASE_URL}/search/movie"
            params = {"api_key": API_KEY, "query": search, "page": 1}
            movies = fetch_movies(url, params, limit=20)
        
        return Response(movies)
    
    # return catalog with different sections
    catalog = {}
    
    # popular movies
    url = f"{API_BASE_URL}/movie/popular"
    params = {"api_key": API_KEY, "page": 1}
    catalog["popular"] = fetch_movies(url, params, limit=20)
    
    # top rated
    url = f"{API_BASE_URL}/movie/top_rated"
    params = {"api_key": API_KEY, "page": 1}
    catalog["top_rated"] = fetch_movies(url, params, limit=20)
    
    # action
    url = f"{API_BASE_URL}/discover/movie"
    params = {"api_key": API_KEY, "with_genres": 28, "sort_by": "popularity.desc", "page": 1}
    catalog["action"] = fetch_movies(url, params, limit=20)
    
    # comedy
    url = f"{API_BASE_URL}/discover/movie"
    params = {"api_key": API_KEY, "with_genres": 35, "sort_by": "popularity.desc", "page": 1}
    catalog["comedy"] = fetch_movies(url, params, limit=20)
    
    # drama
    url = f"{API_BASE_URL}/discover/movie"
    params = {"api_key": API_KEY, "with_genres": 18, "sort_by": "popularity.desc", "page": 1}
    catalog["drama"] = fetch_movies(url, params, limit=20)
    
    return Response(catalog)