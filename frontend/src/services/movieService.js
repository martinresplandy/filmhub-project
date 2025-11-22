const API_URL = 'http://localhost:8000/api';

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    'Authorization': `Token ${token}`
  };
};

export const movieService = {
  // Buscar todos os filmes
  getMovies: async () => {
    const response = await fetch(`${API_URL}/movies/`, {
      headers: getAuthHeaders()
    });
    return response.json();
  },

  // Buscar filme por ID
  getMovie: async (id) => {
    const response = await fetch(`${API_URL}/movies/${id}/`, {
      headers: getAuthHeaders()
    });
    return response.json();
  },

  // Pesquisar filmes
  searchMovies: async (query) => {
    const response = await fetch(`${API_URL}/movies/?search=${encodeURIComponent(query)}`, {
      headers: getAuthHeaders()
    });
    return response.json();
  },

  // Buscar filmes por género
  getMoviesByGenre: async (genre) => {
    const response = await fetch(`${API_URL}/movies/?genre=${encodeURIComponent(genre)}`, {
      headers: getAuthHeaders()
    });
    return response.json();
  },

  // Avaliar filme
  rateMovie: async (movieId, rating) => {
    const response = await fetch(`${API_URL}/ratings/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ movie: movieId, rating })
    });
    return response.json();
  },

  // Buscar recomendações
  getRecommendations: async () => {
    const response = await fetch(`${API_URL}/recommendations/`, {
      headers: getAuthHeaders()
    });
    return response.json();
  },

  // Buscar filmes populares
  getPopularMovies: async () => {
    const response = await fetch(`${API_URL}/movies/popular/`, {
      headers: getAuthHeaders()
    });
    return response.json();
  }
};