import requests
from enum import Enum
import concurrent.futures

from django.contrib.auth import authenticate

from .serializers import UserSerializer, MovieSerializer, RatingSerializer
from .models import Movie, Rating, UserProfile
from .validators.shared import validate_rating_score


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

def add_rating(user, movie_external_id, score, comment=''):
    validate_rating_score(score)
    if user is not None and movie_external_id is not None:
        # Check if the movie exists in our DB
        try:
            movie_instance = Movie.objects.get(external_id=movie_external_id)
        except Movie.DoesNotExist:
            movie_instance, response_status = create_movie_from_external_id(movie_external_id)
            if response_status != Status.SUCCESS:
                return None, response_status
        # Check if the rating already exists
        if Rating.objects.filter(user=user, movie=movie_instance).exists():
            return None, Status.ALREADY_EXISTS
        # Create and save the new rating
        rating = Rating(user=user, movie=movie_instance, score=score, comment=comment)
        rating.save()
        return rating, Status.SUCCESS
    return None, Status.FAILURE

def update_rating(user, id, new_score, new_comment=''):
    validate_rating_score(new_score)
    try:
        rating = Rating.objects.get(id=id)
    except Rating.DoesNotExist:
        return None, Status.NOT_FOUND
    if rating is None:
        return None, Status.NOT_FOUND
    # Ensure the rating belongs to the user
    if rating.user == user:
        validate_rating_score(new_score)
        rating_instance = rating
        rating_instance.score = new_score
        rating_instance.comment = new_comment
        rating_instance.save()
        return rating_instance, Status.SUCCESS
    return None, Status.FAILURE

def delete_rating(user, id):
    try:
        rating = Rating.objects.get(id=id)
    except Rating.DoesNotExist:
        return None, Status.NOT_FOUND
    if rating is None:
        return None, Status.NOT_FOUND
    # Ensure the rating belongs to the user
    if rating.user == user:
        rating.delete()
        return rating, Status.SUCCESS
    return None, Status.FAILURE

# **** RECOMMENDED MOVIES **** #

def get_recommended_movies_for_user(user_profile: UserProfile):
    # We optimized that function with concurrent executions
    recommended = user_profile.recommended_movies.all()
    # if the recommendation list is empty, update it
    if len(recommended) == 0:
        recommended = update_recommendations(user_profile)
    return user_profile.recommended_movies.all(), Status.SUCCESS

def fetch_recommendations_chunk(url, params):
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get('results', [])
    
def update_recommendations(user_profile: UserProfile):
    
    REVERSE_GENRE_MAP = {v.lower(): k for k, v in GENRE_MAP.items()}
    REVERSE_KEYWORD_MAP = {v.lower(): k for k, v in KEYWORD_MAP.items()}
    
    user_profile.recommended_movies.clear()
    ratings = user_profile.user.rating_set.all()
    
    liked_genre_ids = set()
    liked_keyword_ids = set()
    for rating in ratings:
        if rating.score >= 3:
            for name in [g.strip() for g in rating.movie.genre.split(',')]:
                genre_id = REVERSE_GENRE_MAP.get(name.lower())
                if genre_id: liked_genre_ids.add(str(genre_id))
                
            for name in [k.strip() for k in rating.movie.keyword.split(',')]:
                keyword_id = REVERSE_KEYWORD_MAP.get(name.lower())
                if keyword_id: liked_keyword_ids.add(str(keyword_id))

    all_requests = []
    base_params = {"api_key": API_KEY, "sort_by": "popularity.desc", "page": 1}
    
    if liked_genre_ids:
        combined_genre_params = {**base_params, "with_genres": ','.join(liked_genre_ids)}
        all_requests.append((f"{API_BASE_URL}/discover/movie", combined_genre_params, GENRE_POINTS))
    
    if liked_keyword_ids:
        combined_keyword_params = {**base_params, "with_keywords": ','.join(liked_keyword_ids)}
        all_requests.append((f"{API_BASE_URL}/discover/movie", combined_keyword_params, KEYWORD_POINTS))

    recommended_set = {}
    
    # Use max_workers=5 for faster processing of network-bound tasks
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_request = {
            executor.submit(fetch_recommendations_chunk, url, params): (url, params, points)
            for url, params, points in all_requests
        }
        
        for future in concurrent.futures.as_completed(future_to_request):
            _, _, points = future_to_request[future]
            try:
                results = future.result()
                # Process the results from this specific chunk
                for item in results:
                    movie_id = item['id']
                    recommended_set[movie_id] = recommended_set.get(movie_id, 0) + points
            except Exception as exc:
                print(f'Recommendation chunk failed: {exc}')

    # 4. Sort and Filter Recommendations
    sorted_recommendations = sorted(
        recommended_set.items(), 
        key=lambda item: item[1], 
        reverse=True
    )
    
    watched_ids = set(user_profile.watched_movies.values_list('external_id', flat=True))
    watchlist_ids = set(user_profile.watch_list.values_list('external_id', flat=True))
    ratedlist_ids = set(ratings.values_list('movie__external_id', flat=True))
    
    for movie_id, score in sorted_recommendations:
        if movie_id in watched_ids or movie_id in watchlist_ids or movie_id in ratedlist_ids:
            continue
            
        try:
            movie_instance = Movie.objects.get(external_id=movie_id)
        except Movie.DoesNotExist:
            movie_tuple = create_movie_from_external_id(movie_id)
            if movie_tuple[1] != Status.SUCCESS:
                continue
            movie_instance = movie_tuple[0]

        if movie_instance:
            user_profile.recommended_movies.add(movie_instance)
            if user_profile.recommended_movies.count() >= 20:
                break
            
    return user_profile.recommended_movies.all()

