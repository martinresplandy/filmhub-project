import { useState, useEffect, useCallback } from "react";
import useAuth from "../../hooks/useAuth";
import SearchBar from "../../components/SearchBar/SearchBar";
import MovieList from "../../components/MovieList/MovieList";
import { movieService } from "../../services/movieService";
import "./MainPage.css";

export default function MainPage() {
  const { auth } = useAuth();

  const [currentView, setCurrentView] = useState("home");
  const [catalog, setCatalog] = useState({
    popular: [],
    top_rated: [],
    action: [],
    comedy: [],
    drama: []
  });
  const [searchResults, setSearchResults] = useState([]);
  const [moviesLoading, setMoviesLoading] = useState(true);
  const [ratings, setRatings] = useState([]);
  const [moviesError, setMoviesError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  const loadRatings = useCallback(async () => {
    try {
      const ratingsData = await movieService.getRatings();
      setRatings(Array.isArray(ratingsData) ? ratingsData : []);
    } catch (err) {
      console.error("Error loading ratings:", err);
      setRatings([]);
    }
  }, []);

  const loadMovies = useCallback(async () => {
    setMoviesLoading(true);
    setMoviesError("");
    try {
      const moviesData = await movieService.getMovies();
      if (moviesData && typeof moviesData === 'object') {
        setCatalog({
          popular: Array.isArray(moviesData.popular) ? moviesData.popular : [],
          top_rated: Array.isArray(moviesData.top_rated) ? moviesData.top_rated : [],
          action: Array.isArray(moviesData.action) ? moviesData.action : [],
          comedy: Array.isArray(moviesData.comedy) ? moviesData.comedy : [],
          drama: Array.isArray(moviesData.drama) ? moviesData.drama : []
        });
      }
    } catch (err) {
      console.error("Error loading movies:", err);
      setMoviesError("Error loading movies. Please try again.");
    } finally {
      setMoviesLoading(false);
    }
  }, []);

  const loadInitialData = useCallback(async () => {
    await Promise.all([loadMovies(), loadRatings()]);
  }, [loadMovies, loadRatings]);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  const handleSearch = async (query) => {
    setSearchQuery(query);
    if (!query || query.trim() === "") {
      setSearchResults([]);
      setCurrentView("home");
      return;
    }

    setMoviesLoading(true);
    setMoviesError("");
    setCurrentView("search");

    try {
      const results = await movieService.searchMovies(query, 'title');
      setSearchResults(Array.isArray(results) ? results : []);
    } catch (err) {
      console.error("Error searching movies:", err);
      setMoviesError("Error searching movies. Please try again.");
      setSearchResults([]);
    } finally {
      setMoviesLoading(false);
    }
  };

  const handleRate = async (movieId, rating, comment = '') => {
    try {
      await movieService.rateOrUpdateMovie(movieId, rating, comment);
      await Promise.all([loadMovies(), loadRatings()]);
    } catch (err) {
      console.error("Error rating movie:", err);
      alert(err.message || "Error rating movie. Please try again.");
    }
  };

  const getAllMovies = () => {
    return [
      ...catalog.popular,
      ...catalog.top_rated,
      ...catalog.action,
      ...catalog.comedy,
      ...catalog.drama
    ];
  };

  return (
    <div className="main-page">
      <div className="main-content">
        <header className="main-header">
          <h1 className="main-welcome">
            Welcome back, {auth.user?.username || "User"}!
          </h1>
          <p className="main-subtitle">
            Discover your next favorite movie — rate, explore!
          </p>
          <SearchBar onSearch={handleSearch} />
        </header>

        <main className="main-movies">
          {currentView === "search" ? (
            // Search Results View
            <>
              {moviesLoading ? (
                <p>Loading search results...</p>
              ) : searchResults.length > 0 ? (
                <MovieList
                  title={`Search Results for "${searchQuery}"`}
                  movies={searchResults}
                  loading={false}
                  onRate={handleRate}
                  ratings={ratings}
                />
              ) : (
                <div style={{ textAlign: "center", padding: "40px 20px" }}>
                  <h2>No results found for "{searchQuery}"</h2>
                  <p>Try a different search term</p>
                </div>
              )}
            </>
          ) : (
            // Home View - Catalog
            <>
              {moviesError && (
                <div
                  style={{
                    color: "red",
                    textAlign: "center",
                    padding: "20px",
                    backgroundColor: "#fee",
                    borderRadius: "8px",
                    margin: "0 0 20px 0"
                  }}
                >
                  {moviesError}
                </div>
              )}
              
              {/* Popular Movies */}
              {catalog.popular.length > 0 && (
                <MovieList
                  title="Popular Movies"
                  movies={catalog.popular}
                  loading={moviesLoading}
                  onRate={handleRate}
                  ratings={ratings}
                />
              )}

              {/* Top Rated Movies */}
              {catalog.top_rated.length > 0 && (
                <MovieList
                  title="Top Rated"
                  movies={catalog.top_rated}
                  loading={moviesLoading}
                  onRate={handleRate}
                  ratings={ratings}
                />
              )}

              {/* Action Movies */}
              {catalog.action.length > 0 && (
                <MovieList
                  title="Action Movies"
                  movies={catalog.action}
                  loading={moviesLoading}
                  onRate={handleRate}
                  ratings={ratings}
                />
              )}

              {/* Comedy Movies */}
              {catalog.comedy.length > 0 && (
                <MovieList
                  title="Comedy Movies"
                  movies={catalog.comedy}
                  loading={moviesLoading}
                  onRate={handleRate}
                  ratings={ratings}
                />
              )}

              {/* Drama Movies */}
              {catalog.drama.length > 0 && (
                <MovieList
                  title="Drama Movies"
                  movies={catalog.drama}
                  loading={moviesLoading}
                  onRate={handleRate}
                  ratings={ratings}
                />
              )}

              {/* All Movies (combined) */}
              {!moviesLoading && getAllMovies().length > 0 && (
                <MovieList
                  title="All Movies"
                  movies={getAllMovies()}
                  loading={false}
                  onRate={handleRate}
                  ratings={ratings}
                />
              )}

              {/* Loading State */}
              {moviesLoading && (
                <div style={{ textAlign: "center", padding: "40px" }}>
                  <p>Loading movies...</p>
                </div>
              )}

              {/* Empty State */}
              {!moviesLoading && getAllMovies().length === 0 && !moviesError && (
                <div style={{ textAlign: "center", padding: "40px" }}>
                  <h2>No movies available</h2>
                  <p>Check your connection and try again</p>
                </div>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}