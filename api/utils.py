import requests
from enum import Enum

from django.contrib.auth import authenticate

from .serializers import UserSerializer, MovieSerializer, RatingSerializer
from .models import Movie, Rating, UserProfile


API_BASE_URL = "https://api.themoviedb.org/3" 
API_KEY = "ed6c1919d48f4231cb8f449cfe728211"
GENRE_MAP = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy",
    80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family",
    14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music",
    9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
    10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western",
}
GENRE_POINTS = 1
KEYWORD_MAP = {}
KEYWORD_POINTS = 3

def print_maps():
    print("GENRE_MAP:", GENRE_MAP)
    print("KEYWORD_MAP:", KEYWORD_MAP)

# **** STATUS **** #

class Status(Enum):
    SUCCESS = "success"
    ALREADY_EXISTS = "already_exists"
    NOT_FOUND = "not_found"
    FAILURE = "failure"

# **** USER **** #

def register_user(serializer: UserSerializer):
    if serializer.is_valid():
        user = serializer.save()
        UserProfile.objects.create(user=user)
        return user, Status.SUCCESS
    return None, Status.FAILURE

def login_user(username, password):
    user = authenticate(username=username, password=password)
    return user, Status.SUCCESS if user else Status.FAILURE

# **** RATINGS **** #

def get_all_ratings_for_user(user):
    return Rating.objects.filter(user=user), Status.SUCCESS

def add_rating(rating: RatingSerializer):
    if rating.is_valid():
        try:
            Movie.objects.get(external_id=rating.validated_data['movie'].external_id)
        except Movie.DoesNotExist:
            create_movie_from_external_id(rating.validated_data['movie'].external_id)
        if Rating.objects.filter(
            user=rating.validated_data['user'],
            movie=rating.validated_data['movie']
        ).exists():
            return None, Status.ALREADY_EXISTS
        rating_instance = rating.save()
        return rating_instance, Status.SUCCESS
    return None, Status.FAILURE

def update_rating(rating: RatingSerializer):
    if rating.is_valid():
        try:
            existing_rating = Rating.objects.get(
                user=rating.validated_data['user'],
                movie=rating.validated_data['movie']
            )
            if existing_rating:
                existing_rating.score = rating.validated_data.get('score', existing_rating.score)
                existing_rating.comment = rating.validated_data.get('comment', existing_rating.comment)
                existing_rating.save()
                return existing_rating, Status.SUCCESS
            else:
                return None, Status.NOT_FOUND
        except Rating.DoesNotExist:
            return None, Status.FAILURE
    return None, Status.FAILURE

# **** RECOMMENDED MOVIES **** #

def get_recommended_movies_for_user(user_profile):
    return user_profile.recommended_movies.all(), Status.SUCCESS
    
