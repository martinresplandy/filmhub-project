import { useState, useEffect } from 'react';
import Navbar from '../Navbar/Navbar';
import SearchBar from '../SearchBar/SearchBar';
import MovieList from '../MovieList/MovieList';
import MovieDetails from '../MovieDetails/MovieDetails';
import { movieService } from '../../services/movieService';
import './MainPage.css';

export default function MainPage({ user, onLogout }) {
  const [currentView, setCurrentView] = useState('home');
  const [selectedMovieId, setSelectedMovieId] = useState(null);
  const [movies, setMovies] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  
  const [moviesLoading, setMoviesLoading] = useState(true);
  const [recommendationsLoading, setRecommendationsLoading] = useState(true);
  
  const [moviesError, setMoviesError] = useState('');
  const [recommendationsError, setRecommendationsError] = useState('');
  
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    loadMovies();
    loadRecommendations();
  };

  const loadMovies = async () => {
    setMoviesLoading(true);
    setMoviesError('');
    try {
      console.log('Loading all movies...');
      const moviesData = await movieService.getMovies();
      console.log('Movies loaded:', moviesData);
      setMovies(Array.isArray(moviesData) ? moviesData : []);
    } catch (err) {
      console.error('Error loading movies:', err);
      setMoviesError('Error loading movies. Please try again.');
    } finally {
      setMoviesLoading(false);
    }
  };

  const loadRecommendations = async () => {
    setRecommendationsLoading(true);
    setRecommendationsError('');
    try {
      console.log('Loading recommendations...');
      const recommendationsData = await movieService.getRecommendations();
      console.log('Recommendations loaded:', recommendationsData);
      setRecommendations(Array.isArray(recommendationsData) ? recommendationsData : []);
    } catch (err) {
      console.error('Error loading recommendations:', err);
      setRecommendationsError('Error loading recommendations.');
    } finally {
      setRecommendationsLoading(false);
    }
  };

  const handleSearch = async (query) => {
    setSearchQuery(query);
    if (!query) {
      setSearchResults([]);
      setCurrentView('home');
      return;
    }
    
    setMoviesLoading(true);
    setMoviesError('');
    try {
      const results = await movieService.searchMovies(query);
      setSearchResults(Array.isArray(results) ? results : []);
      setCurrentView('search');
    } catch (err) {
      setMoviesError('Error searching movies.');
    } finally {
      setMoviesLoading(false);
    }
  };

  const handleRate = async (movieId, rating) => {
    try {
      await movieService.rateMovie(movieId, rating);
      loadMovies();
      loadRecommendations();
    } catch (err) {
      console.error('Error rating movie:', err);
    }
  };

  const handleSelectMovie = (movie) => {
    setSelectedMovieId(movie.id);
    setCurrentView('movie-details');
  };

  const handleBackToMovies = () => {
    setSelectedMovieId(null);
    setCurrentView('home');
  };

  const handleNavigate = (view) => {
    setCurrentView(view);
    setSearchQuery('');
    setSearchResults([]);
  };

  const renderContent = () => {
    if (currentView === 'movie-details' && selectedMovieId) {
      return (
        <MovieDetails
          movieId={selectedMovieId}
          user={user}
          onLogout={onLogout}
          onBack={handleBackToMovies}
        />
      );
    }

    if (currentView === 'search' && searchQuery) {
      return (
        <MovieList
          title={`Search results for "${searchQuery}"`}
          movies={searchResults}
          loading={moviesLoading}
          error={moviesError}
          onRate={handleRate}
          onSelectMovie={handleSelectMovie}
          emptyMessage="No movies found for your search"
        />
      );
    }

    if (currentView === 'recommendations') {
      if (recommendationsError && recommendations.length === 0) {
        return (
          <div className="movie-list-section">
            <h2 className="movie-list-title">Recommended for You</h2>
            <div className="movie-list-empty">
              <span className="empty-icon"></span>
              <p>Rate some movies to get personalized recommendations!</p>
            </div>
          </div>
        );
      }
      
      return (
        <MovieList
          title="Recommended for You"
          movies={recommendations}
          loading={recommendationsLoading}
          error=""
          onRate={handleRate}
          onSelectMovie={handleSelectMovie}
          emptyMessage="Rate some movies to get recommendations!"
        />
      );
    }

    return (
      <>
        {!recommendationsLoading && recommendations.length > 0 && (
          <MovieList
            title="Recommended for You"
            movies={recommendations.slice(0, 5)}
            loading={false}
            onRate={handleRate}
            onSelectMovie={handleSelectMovie}
          />
        )}
        
        <MovieList
          title="All Movies"
          movies={movies}
          loading={moviesLoading}
          error={moviesError}
          onRate={handleRate}
          onSelectMovie={handleSelectMovie}
        />
      </>
    );
  };

  return (
    <div className="main-page">
      {currentView === 'movie-details' ? (
        renderContent()
      ) : (
        <>
          <Navbar 
            user={user} 
            onLogout={onLogout} 
            onNavigate={handleNavigate}
          />
          
          <div className="main-content">
            <header className="main-header">
              <h1 className="main-welcome">
                Welcome back, {user?.username || 'User'}!
              </h1>
              <p className="main-subtitle">
                Discover your next favorite movie – rate, explore, and get smart recommendations!
              </p>
              {(currentView === 'home' || currentView === 'search') && (
                <SearchBar onSearch={handleSearch} />
              )}
            </header>
            
            <main className="main-movies">
              {renderContent()}
            </main>
          </div>
        </>
      )}
    </div>
  );
}