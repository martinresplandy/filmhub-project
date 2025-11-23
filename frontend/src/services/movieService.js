const API_URL = 'http://localhost:8000/api';

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    'Authorization': `Token ${token}`
  };
};

export const movieService = {
  getMovies: async () => {
    const response = await fetch(`${API_URL}/movies/`, {
      headers: getAuthHeaders()
    });
    return response.json();
  },

  getMovie: async (id) => {
    const response = await fetch(`${API_URL}/movies/${id}/`, {
      headers: getAuthHeaders()
    });
    return response.json();
  },

  searchMovies: async (query) => {
    const response = await fetch(`${API_URL}/movies/?search=${encodeURIComponent(query)}`, {
      headers: getAuthHeaders()
    });
    return response.json();
  },

  getMoviesByGenre: async (genre) => {
    const response = await fetch(`${API_URL}/movies/?genre=${encodeURIComponent(genre)}`, {
      headers: getAuthHeaders()
    });
    return response.json();
  },

  rateMovie: async (movieId, rating) => {
    const response = await fetch(`${API_URL}/ratings/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ movie: movieId, rating })
    });
    return response.json();
  },

  getRecommendations: async () => {
    const response = await fetch(`${API_URL}/recommendations/`, {
      headers: getAuthHeaders()
    });
    return response.json();
  },

  getPopularMovies: async () => {
    const response = await fetch(`${API_URL}/movies/popular/`, {
      headers: getAuthHeaders()
    });
    return response.json();
  }
};