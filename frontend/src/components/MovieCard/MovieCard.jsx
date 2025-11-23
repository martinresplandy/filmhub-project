import './MovieCard.css';

export default function MovieCard({ movie, onSelect }) {
  const userRating = movie.user_rating || 0;

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
          </div>
        </div>
      </div>
    </div>
  );
}