# **** WATCHED MOVIES **** #

def get_watched_movies_for_user(user_profile: UserProfile):
    return user_profile.watched_movies.all(), Status.SUCCESS

def add_watched_movie(user_profile: UserProfile, movie_id):
    try:
        movie_instance = Movie.objects.get(external_id=movie_id)
    except Movie.DoesNotExist:
        movie_instance, response_status = create_movie_from_external_id(movie_id)
        if response_status != Status.SUCCESS:
            return None, response_status
    if movie_instance in user_profile.watched_movies.all():
        return movie_instance, Status.ALREADY_EXISTS
    if movie_instance in user_profile.watch_list.all():
        user_profile.watch_list.remove(movie_instance)
    user_profile.watched_movies.add(movie_instance)
    return movie_instance, Status.SUCCESS
    
def remove_watched_movie(user_profile: UserProfile, movie_id):
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

def get_watch_list_for_user(user_profile: UserProfile):
    return user_profile.watch_list.all(), Status.SUCCESS

def add_watch_list_movie(user_profile: UserProfile, movie_id):
    try:
        movie_instance = Movie.objects.get(external_id=movie_id)
    except Movie.DoesNotExist:
        movie_instance, response_status = create_movie_from_external_id(movie_id)
        if response_status != Status.SUCCESS:
            return None, response_status
    if movie_instance in user_profile.watch_list.all():
        return movie_instance, Status.ALREADY_EXISTS
    user_profile.watch_list.add(movie_instance)
    return movie_instance, Status.SUCCESS
    
def remove_watch_list_movie(user_profile: UserProfile, movie_id):
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
        movie = get_movie_from_external_API(api_url, headers, params)
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

def fetch_and_serialize_section(section_name, url, params):
    try:
        movie_list = get_movies_from_external_API(url, headers={"accept": "application/json"}, params=params)
        return section_name, MovieSerializer(movie_list, many=True).data
    except Exception as e:
        print(f"Error fetching section {section_name}: {e}")
        return section_name, []

def movies_catalog():
    # We optimized the function with multithreading
    requests_to_run = {
        "popular": {
            "url": f"{API_BASE_URL}/movie/popular",
            "params": {"api_key": API_KEY, "page": 1}
        },
        "top_rated": {
            "url": f"{API_BASE_URL}/movie/top_rated",
            "params": {"api_key": API_KEY, "page": 1}
        },
        "action": {
            "url": f"{API_BASE_URL}/discover/movie",
            "params": {"api_key": API_KEY, "with_genres": 28, "sort_by": "popularity.desc", "page": 1}
        },
        "comedy": {
            "url": f"{API_BASE_URL}/discover/movie",
            "params": {"api_key": API_KEY, "with_genres": 35, "sort_by": "popularity.desc", "page": 1}
        },
        "drama": {
            "url": f"{API_BASE_URL}/discover/movie",
            "params": {"api_key": API_KEY, "with_genres": 18, "sort_by": "popularity.desc", "page": 1}
        }
    }
    
    catalog = {}
    
    # Use ThreadPoolExecutor to run all requests concurrently (5 workers for 5 requests)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_section = {
            executor.submit(
                fetch_and_serialize_section, 
                name, 
                data["url"], 
                data["params"]
            ): name for name, data in requests_to_run.items()
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_section):
            section_name = future_to_section[future]
    
            try:
                _, serialized_data = future.result()
                catalog[section_name] = serialized_data
            except Exception as exc:
                print(f'{section_name} generated an unhandled exception: {exc}')
                catalog[section_name] = []
                
    return catalog, Status.SUCCESS

