from rest_framework import serializers
from .models import Movie, Rating
from django.contrib.auth.models import User
from .validators import (validate_email, validate_email_unique, validate_password_strength, validate_username)
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
        fields = ['id', 'title', 'description', 'genre', 'year', 'average_rating']

    def get_average_rating(self, obj):
        avg = obj.rating_set.aggregate(Avg('score'))['score__avg']
        return round(avg, 2) if avg is not None else None

    def validate(self, data):
        """
        Prevent creation of a movie with the exact same (title, description, genre, year).
        For updates, make sure the new values don't collide with another existing movie.
        """
        # Build lookup values: on update some fields may be missing in `data` so use instance values
        title = data.get('title', getattr(self.instance, 'title', None))
        description = data.get('description', getattr(self.instance, 'description', None))
        genre = data.get('genre', getattr(self.instance, 'genre', None))
        year = data.get('year', getattr(self.instance, 'year', None))

        # Queryset excluding current instance (if updating)
        qs = Movie.objects.all()
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.filter(title=title, description=description, genre=genre, year=year).exists():
            raise serializers.ValidationError(
                'A movie with the same title, description, genre and year already exists.'
            )

        return data

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'movie', 'user', 'score']
        read_only_fields = ['user']