import { useState, useEffect, useCallback } from 'react';
import { movieService } from '../../services/movieService';
import Navbar from '../Navbar/Navbar';
import './MovieDetails.css';

export default function MovieDetails({ movieId, user, onLogout, onBack }) {
  const [movie, setMovie] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [selectedRating, setSelectedRating] = useState(0);
  const [userRating, setUserRating] = useState(0);

  const loadMovieDetails = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const movieData = await movieService.getMovie(movieId);
      setMovie(movieData);
      setUserRating(movieData.user_rating || 0);
    } catch (err) {
      console.error('Error loading movie details:', err);
      setError('Error loading movie details. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [movieId]);

  useEffect(() => {
    loadMovieDetails();
  }, [loadMovieDetails]);

  const handleOpenRatingModal = () => {
    setSelectedRating(userRating);
    setShowRatingModal(true);
  };

  const handleCloseRatingModal = () => {
    setShowRatingModal(false);
    setSelectedRating(0);
  };

  const handleSubmitRating = async () => {
    if (selectedRating > 0) {
      try {
        await movieService.rateMovie(movieId, selectedRating);
        setUserRating(selectedRating);
        handleCloseRatingModal();
        loadMovieDetails();
      } catch (err) {
        console.error('Error submitting rating:', err);
      }
    }
  };

  const renderStars = (rating, size = 20) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      const filled = i <= Math.round(rating);
      stars.push(
        <span
          key={i}
          className={`star ${filled ? 'star-filled' : 'star-empty'}`}
          style={{ fontSize: `${size}px` }}
        >
          ★
        </span>
      );
    }
    return stars;
  };

  if (loading) {
    return (
      <div className="movie-details">
        <Navbar user={user} onLogout={onLogout} onNavigate={onBack} />
        <div className="movie-details-container">
          <div className="movie-details-loading">
            <div className="loading-spinner"></div>
            <p>Loading movie details...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !movie) {
    return (
      <div className="movie-details">
        <Navbar user={user} onLogout={onLogout} onNavigate={onBack} />
        <div className="movie-details-container">
          <button className="movie-details-back" onClick={onBack}>
            ← Back to Movies
          </button>
          <div className="movie-details-error">
            <p>{error || 'Movie not found'}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="movie-details">
      <Navbar user={user} onLogout={onLogout} onNavigate={onBack} />
      
      <div className="movie-details-container">
        <button className="movie-details-back" onClick={onBack}>
          ← Back to Movies
        </button>

        <div className="movie-details-content">
          <div className="movie-details-hero">
            <div className="movie-details-poster">
              {movie.poster_url ? (
                <img src={movie.poster_url} alt={movie.title} />
              ) : (
                <div className="movie-details-poster-placeholder">
                </div>
              )}
            </div>

            <div className="movie-details-info">
              <h1 className="movie-details-title">{movie.title}</h1>

              <div className="movie-details-meta">
                <div className="meta-item">
                  <span className="meta-icon"></span>
                  <span>{movie.year}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-genre">{movie.genre}</span>
                </div>
                {movie.duration && (
                  <div className="meta-item">
                    <span className="meta-icon"></span>
                    <span>{movie.duration} min</span>
                  </div>
                )}
              </div>

              <div className="movie-details-rating-section">
                <div className="rating-block">
                  <span className="rating-label">Average Rating</span>
                  <div className="rating-display">
                    <div className="rating-stars">
                      {renderStars(movie.average_rating)}
                    </div>
                    <span className="rating-number">
                      {movie.average_rating?.toFixed(1) || 'N/A'}
                    </span>
                    {movie.rating_count > 0 && (
                      <span className="rating-count">
                        ({movie.rating_count} {movie.rating_count === 1 ? 'rating' : 'ratings'})
                      </span>
                    )}
                  </div>
                </div>

                <div className="rating-block">
                  <span className="rating-label">Your Rating</span>
                  <div className="rating-display">
                    <div className="rating-stars">
                      {renderStars(userRating)}
                    </div>
                    {userRating > 0 && (
                      <span className="rating-number">{userRating}</span>
                    )}
                    <button 
                      className="rate-movie-button" 
                      onClick={handleOpenRatingModal}
                    >
                      {userRating > 0 ? 'Update Rating' : 'Rate This Movie'}
                    </button>
                  </div>
                </div>
              </div>

              {movie.description && (
                <p className="movie-details-description">{movie.description}</p>
              )}
            </div>
          </div>

          {(movie.director || movie.cast || movie.language) && (
            <div className="movie-details-extra">
              <div className="extra-info-grid">
                {movie.director && (
                  <div className="extra-info-item">
                    <span className="extra-info-label">Director</span>
                    <span className="extra-info-value">{movie.director}</span>
                  </div>
                )}
                {movie.cast && (
                  <div className="extra-info-item">
                    <span className="extra-info-label">Cast</span>
                    <span className="extra-info-value">{movie.cast}</span>
                  </div>
                )}
                {movie.language && (
                  <div className="extra-info-item">
                    <span className="extra-info-label">Language</span>
                    <span className="extra-info-value">{movie.language}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {showRatingModal && (
        <div className="rating-modal" onClick={handleCloseRatingModal}>
          <div 
            className="rating-modal-content" 
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="rating-modal-title">Rate {movie.title}</h2>
            <p className="rating-modal-subtitle">
              Select a rating from 1 to 5 stars
            </p>

            <div className="rating-options">
              {[1, 2, 3, 4, 5].map((rating) => (
                <button
                  key={rating}
                  className={`rating-option ${selectedRating === rating ? 'selected' : ''}`}
                  onClick={() => setSelectedRating(rating)}
                >
                  {rating}
                </button>
              ))}
            </div>

            <div className="rating-modal-actions">
              <button
                className="modal-button modal-button-cancel"
                onClick={handleCloseRatingModal}
              >
                Cancel
              </button>
              <button
                className="modal-button modal-button-submit"
                onClick={handleSubmitRating}
                disabled={selectedRating === 0}
              >
                Submit Rating
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}