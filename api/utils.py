import requests
from api.models import Movie


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


# **** USER **** #
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

def create_movie_from_external_id(self):
        # If the movie doesn't exist (tested in the previous function), proceed to API call to integrate it into our DB
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
            self.poster_url = f"https://image.tmdb.org/t/p/w500{data.get('poster_path')}" if data.get('poster_path') else ""
            self.description = data.get('overview', '') # Use overview for description
            self.duration = data.get('runtime', 0)     # Use runtime for duration (minutes)
            
            # GENRES
            genre_names_list = []
            for genre in data.get('genres', []):
                genre_names_list.append(genre['name']) 
                GENRE_MAP[genre['id']] = genre['name']
            # Store the main genres as a comma-separated string, limited by your max_length
            self.genre = ", ".join(genre_names_list)[:255]

            # KEYWORDS
            # Fetch keywords from a separate endpoint
            keywords_url = f"{API_BASE_URL}/movie/{self.external_id}/keywords"
            keywords_response = requests.get(keywords_url, headers=headers, params=params)
            keywords_response.raise_for_status()
            keywords_data = keywords_response.json()

            keyword_names_list = []
            for k in keywords_data.get('keywords', []):
                keyword_names_list.append(k['name'])
                KEYWORD_MAP[k['id']] = k['name']
            
            self.keyword = ", ".join(keyword_names_list)[:255]

            # YEAR
            # Extract year from release_date (e.g., "2023-10-20")
            release_date = data.get('release_date')
            self.year = int(release_date.split('-')[0]) if release_date else 0

            print_maps()

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
    
    return {
        "external_id": movie_id,
        "title": title,
        "poster_url": poster_url,
        "genre": genre_string,
        "year": year,
        "average_rating": rating_float,
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

def search_by_director(director_name):
    """
    Searches for movies by director.
    
    Args:
        director_name: Director's name
        
    Returns:
        List of director's movies formatted
    """
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
    """
    Searches for movies by genre.
    
    Args:
        genre_name: Genre name
        
    Returns:
        List of genre movies formatted
    """
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