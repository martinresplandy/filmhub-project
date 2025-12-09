import { useState, useEffect, useCallback } from "react";
import { movieService } from "../../services/movieService";
import MovieList from "../../components/MovieList/MovieList";
import "./Recommendations.css";

export default function Recommendations() {
  const [recommendations, setRecommendations] = useState([]);
  const [ratings, setRatings] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const loadRecommendations = useCallback(async () => {
    try {
      const data = await movieService.getRecommendations();
      setRecommendations(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Error loading recommendations:", err);
      setError("Failed to load recommendations. Please try again later.");
    }
  }, []);

  const loadRatings = useCallback(async () => {
    try {
      const ratingsData = await movieService.getRatings();
      setRatings(Array.isArray(ratingsData) ? ratingsData : []);
    } catch (err) {
      console.error("Error loading ratings:", err);
      setRatings([]);
    }
  }, []);

  const loadInitialData = useCallback(async () => {
    setIsLoading(true);
    setError("");
    
    try {
      await Promise.all([loadRecommendations(), loadRatings()]);
    } catch (err) {
      console.error("Error loading initial data:", err);
      setError("Failed to load data. Please try again later.");
    } finally {
      setIsLoading(false);
    }
  }, [loadRecommendations, loadRatings]);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  const handleRate = async (movieId, rating) => {
    try {
      setError("");
      setSuccessMessage("");
      
      await movieService.rateOrUpdateMovie(movieId, rating);
      
      setSuccessMessage("Rating saved successfully!");
      
      await Promise.all([loadRecommendations(), loadRatings()]);
      
      setTimeout(() => setSuccessMessage(""), 3000);
    } catch (err) {
      console.error("Error rating movie:", err);
      setError(err.message || "Error saving rating. Please try again.");
    }
  };

  return (
    <div className="recommendations-page">
      <div className="recommendations-content">
        <header className="recommendations-header">
          <h1 className="recommendations-title">Recommended for You</h1>
          <p className="recommendations-subtitle">Personalized movie suggestions based on your ratings!</p>
        </header>
        
        <main className="recommendations-movies">
          {successMessage && (
            <div className="success-message" style={{
              backgroundColor: '#4caf50',
              color: 'white',
              padding: '12px 20px',
              borderRadius: '4px',
              marginBottom: '20px',
              textAlign: 'center'
            }}>
              {successMessage}
            </div>
          )}
          
          {error && (
            <div className="error-message" style={{
              backgroundColor: '#f44336',
              color: 'white',
              padding: '12px 20px',
              borderRadius: '4px',
              marginBottom: '20px',
              textAlign: 'center'
            }}>
              {error}
            </div>
          )}
          
          <MovieList
            title=""
            movies={recommendations}
            loading={isLoading}
            error={error}
            onRate={handleRate}
            emptyMessage="Rate some movies to get personalized recommendations!"
            ratings={ratings}
          />
        </main>
      </div>
    </div>
  );
}