def update_recommendations(self):
        # Clear existing recommendations
        self.recommended_movies.clear()

        # Retrieve rated movies by the user
        ratings = self.user.rating_set.all()
        # Define the main conditions for the recommendation logic
        liked_genres = set()
        liked_keywords = set()
        for rating in ratings:
            movie = rating.movie
            if rating.score >= 3:
                # Extract genres
                movie_genres = [g.strip() for g in movie.genre.split(',')]
                liked_genres.update(movie_genres)
                # Extract keywords
                movie_keywords = [k.strip() for k in movie.keyword.split(',')]
                liked_keywords.update(movie_keywords)
        # Find movies that match liked genres or keywords
        # Construct the header
        headers = {
            "accept": "application/json",
        }
        
        recommended_set = {}
        for genre_id in liked_genres:
            # Construct the request URL and params
            api_url = f"{API_BASE_URL}/discover/movie"
            params = {
                "api_key": API_KEY,
                "with_genres": genre_id,
                "sort_by": "popularity.desc",
                "page": 1
            }
            # Execute the API Request
            response = requests.get(api_url, headers=headers, params=params)
            response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)
            data = response.json()
            # Adding points by genre matches
            for item in data.get('results', []):
                movie_id = item['id']
                if movie_id not in recommended_set:
                    recommended_set[movie_id] = GENRE_POINTS
                else:
                    recommended_set[movie_id] += GENRE_POINTS
        for keyword_id in liked_keywords:
            # Construct the request URL and params
            api_url = f"{API_BASE_URL}/discover/movie"
            params = {
                "api_key": API_KEY,
                "with_keywords": keyword_id,
                "sort_by": "popularity.desc",
                "page": 1
            }
            # Execute the API Request
            response = requests.get(api_url, headers=headers, params=params)
            response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)
            data = response.json()
            # Adding points by keyword matches
            for item in data.get('results', []):
                movie_id = item['id']
                if movie_id not in recommended_set:
                    recommended_set[movie_id] = KEYWORD_POINTS
                else:
                    recommended_set[movie_id] += KEYWORD_POINTS
        # Sort recommended movies by their accumulated score
        sorted_recommendations = sorted(
            recommended_set.items(), 
            key=lambda item: item[1], 
            reverse=True
        )
        # if the movie is already watched or in watchlist, skip it
        watched_ids = set(self.watched_movies.values_list('external_id', flat=True))
        watchlist_ids = set(self.watch_list.values_list('external_id', flat=True))
        for movie_id, score in sorted_recommendations:
            if movie_id in watched_ids or movie_id in watchlist_ids:
                continue
            movie = None
            try:
                movie = Movie.objects.get(external_id=movie_id)
            except Movie.DoesNotExist:
                movie_obj = Movie(external_id=movie_id)
                movie = create_movie_from_external_id(movie_obj)
            if movie:
                self.recommended_movies.add(movie)
                # Limit to 20 recommendations
                if self.recommended_movies.count() >= 20:
                   break
                
        return self.recommended_movies.all()

# **** WATCHED MOVIES **** #

def get_watched_movies_for_user(user_profile):
    return user_profile.watched_movies.all()

def add_watched_movie(user_profile, movie_id):
    movie = None
    try:
        movie = Movie.objects.get(external_id=movie_id)
    except Movie.DoesNotExist:
        movie = create_movie_from_external_id(movie_id)
    if not movie:
        return None
    else:
        if movie in user_profile.watched_movies.all():
            return movie
        user_profile.watched_movies.add(movie)
        return movie
    
def remove_watched_movie(user_profile, movie_id):
    try:
        movie = Movie.objects.get(external_id=movie_id)
        if movie in user_profile.watched_movies.all():
            user_profile.watched_movies.remove(movie)
            return movie, Status.SUCCESS
        else:
            return None, Status.NOT_FOUND
    except Movie.DoesNotExist:
        return None, Status.FAILURE
    
# **** WATCH LIST **** #

def get_watch_list_for_user(user_profile):
    return user_profile.watch_list.all(), Status.SUCCESS

def add_watch_list_movie(user_profile, movie_id):
    movie = None
    try:
        movie = Movie.objects.get(external_id=movie_id)
    except Movie.DoesNotExist:
        movie = create_movie_from_external_id(movie_id)
    if not movie:
        return None, Status.FAILURE
    else:
        if movie in user_profile.watch_list.all():
            return movie, Status.ALREADY_EXISTS
        user_profile.watch_list.add(movie)
        return movie, Status.SUCCESS
    
def remove_watch_list_movie(user_profile, movie_id):
    try:
        movie = Movie.objects.get(external_id=movie_id)
        if movie in user_profile.watch_list.all():
            user_profile.watch_list.remove(movie)
            return movie, Status.SUCCESS
        else:
            return None, Status.NOT_FOUND
    except Movie.DoesNotExist:
        return None, Status.FAILURE

# **** MOVIE STORING **** #

