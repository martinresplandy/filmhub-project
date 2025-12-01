from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
import requests
import time

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes

from .validators import get_or_create_movie_from_external_id
from .models import Movie, Rating, UserProfile, API_BASE_URL, API_KEY
from .serializers import UserSerializer, MovieSerializer, RatingSerializer
from .permissions import IsSuperUserOrReadOnly

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

@api_view(['GET', 'POST', 'UPDATE'])
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
    
    elif request.method == 'UPDATE':
        # TODO: Implement update logic for ratings
        serializer = RatingSerializer(data=request.data)
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
        user_profile.watch_list.add(movie)
        return Response({'message': f'Movie "{movie.title}" added to your watch list.'}, status=status.HTTP_200_OK)

# **** RECOMMENDED MOVIES **** #

@api_view(['GET', 'UPDATE'])
@permission_classes([IsAuthenticated])
def recommended_movies_list(request):
    if request.method == 'GET':
        user_profile = request.user.userprofile
        recommended = user_profile.recommended_movies.all()
        serializer = MovieSerializer(recommended, many=True)
        return Response(serializer.data)
    elif request.method == 'UPDATE':
        user_profile = request.user.userprofile
        user_profile.update_recommendations()
        recommended = user_profile.recommended_movies.all()
        serializer = MovieSerializer(recommended, many=True)
        return Response(serializer.data)
    
# **** MOVIE BY ID **** #
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def movie_by_id(request):
    external_id = request.data.get('external_id')
    if not external_id:
        return Response({'error': 'external_id parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    movie = get_or_create_movie_from_external_id(external_id)
    if not movie:
        return Response({'error': 'Movie not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = MovieSerializer(movie)
    return Response(serializer.data)

# **** MOVIES CATALOG **** #
GENRE_MAP = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy",
    80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family",
    14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music",
    9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
    10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western",
}

# This view is used to get the movies catalog or search 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def movies_catalog(request):
    search_query = request.GET.get('search', '').strip()

    # We need to decide how many pages we want to search , beacuse if it is like a genre it will have lots and lots of movies
    if search_query:
        url = f"{API_BASE_URL}/search/movie"
        params = {"api_key": API_KEY, "query": search_query, "page": 1}
        response = requests.get(url, params=params)
        data = response.json()
        all_results = data.get('results', [])
        
        result = []
        for movie in all_results:
            genre_ids = movie.get('genre_ids', [])
            genres = [GENRE_MAP.get(gid, "Unknown") for gid in genre_ids]
            release_date = movie.get('release_date', '')
            year = int(release_date.split('-')[0]) if release_date else None
            poster_path = movie.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/w185{poster_path}" if poster_path else None
            
            result.append({
                "external_id": movie.get('id'),
                "title": movie.get('title', ''),
                "poster_url": poster_url,
                "genre": ", ".join(genres) if genres else "Unknown",
                "year": year,
                "average_rating": round(movie.get('vote_average', 0), 1),
            })
        return Response(result)
    
    all_movies = []
    for page in range(1, 6):
        url = f"{API_BASE_URL}/movie/popular"
        params = {"api_key": API_KEY, "page": page}
        response = requests.get(url, params=params)
        data = response.json()
        all_movies.extend(data.get('results', []))
        if len(all_movies) >= 100:
            break
    
    result = []
    for movie in all_movies[:100]:
        genre_ids = movie.get('genre_ids', [])
        genres = [GENRE_MAP.get(gid, "Unknown") for gid in genre_ids]
        release_date = movie.get('release_date', '')
        year = int(release_date.split('-')[0]) if release_date else None
        poster_path = movie.get('poster_path')
        poster_url = f"https://image.tmdb.org/t/p/w185{poster_path}" if poster_path else None
        
        result.append({
            "external_id": movie.get('id'),
            "title": movie.get('title', ''),
            "poster_url": poster_url,
            "genre": ", ".join(genres) if genres else "Unknown",
            "year": year,
            "average_rating": round(movie.get('vote_average', 0), 1),
        })
    
    return Response(result)
