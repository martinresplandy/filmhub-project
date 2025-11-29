from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import requests

API_BASE_URL = "https://api.themoviedb.org/3" 
API_KEY = "ed6c1919d48f4231cb8f449cfe728211"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    watched_movies = models.ManyToManyField('Movie', blank=True, related_name='watched_by')
    watch_list = models.ManyToManyField('Movie', blank=True, related_name='in_watchlists')
    recommended_movies = models.ManyToManyField('Movie', blank=True, related_name='recommended_to')

    def __str__(self):
        return self.user.username
    
    def update_recommendations(self):
        # Placeholder for recommendation logic
        pass

class Movie(models.Model):
    external_id = models.IntegerField(unique=True, null=False, blank=False)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    genre = models.CharField(max_length=255)
    duration = models.IntegerField(help_text="Duration in minutes")
    year = models.IntegerField()

    def __str__(self):  
        return self.title
    
    def add_movie_if_not_exists(self):
        # Quick check for existing movie based on external_id
        existing_movie = Movie.objects.filter(external_id=self.external_id).first()
        if existing_movie:
            # Return the existing object if found
            return existing_movie
        
        # If the movie doesn't exist, proceed to API call
        try:
            # Construct the API URL and headers
            api_url = f"{API_BASE_URL}/movie/{self.external_id}"
            headers = {
                "accept": "application/json",
            }
            params = {
                "api_key": API_KEY,
            }

            # Execute the API Request
            response = requests.get(api_url, headers=headers, params=params)
            response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)

            # Parse the JSON response
            data = response.json()

            # Extract relevant fields from the API response
            if not data.get('title') or not data.get('release_date'):
                 raise ValueError("Missing essential movie data from API.")
            self.title = data.get('title')
            self.description = data.get('overview', '') # Use overview for description
            self.duration = data.get('runtime', 0)     # Use runtime for duration (minutes)
            # Extract genre names (TMDb returns a list of dictionaries)
            genre_names = [g['name'] for g in data.get('genres', [])]
            # Store the main genres as a comma-separated string, limited by your max_length
            self.genre = ", ".join(genre_names)[:255]
            # Extract year from release_date (e.g., "2023-10-20")
            release_date = data.get('release_date')
            self.year = int(release_date.split('-')[0]) if release_date else 0

            # Save the new movie to the database
            self.save()
            return self
        except requests.exceptions.HTTPError as e:
            # Handle specific HTTP errors (e.g., 404 Not Found)
            print(f"API HTTP Error for ID {self.external_id}: {e}")
            return None # Or raise an appropriate error
            
        except requests.exceptions.RequestException as e:
            # Handle connection errors, timeouts, etc.
            print(f"API Connection Error: {e}")
            return None 
            
        except Exception as e:
            # Handle JSON parsing or other general errors
            print(f"General Error processing movie {self.external_id}: {e}")
            return None
    
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

