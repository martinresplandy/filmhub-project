import { useState } from 'react';
import './MovieCard.css';

export default function MovieCard({ movie, onRate, onSelect }) {
  const [userRating, setUserRating] = useState(movie.user_rating || 0);
  const [showRatingPopup, setShowRatingPopup] = useState(false);
  const [selectedRating, setSelectedRating] = useState(0);

  const handleOpenPopup = () => {
    setSelectedRating(userRating);
    setShowRatingPopup(true);
  };

  const handleClosePopup = () => {
    setShowRatingPopup(false);
    setSelectedRating(0);
  };

  const handleSubmitRating = () => {
    if (selectedRating > 0) {
      setUserRating(selectedRating);
      if (onRate) {
        onRate(movie.id, selectedRating);
      }
      handleClosePopup();
    }
  };

  const renderStars = (rating) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      const filled = i <= Math.round(rating);
      stars.push(
        <span
          key={i}
          className={`star ${filled ? 'star-filled' : 'star-empty'}`}
        >
          ★
        </span>
      );
    }
    return stars;
  };

  return (
    <div className="movie-card">
      <div 
        className="movie-card-poster"
        onClick={() => onSelect && onSelect(movie)}
      >
        {movie.poster_url ? (
          <img src={movie.poster_url} alt={movie.title} />
        ) : (
          <div className="movie-card-placeholder">
          </div>
        )}
        <div className="movie-card-overlay">
          <span>View Details</span>
        </div>
      </div>
      
      <div className="movie-card-info">
        <h3 className="movie-card-title">{movie.title}</h3>
        
        <div className="movie-card-meta">
          <span className="movie-card-year">{movie.year}</span>
          <span className="movie-card-genre">{movie.genre}</span>
        </div>
        
        <div className="movie-card-rating">
          <div className="movie-card-avg-rating">
            {renderStars(movie.average_rating)}
            <span className="rating-value">
              {movie.average_rating?.toFixed(1) || 'N/A'}
            </span>
          </div>
        </div>
        
        <div className="movie-card-user-rating">
          <div className="your-rating-container">
            <div className="your-rating-display">
              <span className="your-rating-label">Your rating:</span>
              <div className="your-rating-stars">
                {renderStars(userRating)}
              </div>
            </div>
            <button className="rate-button" onClick={handleOpenPopup}>
              Rate
            </button>
          </div>

          {}
          {showRatingPopup && (
            <div className="rating-popup">
              <h4 className="rating-popup-title">Rate this movie</h4>
              
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
              
              <div className="rating-popup-actions">
                <button 
                  className="popup-button popup-button-cancel"
                  onClick={handleClosePopup}
                >
                  Cancel
                </button>
                <button 
                  className="popup-button popup-button-submit"
                  onClick={handleSubmitRating}
                  disabled={selectedRating === 0}
                >
                  Submit
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}