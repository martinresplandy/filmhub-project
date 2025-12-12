import { API_URL } from "../config";


const getAuthHeaders = () => {
  const token = localStorage.getItem("token");
  return {
    "Content-Type": "application/json",
    Authorization: `Token ${token}`,
  };
};

export const movieService = {
  getMovies: async () => {
    const response = await fetch(`${API_URL}/movies/`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to fetch movies catalog');
    }
    return response.json();
  },

  getMovie: async (external_id) => {
    try {
      const id = parseInt(external_id);
      
      const [catalogData, recommendationsData, watchListData, watchedData] = await Promise.allSettled([
        fetch(`${API_URL}/movies/`, { headers: getAuthHeaders() }).then(r => r.ok ? r.json() : null),
        fetch(`${API_URL}/recommended_movies/`, { headers: getAuthHeaders() }).then(r => r.ok ? r.json() : null),
        fetch(`${API_URL}/movies/watch_list/`, { headers: getAuthHeaders() }).then(r => r.ok ? r.json() : null),
        fetch(`${API_URL}/movies/watched/`, { headers: getAuthHeaders() }).then(r => r.ok ? r.json() : null),
      ]);
      
      if (catalogData.status === 'fulfilled' && catalogData.value) {
        for (const section in catalogData.value) {
          if (Array.isArray(catalogData.value[section])) {
            const movie = catalogData.value[section].find(m => m.external_id === id);
            if (movie) return movie;
          }
        }
      }
      
      if (recommendationsData.status === 'fulfilled' && Array.isArray(recommendationsData.value)) {
        const movie = recommendationsData.value.find(m => m.external_id === id);
        if (movie) return movie;
      }
      
      if (watchListData.status === 'fulfilled' && Array.isArray(watchListData.value)) {
        const movie = watchListData.value.find(m => m.external_id === id);
        if (movie) return movie;
      }
      
      if (watchedData.status === 'fulfilled' && Array.isArray(watchedData.value)) {
        const movie = watchedData.value.find(m => m.external_id === id);
        if (movie) return movie;
      }
      
      throw new Error('Movie not found');
    } catch (error) {
      throw error;
    }
  },

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

  getRatings: async () => {
    const response = await fetch(`${API_URL}/ratings/`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to fetch ratings');
    }
    return response.json();
  },

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

  rateOrUpdateMovie: async (movieId, score, comment = '') => {
  if (score < 1 || score > 10) {
    throw new Error('Rating must be between 1 and 10');
  }
  
  try {
      const response = await fetch(`${API_URL}/ratings/`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ 
          movie: movieId, 
          score: score,
          comment: comment 
        }),
      });
      
      if (response.ok) {
        return await response.json();
      }
      
      const error = await response.json();
      
      if (error.error && error.error.includes('already exists')) {
        const updateResponse = await fetch(`${API_URL}/ratings/`, {
          method: "PATCH",
          headers: getAuthHeaders(),
          body: JSON.stringify({ 
            movie: movieId, 
            score: score,
            comment: comment 
          }),
        });
        
        if (!updateResponse.ok) {
          const updateError = await updateResponse.json();
          throw new Error(updateError.error || 'Failed to update rating');
        }
        
        return await updateResponse.json();
      }
      throw new Error(error.error || error.message || 'Failed to rate movie');
    } catch (error) {
    console.error('Error in rateOrUpdateMovie:', error);
    throw error;
    }
  },

  getRecommendations: async () => {
    const response = await fetch(`${API_URL}/recommended_movies/`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  },

  getWatchList: async () => {
    const response = await fetch(`${API_URL}/movies/watch_list/`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to fetch watch list');
    }
    return response.json();
  },

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

  getWatchedMovies: async () => {
    const response = await fetch(`${API_URL}/movies/watched/`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to fetch watched movies');
    }
    return response.json();
  },

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