from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes
from .models import Movie, Rating
from .serializers import UserSerializer, MovieSerializer, RatingSerializer
from .permissions import IsSuperUserOrReadOnly

# View to register new user
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
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

# Ratings view
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def ratings(request):
    if request.method == 'GET':
        ratings = Rating.objects.filter(user=request.user)
        serializer = RatingSerializer(ratings, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            # Prevent users from rating the same movie multiple times
            if (Rating.objects.filter(user=request.user, movie=serializer.validated_data['movie']).exists()):
                return Response({'error': 'You have already rated this movie.'}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Viewsets for Movie
class MovieViewSet(viewsets.ModelViewSet):
    # Check if the user is well logged in.
    authentication_classes = [TokenAuthentication]
    # Give access only to authenticated users.
    permission_classes = [IsSuperUserOrReadOnly]

    queryset = Movie.objects.all()
    serializer_class = MovieSerializer