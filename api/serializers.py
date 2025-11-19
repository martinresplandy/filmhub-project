from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Movie, Rating
from django.db.models import Avg

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class MovieSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'genre', 'year', 'average_rating']

    def get_average_rating(self, obj):
        # Calcula a média de ratings para o filme
        avg = obj.rating_set.aggregate(Avg('score'))['score__avg']
        return round(avg, 2) if avg is not None else None

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'movie', 'user', 'score']
        read_only_fields = ['user']