def create_movie_from_external_id(movie_id):
        # If the movie doesn't exist (tested in the previous function), proceed to API call to integrate it into our DB
        try:
            # Construct the API URL and headers
            api_url = f"{API_BASE_URL}/movie/{movie_id}"
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

            # Create a new Movie instance
            movie = Movie(external_id=movie_id)

            # Extract relevant fields from the API response
            if not data.get('title') or not data.get('release_date'):
                 raise ValueError("Missing essential movie data from API.")
            movie.title = data.get('title')
            movie.poster_url = f"https://image.tmdb.org/t/p/w500{data.get('poster_path')}" if data.get('poster_path') else ""
            movie.description = data.get('overview', '') 
            movie.director = data.get('director','Unknown')
            movie.duration = data.get('runtime', 0)
            
            # GENRES
            genre_names_list = []
            for genre in data.get('genres', []):
                genre_names_list.append(genre['name']) 
                GENRE_MAP[genre['id']] = genre['name']
            # Store the main genres as a comma-separated string, limited by your max_length
            movie.genre = ", ".join(genre_names_list)[:255]

            # KEYWORDS
            # Fetch keywords from a separate endpoint
            keywords_url = f"{API_BASE_URL}/movie/{movie_id}/keywords"
            keywords_response = requests.get(keywords_url, headers=headers, params=params)
            keywords_response.raise_for_status()
            keywords_data = keywords_response.json()

            keyword_names_list = []
            for k in keywords_data.get('keywords', []):
                keyword_names_list.append(k['name'])
                KEYWORD_MAP[k['id']] = k['name']
            
            movie.keyword = ", ".join(keyword_names_list)[:255]

            # YEAR
            # Extract year from release_date (e.g., "2023-10-20")
            release_date = data.get('release_date')
            movie.year = int(release_date.split('-')[0]) if release_date else 0

            print_maps()

            # Save the new movie to the database
            movie.save()
            return movie, Status.SUCCESS
        except requests.exceptions.HTTPError as e:
            # Handle specific HTTP errors (e.g., 404 Not Found)
            print(f"API HTTP Error for ID {movie_id}: {e}")
            return None, Status.FAILURE
            
        except requests.exceptions.RequestException as e:
            # Handle connection errors, timeouts, etc.
            print(f"API Connection Error: {e}")
            return None, Status.FAILURE
            
        except Exception as e:
            # Handle JSON parsing or other general errors
            print(f"General Error processing movie {movie_id}: {e}")
            return None, Status.FAILURE

# **** MOVIE CATALOG **** #

def movies_catalog(content):
    if content:
        # return catalog with different sections
        catalog = {}
        
        # popular movies
        url = f"{API_BASE_URL}/movie/popular"
        params = {"api_key": API_KEY, "page": 1}
        catalog["popular"] = fetch_movies(url, params, limit=20)
        
        # top rated
        url = f"{API_BASE_URL}/movie/top_rated"
        params = {"api_key": API_KEY, "page": 1}
        catalog["top_rated"] = fetch_movies(url, params, limit=20)
        
        # action
        url = f"{API_BASE_URL}/discover/movie"
        params = {"api_key": API_KEY, "with_genres": 28, "sort_by": "popularity.desc", "page": 1}
        catalog["action"] = fetch_movies(url, params, limit=20)
        
        # comedy
        url = f"{API_BASE_URL}/discover/movie"
        params = {"api_key": API_KEY, "with_genres": 35, "sort_by": "popularity.desc", "page": 1}
        catalog["comedy"] = fetch_movies(url, params, limit=20)
        
        # drama
        url = f"{API_BASE_URL}/discover/movie"
        params = {"api_key": API_KEY, "with_genres": 18, "sort_by": "popularity.desc", "page": 1}
        catalog["drama"] = fetch_movies(url, params, limit=20)
        
        return catalog, Status.SUCCESS
    return {}, Status.FAILURE

# **** MOVIE SEARCH **** #

def movies_search(content, search_type):
    # handle search
    if content and search_type:
        if search_type == 'director':
            movies = search_by_director(content)
        elif search_type == 'genre':
            movies = search_by_genre(content)
        else:
            # default is title search
            url = f"{API_BASE_URL}/search/movie"
            params = {"api_key": API_KEY, "query": content, "page": 1}
            movies = fetch_movies(url, params, limit=20)
        
        return movies, Status.SUCCESS
    return [], Status.FAILURE

