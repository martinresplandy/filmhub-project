const API_URL = "http://localhost:8000/api";

const getAuthHeaders = () => {
  const token = localStorage.getItem("token");
  return {
    "Content-Type": "application/json",
    Authorization: `Token ${token}`,
  };
};

export const movieService = {
  // Get catalog with popular, top_rated, action, comedy, drama
  getMovies: async () => {
    const response = await fetch(`${API_URL}/movies/`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to fetch movies catalog');
    }
    return response.json();
  },

  // Get specific movie by external_id
  getMovie: async (external_id) => {
    const response = await fetch(`${API_URL}/movie/`, {
      method: 'GET',
      headers: getAuthHeaders(),
      body: JSON.stringify({ external_id }),
    });
    if (!response.ok) {
      throw new Error('Failed to fetch movie');
    }
    return response.json();
  },

  // Search movies by title (default), director, or genre
  searchMovies: async (query, searchType = 'title') => {
    const response = await fetch(
      `${API_URL}/movies/?search=${encodeURIComponent(query)}&search_type=${searchType}`,
      {
        headers: getAuthHeaders(),
      }
    );
    if (!response.ok) {
      throw new Error('Failed to search movies');
    }
    return response.json();
  },

  // Search by genre
  getMoviesByGenre: async (genre) => {
    const response = await fetch(
      `${API_URL}/movies/?search=${encodeURIComponent(genre)}&search_type=genre`,
      {
        headers: getAuthHeaders(),
      }
    );
    if (!response.ok) {
      throw new Error('Failed to fetch movies by genre');
    }
    return response.json();
  },

  // Search by director
  getMoviesByDirector: async (director) => {
    const response = await fetch(
      `${API_URL}/movies/?search=${encodeURIComponent(director)}&search_type=director`,
      {
        headers: getAuthHeaders(),
      }
    );
    if (!response.ok) {
      throw new Error('Failed to fetch movies by director');
    }
    return response.json();
  },

  // Rate a movie
  rateMovie: async (movieId, score, comment = '') => {
    const response = await fetch(`${API_URL}/ratings/`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ 
        movie: movieId, 
        score: score,
        comment: comment 
      }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to rate movie');
    }
    return response.json();
  },

  // Get user's ratings
  getRatings: async () => {
    const response = await fetch(`${API_URL}/ratings/`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to fetch ratings');
    }
    return response.json();
  },

  // Update existing rating
  updateRating: async (movieId, score, comment = '') => {
    const response = await fetch(`${API_URL}/ratings/`, {
      method: "PATCH",
      headers: getAuthHeaders(),
      body: JSON.stringify({ 
        movie: movieId, 
        score: score,
        comment: comment 
      }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to update rating');
    }
    return response.json();
  },

  // Get recommendations
  getRecommendations: async () => {
    const response = await fetch(`${API_URL}/recommended_movies/`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  },

  // Update recommendations (trigger recalculation)
  updateRecommendations: async () => {
    const response = await fetch(`${API_URL}/movies/recommended/`, {
      method: 'UPDATE',
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to update recommendations');
    }
    return response.json();
  },

  // Get watchlist
  getWatchList: async () => {
    const response = await fetch(`${API_URL}/movies/watch_list/`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to fetch watch list');
    }
    return response.json();
  },

  // Add to watchlist
  addToWatchList: async (external_id) => {
    const response = await fetch(`${API_URL}/movies/watch_list/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ external_id }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to add to watch list');
    }
    return response.json();
  },

  // Get watched movies
  getWatchedMovies: async () => {
    const response = await fetch(`${API_URL}/movies/watched/`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to fetch watched movies');
    }
    return response.json();
  },

  // Add to watched movies
  addToWatchedMovies: async (external_id) => {
    const response = await fetch(`${API_URL}/movies/watched/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ external_id }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to add to watched movies');
    }
    return response.json();
  },
};