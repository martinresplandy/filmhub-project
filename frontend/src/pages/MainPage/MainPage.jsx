// src/pages/MainPage/MainPage.jsx
import { useState, useEffect, useCallback } from "react";
// import { useNavigate } from "react-router-dom";
import useAuth from "../../hooks/useAuth";
import SearchBar from "../../components/SearchBar/SearchBar";
import MovieList from "../../components/MovieList/MovieList";
import { movieService } from "../../services/movieService";
import "./MainPage.css";

export default function MainPage() {
  const { auth } = useAuth();

  const [currentView, setCurrentView] = useState("home");
  const [movies, setMovies] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [moviesLoading, setMoviesLoading] = useState(true);
  const [recommendations, setRecommendations] = useState([]);
  const [recommendationsLoading, setRecommendationsLoading] = useState(true);
  const [moviesError, setMoviesError] = useState("");
  // const [searchQuery, setSearchQuery] = useState("");

  const loadMovies = useCallback(async () => {
    setMoviesLoading(true);
    setMoviesError("");
    try {
      const moviesData = await movieService.getMovies();
      setMovies(Array.isArray(moviesData) ? moviesData : []);
    } catch (err) {
      console.error("Error loading movies:", err);
      setMoviesError("Error loading movies. Please try again.");
    } finally {
      setMoviesLoading(false);
    }
  }, []);

  const loadRecommendations = useCallback(async () => {
    setRecommendationsLoading(true);
    try {
      const recommendationsData = await movieService.getRecommendations();
      setRecommendations(
        Array.isArray(recommendationsData) ? recommendationsData : []
      );
    } catch (err) {
      console.error("Error loading recommendations:", err);
    } finally {
      setRecommendationsLoading(false);
    }
  }, []);

  const loadInitialData = useCallback(async () => {
    loadMovies();
    loadRecommendations();
  }, [loadMovies, loadRecommendations]);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  const handleSearch = async (query) => {
    // setSearchQuery(query);
    if (!query) {
      setSearchResults([]);
      setCurrentView("home");
      return;
    }
    setMoviesLoading(true);
    setMoviesError("");
    try {
      const results = await movieService.searchMovies();
      setSearchResults(Array.isArray(results) ? results : []);
      setCurrentView("search");
    } catch (err) {
      setMoviesError("Error searching movies.");
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
      console.error("Error rating movie:", err);
    }
  };

  return (
    <div className="main-page">
      <>
        <div className="main-content">
          <header className="main-header">
            <h1 className="main-welcome">
              {/* USE AUTH.USER */}
              Welcome back, {auth.user?.username || "User"}!
            </h1>
            <p className="main-subtitle">
              Discover your next favorite movie – rate, explore, and get smart
              recommendations!
            </p>
            {(currentView === "home" || currentView === "search") && (
              <SearchBar onSearch={handleSearch} />
            )}
          </header>

          <main className="main-movies">
            <>
              {searchResults.length > 0 && (
                <MovieList
                  title="Recommended for You"
                  movies={searchResults.slice(0, 5)}
                  loading={false}
                  onRate={handleRate}
                />
              )}
              {!recommendationsLoading && recommendations.length > 0 && (
                <MovieList
                  title="Recommended for You"
                  movies={recommendations.slice(0, 5)}
                  loading={false}
                  onRate={handleRate}
                />
              )}

              <MovieList
                title="All Movies"
                movies={movies}
                loading={moviesLoading}
                error={moviesError}
                onRate={handleRate}
              />
            </>
          </main>
        </div>
      </>
    </div>
  );
}
