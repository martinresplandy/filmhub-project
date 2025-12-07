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
    delete_rating,
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

# ****  USER **** #

# Register view
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

# Login view
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
        rating, response_status = add_rating(request.user, request.data.get('external_movie_id'), request.data.get('score'), request.data.get('comment'))
        match response_status:
            case Status.SUCCESS:
                serializer = RatingSerializer(rating)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            case Status.ALREADY_EXISTS:
                return Response({'error': 'Rating for this movie already exists. Use PATCH to update.'}, status=status.HTTP_400_BAD_REQUEST)
            case Status.FAILURE:
                return Response({'error': 'Could not create rating. The data provided is wrong.'}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PATCH':
        rating, response_status = update_rating(request.user, request.data.get('rating_id'), request.data.get('new_score'), request.data.get('new_comment'))
        match response_status:
            case Status.SUCCESS:
                serializer = RatingSerializer(rating)
                return Response(serializer.data, status=status.HTTP_200_OK)
            case Status.NOT_FOUND:
                return Response({'error': 'Rating not found. Cannot update non-existing rating.'}, status=status.HTTP_404_NOT_FOUND)
            case Status.FAILURE:
                return Response({'error': 'Could not update rating. Check the data provided.'}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        rating, response_status = delete_rating(request.user, request.data.get('rating_id'))
        match response_status:
            case Status.SUCCESS:
                return Response({'message': f'Rating for movie "{rating.movie.title}" deleted successfully.'}, status=status.HTTP_200_OK)
            case Status.NOT_FOUND:
                return Response({'error': 'Rating not found. Cannot delete non-existing rating.'}, status=status.HTTP_404_NOT_FOUND)
            case Status.FAILURE:
                return Response({'error': 'Could not delete rating. Check the data provided.'}, status=status.HTTP_400_BAD_REQUEST)

# **** RECOMMENDED MOVIES **** #

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def recommended_movies_list_view(request):
    if request.method == 'GET':
        recommended, response_status = get_recommended_movies_for_user(request.user.userprofile)
        if response_status == Status.SUCCESS:
            serializer = MovieSerializer(recommended, many=True)
            return Response(serializer.data)
        return Response({'error': 'Could not fetch recommended movies.'}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'PATCH':
        recommended, response_status = update_recommendations(request.user.userprofile)
        if response_status == Status.SUCCESS:
            serializer = MovieSerializer(recommended, many=True)
            return Response(serializer.data)
        return Response({'error': 'Could not update recommendations.'}, status=status.HTTP_400_BAD_REQUEST)
        
# **** WATCHED MOVIES **** #

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def watched_movies_view(request):
    if request.method == 'GET':
        watched_movies, response_status = get_watched_movies_for_user(request.user.userprofile)
        if response_status == Status.SUCCESS:
            serializer = MovieSerializer(watched_movies, many=True)
            return Response(serializer.data)
        return Response({'error': 'Could not fetch watched movies.'}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'POST':
        movie, response_status = add_watched_movie(request.user.userprofile, request.data.get('external_id'))
        match response_status:
            case Status.SUCCESS:
                return Response({'message': f'Movie "{movie.title}" added to your watched movies.'}, status=status.HTTP_200_OK)
            case Status.ALREADY_EXISTS:
                return Response({'error': 'Movie already in your watched movies.'}, status=status.HTTP_400_BAD_REQUEST)
            case Status.FAILURE:
                return Response({'error': 'Movie not found.'}, status=status.HTTP_404_NOT_FOUND)
    elif request.method == 'DELETE':
        movie, response_status = remove_watched_movie(request.user.userprofile, request.data.get('external_id'))
        match response_status:
            case Status.SUCCESS:
                return Response({'message': f'Movie "{movie.title}" removed from your watched movies.'}, status=status.HTTP_200_OK)
            case Status.NOT_FOUND:
                return Response({'error': 'Movie not found in your watched movies.'}, status=status.HTTP_404_NOT_FOUND)
            case Status.FAILURE:
                return Response({'error': 'Movie not found.'}, status=status.HTTP_404_NOT_FOUND)

# **** WATCH LIST **** #

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def watch_list_view(request):
    if request.method == 'GET':
        watch_list_movies, response_status = get_watch_list_for_user(request.user.userprofile)
        if response_status == Status.SUCCESS:
            serializer = MovieSerializer(watch_list_movies, many=True)
            return Response(serializer.data)
        return Response({'error': 'Could not fetch watch list movies.'}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'POST':
        movie, response_status = add_watch_list_movie(request.user.userprofile, request.data.get('external_id'))
        match response_status:
            case Status.SUCCESS:
                return Response({'message': f'Movie "{movie.title}" added to your watch list.'}, status=status.HTTP_200_OK)
            case Status.ALREADY_EXISTS:
                return Response({'error': 'Movie already in your watch list.'}, status=status.HTTP_400_BAD_REQUEST)
            case Status.FAILURE:
                return Response({'error': 'Movie not found.'}, status=status.HTTP_404_NOT_FOUND)
    elif request.method == 'DELETE':
        movie, response_status = remove_watch_list_movie(request.user.userprofile, request.data.get('external_id'))
        match response_status:
            case Status.SUCCESS:
                return Response({'message': f'Movie "{movie.title}" removed from your watch list.'}, status=status.HTTP_200_OK)
            case Status.NOT_FOUND:
                return Response({'error': 'Movie not found in your watch list.'}, status=status.HTTP_404_NOT_FOUND)
            case Status.FAILURE:
                return Response({'error': 'Movie not found.'}, status=status.HTTP_404_NOT_FOUND)
    
# **** MOVIE BY ID **** #

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def movie_by_id_view(request):
    external_id = request.data.get('external_id')
    if not external_id:
        return Response({'error': 'external_id parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # This will fetch from API if movie doesn't exist in database
    movie, response_status = get_or_create_movie_from_external_id(external_id)
    if response_status == Status.SUCCESS:
        serializer = MovieSerializer(movie)
        return Response(serializer.data)
    return Response({'error': 'Movie not found.'}, status=status.HTTP_404_NOT_FOUND)

# **** MOVIES CATALOG **** #

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def movies_catalog_view(request):
    catalog, response_status = movies_catalog()
    if response_status == Status.SUCCESS:
        return Response(catalog)
    return Response({'error': 'Could not fetch movie catalog.'}, status=status.HTTP_400_BAD_REQUEST)
    

# **** MOVIES SEARCH **** #

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def movies_search_view(request):
    search = request.data.get('search', '')
    search_type = request.data.get('search_type', 'title')
    movies_searched, response_status = movies_search(search, search_type)
    if response_status == Status.SUCCESS:
        serializer = MovieSerializer(movies_searched, many=True)
        return Response(serializer.data)
    return Response({'error': 'Could not perform search.'}, status=status.HTTP_400_BAD_REQUEST)
