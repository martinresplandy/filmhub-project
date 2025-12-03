import requests
from api.models import Movie


API_BASE_URL = "https://api.themoviedb.org/3" 
API_KEY = "ed6c1919d48f4231cb8f449cfe728211"
GENRE_MAP = {}
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
                movie = movie_obj.create_movie_from_external_id()
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