# **** MOVIE SEARCH **** #

def movies_search(content, search_type):
    # handle search
    if content != '' and search_type != '':
        if search_type == 'director':
            movies = search_by_director(content)
        elif search_type == 'genre':
            movies = search_by_genre(content)
        else:
            # default is title search
            url = f"{API_BASE_URL}/search/movie"
            params = {"api_key": API_KEY, "query": content, "page": 1}
            movies = get_movies_from_external_API(url, None, params)
        
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
    except requests.exceptions.RequestException as e:
        print(f"Director Search API Error: {e}")
        return []
    except Exception as e:
        print(f"General Error in Director Search: {e}")
        return []

def search_by_genre(genre_name, limit=20):
    REVERSE_GENRE_MAP = {v.lower(): k for k, v in GENRE_MAP.items()}
    genre_id = REVERSE_GENRE_MAP.get(genre_name.lower())
    if not genre_id:
        return []
    # get movies for this genre
    url = f"{API_BASE_URL}/discover/movie"
    params = {"api_key": API_KEY, "with_genres": genre_id, "sort_by": "popularity.desc", "page": 1}
    
    result = get_movies_from_external_API(url, None, params)
    result = result[:limit]
    return result

# **** MOVIES FROM EXTERNAL API **** #

def get_movies_from_external_API(url, headers={}, params={}, limit=20):
    # Execute the API Request
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)

    # Parse the JSON response
    json_body = response.json()

    movies = []
    
    for data in json_body.get('results'):
        if (len(movies) >= limit):
            break
        movies.append(format_movie(data))
    return movies

def get_movie_from_external_API(url, headers, params):
    # Execute the API Request
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)

    # Parse the JSON response
    data = response.json()

    return format_movie(data)
    
# **** FORMAT MOVIE FROM EXTERNAL API **** #

def format_movie(movie_obj: dict):
    # Checking the object type
    if not movie_obj.get('title') or not movie_obj.get('id'):
        raise ValueError("Missing essential movie data from API.")

    standard_headers = {"accept": "application/json"}
    standard_params = {"api_key": API_KEY,}

    # Create a new Movie instance
    movie = Movie(external_id=movie_obj.get('id'))
    movie.title = movie_obj.get('title')
    movie.poster_url = f"https://image.tmdb.org/t/p/w500{movie_obj.get('poster_path')}" if movie_obj.get('poster_path') else ""
    movie.description = movie_obj.get('overview', '') 
    movie.director = movie_obj.get('director','Unknown')
    movie.duration = movie_obj.get('runtime', 0)
    
    # GENRES
    genre_names_list = []
    for genre in movie_obj.get('genres', []):
        genre_names_list.append(genre['name']) 
        GENRE_MAP[genre['id']] = genre['name']
    # Store the main genres as a comma-separated string, limited by your max_length
    movie.genre = ", ".join(genre_names_list)[:255]

    # KEYWORDS
    # Fetch keywords from a separate endpoint
    keywords_url = f"{API_BASE_URL}/movie/{movie_obj.get('id')}/keywords"
    keywords_response = requests.get(keywords_url, headers=standard_headers, params=standard_params)
    keywords_response.raise_for_status()
    keywords_data = keywords_response.json()

    keyword_names_list = []
    for k in keywords_data.get('keywords', []):
        keyword_names_list.append(k['name'])
        KEYWORD_MAP[k['id']] = k['name']
    
    movie.keyword = ", ".join(keyword_names_list)[:255]

    # YEAR
    # Extract year from release_date (e.g., "2023-10-20")
    release_date = movie_obj.get('release_date')
    movie.year = int(release_date.split('-')[0]) if release_date else 0
    return movie