def search_by_director(director_name):
    try:
        # search for the person first
        url = f"{API_BASE_URL}/search/person"
        params = {"api_key": API_KEY, "query": director_name, "page": 1}
        response = requests.get(url, params=params)
        data = response.json()
        people = data.get('results', [])
        
        if not people:
            return []
        
        # get the first person found (usually the most popular one)
        person_id = people[0].get('id')
        
        # now get all movies this person worked on
        url = f"{API_BASE_URL}/person/{person_id}/movie_credits"
        params = {"api_key": API_KEY}
        response = requests.get(url, params=params)
        data = response.json()
        crew = data.get('crew', [])
        
        result = []
        for job in crew:
            if len(result) >= 20:
                break
            
            # only get movies where they were director
            if job.get('job') == 'Director':
                formatted = format_movie(job)
                if formatted:
                    result.append(formatted)
        
        return result
    except:
        return []

def search_by_genre(genre_name):
    try:
        # look up the genre id
        genre_id = None
        for gid, gname in GENRE_MAP.items():
            if gname.lower() == genre_name.lower():
                genre_id = gid
                break
        
        if not genre_id:
            return []
        
        # get movies for this genre
        url = f"{API_BASE_URL}/discover/movie"
        params = {"api_key": API_KEY, "with_genres": genre_id, "sort_by": "popularity.desc", "page": 1}
        response = requests.get(url, params=params)
        data = response.json()
        movies = data.get('results', [])
        
        result = []
        for movie in movies:
            if len(result) >= 20:
                break
            
            formatted = format_movie(movie)
            if formatted:
                result.append(formatted)
        
        return result
    except:
        return []

# **** MOVIE FORMAT AND SEARCH **** #

def format_movie(movie):
    """
    Formats movie data from TMDB API to the format used in the frontend.
    
    Args:
        movie: Dictionary with movie data from TMDB API
        
    Returns:
        Formatted dictionary or None if data is invalid
    """
    # check if movie has the required fields
    title = movie.get('title', '').strip()
    poster = movie.get('poster_path')
    movie_id = movie.get('id')
    
    if not title or not poster or not movie_id:
        return None
    
    # get genres
    genre_ids = movie.get('genre_ids', [])
    genre_names = []
    for genre_id in genre_ids:
        if genre_id in GENRE_MAP:
            genre_names.append(GENRE_MAP[genre_id])
        else:
            genre_names.append("Unknown")
    
    if genre_names:
        genre_string = ", ".join(genre_names)
    else:
        genre_string = "Unknown"
    
    # extract year
    date = movie.get('release_date', '')
    year = None
    if date:
        try:
            year = int(date.split('-')[0])
        except:
            pass
    
    # build poster url
    poster_url = f"https://image.tmdb.org/t/p/w185{poster}"
    
    # get rating
    rating = movie.get('vote_average', 0)
    try:
        rating_float = round(float(rating), 1)
    except:
        rating_float = 0.0
    
    description = movie.get('overview', '')

    return {
        "external_id": movie_id,
        "title": title,
        "poster_url": poster_url,
        "genre": genre_string,
        "year": year,
        "average_rating": rating_float,
        "description": description,
    }

def fetch_movies(url, params, limit=20):
    """
    Fetches movies from TMDB API and returns formatted list.
    
    Args:
        url: TMDB API URL
        params: Request parameters
        limit: Maximum number of movies to return (default: 20)
        
    Returns:
        List of formatted movies
    """
    try:
        response = requests.get(url, params=params)
        data = response.json()
        movies = data.get('results', [])
        
        result = []
        for movie in movies:
            if len(result) >= limit:
                break
            
            formatted = format_movie(movie)
            if formatted:
                result.append(formatted)
        
        return result
    except Exception as e:
        return []