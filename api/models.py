# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Movie(models.Model):
    title = models.CharField(max_length=100)
    director = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField()
    genre = models.CharField(max_length=50)
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

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}: {self.score}" 

