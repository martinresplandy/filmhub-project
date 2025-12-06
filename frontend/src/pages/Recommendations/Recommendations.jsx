import { useState, useEffect, useCallback } from "react";
import { movieService } from "../../services/movieService";
import MovieList from "../../components/MovieList/MovieList";

export default function Recommendations() {
  const [recommendations, setRecommendations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadRecommendations = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await movieService.getRecommendations();
      setRecommendations(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Error loading recommendations:", err);
      setError("Failed to load recommendations. Please try again later.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadRecommendations();
  }, [loadRecommendations]);

  const handleRate = useCallback((movieId, rating) => {
    console.log(`Rated movie ${movieId} with ${rating} stars`);
  }, []);

  if (!isLoading && recommendations.length === 0 && !error) {
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
      loading={isLoading}
      error={error}
      onRate={handleRate}
      emptyMessage="Rate some movies to get recommendations!"
    />
  );
}