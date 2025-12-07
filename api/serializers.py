from rest_framework import serializers
from .models import Movie, Rating
from django.contrib.auth.models import User
from .validators.shared import (validate_email, validate_email_unique, validate_password_strength, validate_unique_movie, validate_username)
from django.db.models import Avg

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'username': {
                'validators': [validate_username],
                'required': True,
                'allow_blank': False
            },
            'email': {
                'validators': [validate_email, validate_email_unique],
                'required': True,
                'allow_blank': False
            },
            'password': {
                'write_only': True,
                'required': True
            }
        }

    def validate_password(self, value):
        validate_password_strength(value)
        return value

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
        fields = ['external_id', 'title', 'poster_url', 'description', 'director', 'genre', 'keyword', 'year', 'duration', 'average_rating']

    def get_average_rating(self, obj):
        # If the Movie object doesn't exists, we don't give any ratings to it
        if obj.pk: 
            avg = obj.rating_set.aggregate(Avg('score'))['score__avg']
            return round(avg, 2) if avg is not None else None
        return getattr(obj, 'average_rating', None)

    def validate(self, data):
        # Build lookup values: handles missing data during updates
        title = data.get('title', getattr(self.instance, 'title', None))
        poster_url = data.get('poster_url', getattr(self.instance, 'poster_url', None))
        description = data.get('description', getattr(self.instance, 'description', None))
        director = data.get('director', getattr(self.instance, 'director', None))
        genre = data.get('genre', getattr(self.instance, 'genre', None))
        keyword = data.get('keyword', getattr(self.instance, 'keyword', None))
        duration = data.get('duration', getattr(self.instance, 'duration', None))
        year = data.get('year', getattr(self.instance, 'year', None))

        # Call the external validator function
        validate_unique_movie(
            title=title,
            poster_url=poster_url,
            description=description,
            director=director,
            genre=genre,
            keyword=keyword,
            duration=duration,
            year=year,
            instance=self.instance # Pass the current instance for exclusion during update
        )

        return data

class RatingSerializer(serializers.ModelSerializer):
    # Take movie by its external_id
    movie = serializers.SlugRelatedField(
        queryset=Movie.objects.all(),
        slug_field='external_id' 
    )

    class Meta:
        model = Rating
        fields = ['id', 'user', 'movie', 'score', 'comment']
        read_only_fields = ['user']