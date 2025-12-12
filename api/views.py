from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
import requests

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes

from api.validators.normal import get_or_create_movie_from_external_id
from .models import Movie, Rating, UserProfile
from .serializers import UserSerializer, MovieSerializer, RatingSerializer
from .utils import (
    Status,
    register_user,
    login_user,
    get_all_ratings_for_user,
    add_rating,
    update_rating,
    get_recommended_movies_for_user,
    update_recommendations,
    get_watched_movies_for_user,
    add_watched_movie,
    remove_watched_movie,
    get_watch_list_for_user,
    add_watch_list_movie,
    remove_watch_list_movie,
    movies_catalog,
    movies_search,
)

from django.shortcuts import render

# **** INDEX / HOME **** #
def index(request):
    return render(request, 'index.html')

# ****  USER **** #

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = UserSerializer(data=request.data)
    registered_user, response_status = register_user(serializer)
    if response_status == Status.SUCCESS:
        token, created = Token.objects.get_or_create(user=registered_user)
        return Response({
            'token': token.key,
            'user': UserSerializer(registered_user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        loggedin_user, response_status = login_user(username, password)
        if response_status == Status.SUCCESS:
            token, created = Token.objects.get_or_create(user=loggedin_user)
            return Response({
                'token': token.key,
                'user': UserSerializer(loggedin_user).data
            })
        return Response({'error': 'Invalid Credentials!'}, status=status.HTTP_401_UNAUTHORIZED)

# ****  RATING **** #

@api_view(['GET', 'POST', 'PATCH'])
@permission_classes([IsAuthenticated])
def ratings_view(request):
    if request.method == 'GET':
        ratings, response_status = get_all_ratings_for_user(request.user)
        if response_status == Status.SUCCESS:
            serializer = RatingSerializer(ratings, many=True)
            return Response(serializer.data)
        return Response({'error': 'Could not fetch ratings.'}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'POST':
        # Get movie external_id from request
        movie_external_id = request.data.get('movie')
        
        if not movie_external_id:
            return Response({'error': 'Movie ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Try to get existing movie first
        try:
            movie = Movie.objects.get(external_id=movie_external_id)
        except Movie.DoesNotExist:
            # Create movie if it doesn't exist
            result = get_or_create_movie_from_external_id(movie_external_id)
            
            # Check if result is a tuple (movie, created) or just movie
            if isinstance(result, tuple):
                movie = result[0]
            else:
                movie = result
            
            if not movie:
                return Response({'error': 'Could not find or create movie.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if rating already exists
        existing_rating = Rating.objects.filter(
            user=request.user,
            movie=movie
        ).first()
        
        if existing_rating:
            return Response(
                {'error': 'Rating for this movie already exists. Use PATCH to update.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the rating directly
        score = request.data.get('score')
        comment = request.data.get('comment', '')
        
        # Validate score
        try:
            score = int(score)
            if score < 1 or score > 10:
                return Response(
                    {'error': 'Score must be between 1 and 10.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid score value.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create rating - Django ForeignKey needs the actual model instance
        try:
            rating = Rating.objects.create(
                user=request.user,
                movie=movie,  # Pass the movie object, Django will extract the FK
                score=score,
                comment=comment
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to create rating: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        update_recommendations(request.user.userprofile)
        serializer = RatingSerializer(rating)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    elif request.method == 'PATCH':
        # Get movie external_id from request
        movie_external_id = request.data.get('movie')
        
        if not movie_external_id:
            return Response({'error': 'Movie ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create movie
        movie = get_or_create_movie_from_external_id(movie_external_id)
        
        if not movie:
            return Response({'error': 'Could not find or create movie.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Find existing rating
        try:
            rating = Rating.objects.get(user=request.user, movie=movie)
        except Rating.DoesNotExist:
            return Response(
                {'error': 'Rating not found. Cannot update non-existing rating.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update rating
        score = request.data.get('score')
        comment = request.data.get('comment', rating.comment)
        
        # Validate score
        try:
            score = int(score)
            if score < 1 or score > 10:
                return Response(
                    {'error': 'Score must be between 1 and 10.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid score value.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rating.score = score
        rating.comment = comment
        rating.save()
        update_recommendations(request.user.userprofile)
        serializer = RatingSerializer(rating)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def recommended_movies_list_view(request):
    if request.method == 'GET':
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=request.user)
        
        recommended, response_status = get_recommended_movies_for_user(user_profile)
        if response_status == Status.SUCCESS:
            serializer = MovieSerializer(recommended, many=True)
            return Response(serializer.data)
        return Response({'error': 'Could not fetch recommended movies.'}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PATCH':
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=request.user)
        
        recommended = update_recommendations(user_profile)
        serializer = MovieSerializer(recommended, many=True)
        return Response(serializer.data)

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def watched_movies_view(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'GET':
        watched_movies = get_watched_movies_for_user(user_profile)
        serializer = MovieSerializer(watched_movies, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        external_id = request.data.get('external_id')
        if not external_id:
            return Response({'error': 'external_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        movie = add_watched_movie(user_profile, external_id)
        if movie:
            return Response({'message': f'Movie "{movie.title}" added to your watched movies.'}, status=status.HTTP_200_OK)
        return Response({'error': 'Movie not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    elif request.method == 'DELETE':
        external_id = request.data.get('external_id')
        if not external_id:
            return Response({'error': 'external_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        movie, response_status = remove_watched_movie(user_profile, external_id)
        if response_status == Status.SUCCESS:
            return Response({'message': f'Movie "{movie.title}" removed from your watched movies.'}, status=status.HTTP_200_OK)
        elif response_status == Status.NOT_FOUND:
            return Response({'error': 'Movie not found in your watched movies.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Movie not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def watch_list_view(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'GET':
        watch_list_movies, response_status = get_watch_list_for_user(user_profile)
        if response_status == Status.SUCCESS:
            serializer = MovieSerializer(watch_list_movies, many=True)
            return Response(serializer.data)
        return Response({'error': 'Could not fetch watch list movies.'}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'POST':
        external_id = request.data.get('external_id')
        if not external_id:
            return Response({'error': 'external_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        movie, response_status = add_watch_list_movie(user_profile, external_id)
        if response_status == Status.SUCCESS:
            return Response({'message': f'Movie "{movie.title}" added to your watch list.'}, status=status.HTTP_200_OK)
        elif response_status == Status.ALREADY_EXISTS:
            return Response({'error': 'Movie already in your watch list.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Movie not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    elif request.method == 'DELETE':
        external_id = request.data.get('external_id')
        if not external_id:
            return Response({'error': 'external_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        movie, response_status = remove_watch_list_movie(user_profile, external_id)
        if response_status == Status.SUCCESS:
            return Response({'message': f'Movie "{movie.title}" removed from your watch list.'}, status=status.HTTP_200_OK)
        elif response_status == Status.NOT_FOUND:
            return Response({'error': 'Movie not found in your watch list.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Movie not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def movies_catalog_view(request):
    search = request.query_params.get('search', '').strip()
    search_type = request.query_params.get('search_type', 'title').strip().lower()
    
    # If no search query, return catalog
    if not search:
        catalog, response_status = movies_catalog(True)
        if response_status == Status.SUCCESS:
            return Response(catalog)
        return Response({'error': 'Could not fetch movie catalog.'}, status=status.HTTP_400_BAD_REQUEST)
    
    movies_searched, response_status = movies_search(search, search_type)
    if response_status == Status.SUCCESS:
        return Response(movies_searched)
    return Response({'error': 'Could not perform search.'}, status=status.HTTP_400_BAD_REQUEST)