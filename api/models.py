from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    watched_movies = models.ManyToManyField('Movie', blank=True, related_name='watched_by')
    watch_list = models.ManyToManyField('Movie', blank=True, related_name='in_watchlists')
    recommended_movies = models.ManyToManyField('Movie', blank=True, related_name='recommended_to')

    def __str__(self):
        return self.user.username
            

class Movie(models.Model):
    external_id = models.IntegerField(unique=True, null=False, blank=False)
    title = models.CharField(max_length=100)
    poster_url = models.URLField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    director = models.CharField(max_length=100, blank=True)
    genre = models.CharField(max_length=255)
    keyword = models.CharField(max_length=255)
    duration = models.IntegerField(help_text="Duration in minutes")
    year = models.IntegerField()

    def __str__(self):  
        return self.title

    class Meta:
        # Ensure the exact combination of these fields is unique at the database level.
        # This prevents race conditions where two requests create the same movie concurrently.
        constraints = [
            models.UniqueConstraint(fields=['title', 'description', 'genre', 'year'], name='unique_movie_full')
        ]
    
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}: {self.score}" 

